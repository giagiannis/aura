#!/usr/bin/python
from time import sleep
import logging
from novaclient import client
import paramiko
import scp
from tempfile import mkstemp, mktemp


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
        sleep(1.0)
        logging.info(vm.networks)
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
        # TODO: add implementation
        for s in self.__module['scripts']:
            self.__execute_script(s)

    def __execute_script(self, script):
        logging.info("Script execution for %s: %s" % \
                (self.__module['name'], script))
        if "input" in script:
            # have to wait until there
            pass
        self.__transfer_and_run(script['file-content'])
        if "output" in script:
            # have to wait until there
            pass

    def __setup_paramiko(self):
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

    def __transfer_and_run(self, content):
        # create temp file
        src_name = mktemp()
        with open(src_name, mode='w') as f:
            f.write(content)
        f.close()
        dst_name = mktemp()
        logging.info("Serialized script's content to %s" % src_name)
        self.__scp.put(src_name, dst_name)
        logging.info("%s: Transfered %s to %s@%s" % (self.__module['name'], src_name, self.__module['address'], dst_name))
        self.__ssh.exec_command("chmod +x %s" % dst_name)
        stdin, stdout, stderr = self.__ssh.exec_command("%s" % dst_name)
        stdout_str = stdout.read()
        stderr_str = stderr.read()
        logging.info("%s stdout: %s" % (dst_name, stdout_str))
        logging.info("%s stderr: %s" % (dst_name, stderr_str))
