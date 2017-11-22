#!/usr/bin/python
from copy import deepcopy
from time import sleep, time, ctime
from novaclient import client
from tempfile import mkstemp, mktemp
from shutil import rmtree
import paramiko
import scp
import os
import threading
import tarfile
import json
import logging



class ApplicationDeployment:
    def __init__(self, description, aura_configuration):
#        desc = ApplicationDescriptionParser(description_file)
#        self.__desc = desc.get_description()
        self.__desc = description
        self.__queue = Queue()
        self.__aura_conf = aura_configuration
        self.__desc['datetime'] = ctime()

    def run(self):
        self.allocate_resources()
        self.run_deployment()

    def allocate_resources(self):
        self.__desc['status']='ALLOCATING_RESOURCES'
        start = time()
        cloud_config = self.__desc['cloud-conf']
        self.__cloud = CloudOrchestrator(cloud_config)
        def create_vm_and_set_ip(m):
            address = self.__cloud.create_vm(m['name'],m['flavor_id'], m['image_id'], None)
            m['address'] = address

        threads = []
        for m in self.__desc['modules']:
            if "address" not in m:
                threads.append(threading.Thread(target = create_vm_and_set_ip, args = (m,)))
        if threads == []:
            return
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.__desc['allocating_resources_time'] = time()-start
        logging.info("Allocation complete: %s" % self.__desc)
    
    def run_deployment(self):
        self.__desc['status']='BOOTING'
        start = time()
        orchestrators = []
        for m in self.__desc['modules']:
            o = VMOrchestrator(self.__queue, m, self.__aura_conf['prv_key'])
            orchestrators.append(o)

        for o in orchestrators:
            o.wait_until_booted()
        self.__desc['booting_time'] = time()-start
        self.__desc['status']='RUNNING'
        start = time()

        # parallel orchestrator execution
        self.__parallel_start_orchestrators(orchestrators)
        
        # checking for shit
        while True:
            logging.info("Heartbeat status %s" % (self.__desc))
            finished_nodes = self.__queue.get_finished_nodes()
            logging.info(finished_nodes)
            if len(finished_nodes) == len(self.__desc['modules']):
                logging.info("Breaking the loop")
                break
#            if self.__queue.get_health_check_request():
#                self.__health_check_routine(orchestrators)
            sleep(1.0)
        self.__desc['running_time'] = time()-start
        self.__desc['status']='DONE'

    def status(self):
        return self.__desc

    def delete(self):
        self.__cloud.delete_vms()

    def __parallel_start_orchestrators(self, orchestrators):
        logging.info("starting orchestrators in parallel")
        threads = []
        for o in orchestrators:
            threads.append(threading.Thread(target = o.execute_scripts))
        for t in threads:
            t.start()
        return threads

class CloudOrchestrator:
    """
    CloudOrchestrator class is responsible to contact with Openstack and
    allocate the resources
    """
    def __init__(self, conf):
        self.__vms = []
        self.__lock = threading.Lock()
        self.__network_name = conf['network_name']
        self.__client = client.Client(\
                conf['version'],\
                conf['username'],\
                conf['password'],\
                conf['project_id'],\
                conf['auth_url'], 
                user_domain_name = conf['domain'],
                connection_pool = True,)
        logging.info("Openstack access established")

    def create_vm(self, name, flavor, image, key):
        """
        create_vm function generates a new VM and return its address
        """
        logging.info("%s: %s, %s, %s", "create_vm", flavor, image, key)
        vm = self.__client.servers.create(name=name, image=image, flavor=flavor)
        self.__lock.acquire()
        self.__vms.append(vm)
        self.__lock.release()
        while vm.networks == {}:
            sleep(1.0)
            vm.get()
        for add in vm.networks[self.__network_name]:
            if len(add.strip().split("."))==4:
                return add
        return None

    def delete_vms(self):
        for vm in self.__vms:
            vm.delete()


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
            args = ""
            for i in script['input']:
                args += self.__queue.block_receive(graph_node_id, i)
        start_time = time()
        script['runs'] = 0
        while True:
            script['runs']+=1
            logging.info("Executing %s" % script['file'])
            script['status'] = 'EXECUTING'
            o,e = self.__transfer_and_run(script['file-content'], args)
            script['stdout'], script['stderr'] = o, e
            if e!="":
                script['status'] = 'ERROR'
                sleep(5.0)
            else:
                break
        script['status']='FINISHED'
        script['elapsed_time'] = time()-start_time
        #logging.info("%s: stdout (%s) and stderr (%s)" % (graph_node_id, o, e))
        if "output" in script:
            script['status']='SENDING_OUTPUT'
            for x in script['output']:
                self.__queue.send(graph_node_id, x, o)
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
        sleep(.100) # we had incident where chmod had not committed its results
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



class ApplicationDescriptionParser:
    def __init__(self, file_path):
        workdir = file_path
        try:
            is_tar = tarfile.is_tarfile(file_path)
        except IOError:
            is_tar=False
        if is_tar:
            self.__tar = tarfile.open(file_path)
            workdir = mkdtemp()
            self.__tar.extractall(path=workdir)

        self.__content = json.load(open(workdir+"/description.json"))
        for m in self.__content['modules']:
            for s in m['scripts']:
                t = open(workdir+"/"+s['file'])
                s['file-content'] = t.read()
        if is_tar:
            rmtree(workdir)

    def set_multiplicities(self, multiplicities):
        for m in self.__content['modules']:
            if m['name'] in multiplicities:
                m['multiplicity'] = multiplicities[m['name']]


    def get_description(self):
        return self.__content

    def expand_description(self):
        new_one = dict()
        new_one['name'] = deepcopy(self.__content['name'])
        new_one['description'] = deepcopy(self.__content['description'])
        new_one['cloud-conf'] = deepcopy(self.__content['cloud-conf'])

        new_one['modules'] = []
        multiplicities= dict()
        for m in self.__content['modules']:
            # creating a dict
            multiplicities[m['name']] = 1
            if 'multiplicity' in m:
                multiplicities[m['name']] = m['multiplicity']

            # replicating for each VM
            if 'multiplicity' not in m or m['multiplicity'] == 1:
                new_one['modules'].append(deepcopy(m))
            else:   # do your shit
                for i in range(1, m['multiplicity']+1):
                    new_m = deepcopy(m)
                    new_m['name'] = "%s%d" %(new_m['name'], i)
                    new_one['modules'].append(new_m)

        for vm in new_one['modules']:
            for s in vm['scripts']:
                if 'input' in s:
                    new_input = []
                    for x in s['input']:
                        multi, seq = x.split("/")[0], x.split("/")[1]
                        if multiplicities[multi]>1:
                            for i in range(1, multiplicities[multi]+1):
                                new_input.append("%s%d/%s"  % (multi, i, seq))
                    if len(new_input)>0:
                        del(s['input'])
                        s['input'] = new_input

                if 'output' in s:
                    new_output = []
                    for x in s['output']:
                        multi, seq = x.split("/")[0], x.split("/")[1]
                        if multiplicities[multi]>1:
                            for i in range(1, multiplicities[multi]+1):
                                new_output.append("%s%d/%s"  % (multi, i, seq))
                    if len(new_output)>0:
                        del(s['output'])
                        s['output'] = new_output
        return new_one

class Queue:
    """
    Queue class implements a simple queing mechanism used by different VMOrchestrators
    to exchange messages
    """
    def __init__(self):
        self.__queue = dict()
        self.__health_check_flag = False
        self.__finished_list = []
        self.__lock = threading.Lock()

    def send(self, orig, dst, msg):
        logging.info("queue %s: added (%s, %s)"%(dst, orig, msg))
        self.__lock.acquire()
        if dst not in self.__queue:
            self.__queue[dst] = dict()
        self.__queue[dst][orig] = msg
        self.__lock.release()


    def receive(self, dst, orig):
        logging.info("queue %s: receive %s"%(dst, orig))
        res = None
        self.__lock.acquire()
        if dst in self.__queue and orig in self.__queue[dst]:
            logging.info("receive request succesful for %s, %s", dst, orig)
            res = self.__queue[dst][orig]
        else:
            logging.info("receive request failed for %s, %s", dst, orig)
        self.__lock.release()
        return res

    def block_receive(self, dst, orig, timeout=-1):
        r = self.receive(dst, orig)
        while r == None and timeout<>0:
            logging.info("blocking until %s, %s arrives", dst, orig)
            r = self.receive(dst, orig)
            if timeout >0:
                timeout-=1
            sleep(1.0)
        return r

    def set_health_check_request(self):
        self.__lock.acquire()
        logging.info("queue: setting health check")
        self.__health_check_flag = True
        self.__lock.release()

    def get_health_check_request(self):
        self.__lock.acquire()
        logging.info("queue: getting health check")
        old = self.__health_check_flag
        self.__lock.release()
        return old

    def get_and_reset_health_check_request(self):
        self.__lock.acquire()
        logging.info("queue: getting and reseting health check")
        old = self.__health_check_flag
        self.__health_check_flag = False
        self.__lock.release()
        return old

    def get_finished_nodes(self):
        logging.info("queue: getting finished nodes")
        return self.__finished_list

    def set_finished_node(self, node_id):
        logging.info("queue: appending to finished nodes (%s)", node_id)
        self.__lock.acquire()
        self.__finished_list.append(node_id)
        self.__lock.release()
    
    def __str__(self):
        return str(self.__queue)
