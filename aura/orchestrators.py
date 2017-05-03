#!/usr/bin/python
from time import sleep
import logging
from novaclient import client
import paramiko
import scp
from tempfile import mkstemp, mktemp
import os


class CloudOrchestrator:
    """
    CloudOrchestrator class is responsible to contact with Openstack and
    allocate the resources
    """
    def __init__(self, conf):
        self.__network_name = conf['network_name']
        self.__client = client.Client(\
                conf['version'],\
                conf['username'],\
                conf['password'],\
                conf['project_id'],\
                conf['auth_url'], connection_pool = True)
        logging.info("Openstack access established")

    def create_vm(self, name, flavor, image, key):
        """
        create_vm function generates a new VM and return its address
        """
        logging.info("%s: %s, %s, %s", "create_vm", flavor, image, key)
        vm = self.__client.servers.create(name=name, image=image, flavor=flavor)
        while vm.networks == {}:
            sleep(1.0)
            vm.get()
        for add in vm.networks[self.__network_name]:
            if len(add.strip().split("."))==4:
                return add
        return None


class VMOrchestrator:
    def __init__(self, queue, module, key_file):
        self.__queue = queue
        self.__module = module
        self.__prv_key = key_file
        self.name = module['name']
        for s in self.__module['scripts']:
            s['status'] = 'PENDING'

        
    def wait_until_booted(self):
        """
        wait_until_booted waits until the VM becomes visible and SSH-able
        """
        while True:
            logging.info("Waiting until %s has boot" % self.__module['name'])
            if self.__setup_paramiko():
                stdin, stdout, stderr = self.__ssh.exec_command("hostname")
                if stderr.read() == '' and \
                        stdout.read().strip()==self.__module['name']:
                            logging.info("%s has booted" % self.__module['name'])
                            return
            sleep(1.0)

    def execute_scripts(self):
        for s in self.__module['scripts']:
            self.__execute_script(s)
        flag = reduce(lambda x,y : x&y, [s['status'] == 'DONE' for s in self.__module['scripts']])
        if flag:
            self.__queue.set_finished_node(self.__module['name'])
            

    def __execute_script(self, script):
        graph_node_id = "%s/%s" % (self.__module['name'], script['seq'])
        logging.info("%s: starting script execution" % (graph_node_id))
        args = None
        if "input" in script:
            script['status'] = 'WAITING_FOR_MESSAGE'
            args = self.__queue.block_receive(graph_node_id, script['input'])
        while True:
            logging.info("Executing %s" % script['file'])
            script['status'] = 'EXECUTING'
            o,e = self.__transfer_and_run(script['file-content'], args)
            if e!="":
                script['status'] = 'ERROR'
                sleep(5.0)
            else:
                break
        script['status']='FINISHED'
        logging.info("%s: stdout (%s) and stderr (%s)" % (graph_node_id, o, e))
        if "output" in script:
            script['status']='SENDING_OUTPUT'
            self.__queue.send(graph_node_id, script['output'], o)
        script['status']='DONE'
        if e != "": # an error occured
            return False
        else:
            return True

    def __setup_paramiko(self):
        # FIXME: I need to set paramiko timeout option to enable long script execution
        try:
            k = paramiko.RSAKey.from_private_key_file(self.__prv_key)
            self.__ssh = paramiko.SSHClient()
            self.__ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.__ssh.connect(\
                self.__module['address'], \
                username="root", \
                pkey = k)
            self.__scp = scp.SCPClient(self.__ssh.get_transport())
            logging.info("Paramiko connection established")
            return True
        except IOError as e:
            logging.info("Paramiko connection failed")
            return False

    def __transfer_and_run(self, content, args=""):
        """
        Serializes the content parameter into a script, transfers it to the dst host and executes it.
        It returns the stdout and stderr objects. args (if given) are the content of the file given as an 
        argument to the script.
        """
        # create temp file
        script_file = self.__transfer_content(content)
        args_file = self.__transfer_content(args)
        self.__ssh.exec_command("chmod +x %s" % script_file)
        stdin, stdout, stderr = self.__ssh.exec_command("%s %s" % (script_file, args_file))
        stdout_str = stdout.read()
        stderr_str = stderr.read()
        return stdout_str, stderr_str

    def __transfer_content(self, content):
        """
        Transfers the content to a randomly generated remote file and returns the dst file name.
        """
        logging.info("Trying to serialize content: %s", content)
        if content == None:
            return ""
        src_name = mktemp()
        with open(src_name, mode='w') as f:
            f.write(content)
        f.close()
        dst_name = mktemp()
        logging.info("Serialized content to %s" % src_name)
        self.__scp.put(src_name, dst_name)
        logging.info("%s: Transfered %s to %s@%s" % (self.__module['name'], src_name, self.__module['address'], dst_name))
        os.remove(src_name)
        return dst_name
