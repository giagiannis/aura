#!/usr/bin/python
from time import sleep
import logging
from novaclient import client


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
            sleep(5)
            vm.get()
        for add in vm.networks[self.__network_name]:
            if len(add.strip().split("."))==4:
                return add
        return None


class VMOrchestrator:
    def __init__(self, address, queue, scripts, name):
        self.__scripts = scripts
        self.__name  = name
        self.__address = address
        self.__queue = queue

    def wait_until_booted(self):
        # TODO: add implementation
        pass

    def execute_scripts(self):
        # TODO: add implementation
        for s in self.__scripts:
            self.__execute_script(s)

    def __execute_script(self, script):
        # TODO: add implementation
        # ssh to VM and execute script
        if "input" in script:
            # have to wait until there
            print "%s: waiting for %s" % (self.__name, script['input'])
        print script
        if "output" in script:
            # have to wait until there
            print "%s: writing to %s" % (self.__name, script['output'])
