#!/usr/bin/python
import logging
from time import sleep
from parsers import ApplicationDescriptionParser
from orchestrators import CloudOrchestrator, VMOrchestrator
from queue import Queue
from threading import Thread
from time import sleep

class ApplicationDeployment:
    def __init__(self, description_file, aura_configuration):
        desc = ApplicationDescriptionParser(description_file)
        self.__desc = desc.get_description()
        self.__queue = Queue()
        self.__aura_conf = aura_configuration

    def allocate_resources(self):
        cloud_config = self.__desc['cloud-conf']
        cloud = CloudOrchestrator(cloud_config)
        def create_vm_and_set_ip(m):
            address = cloud.create_vm(m['name'],m['flavor_id'], m['image_id'], None)
            m['address'] = address

        threads = []
        for m in self.__desc['modules']:
            if "address" not in m:
                threads.append(Thread(target = create_vm_and_set_ip, args = (m,)))
        if threads == []:
            return
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        logging.info("Allocation complete: %s" % self.__desc)
    
    def run_deployment(self):
        orchestrators = []
        for m in self.__desc['modules']:
            o = VMOrchestrator(self.__queue, m, self.__aura_conf['prv_key'])
            orchestrators.append(o)

        for o in orchestrators:
            o.wait_until_booted()

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

    def status(self):
        return self.__desc


    def __parallel_start_orchestrators(self, orchestrators):
        logging.info("starting orchestrators in parallel")
        threads = []
        for o in orchestrators:
            threads.append(Thread(target = o.execute_scripts))
        for t in threads:
            t.start()
        return threads
