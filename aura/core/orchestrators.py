#!/usr/bin/python
from time import sleep


class CloudOrchestrator:
    """
    CloudOrchestrator class is responsible to contact with Openstack and
    allocate the resources
    """
    def __init__(self, conf):
        self.__conf = conf

    def create_vm(self, flavor, image, key):
        """
        create_vm function generates a new VM and return its address
        """
        # TODO: add implementation
        print "given args %s, %s, %s" % (flavor, image, key)


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
