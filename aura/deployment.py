#!/usr/bin/python
import logging
from parsers import ApplicationDescriptionParser
from orchestrators import CloudOrchestrator, VMOrchestrator
from queue import Queue
from threading import Thread
import json

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
        logging.info("Allocation complete: %s" % json.dumps(self.__desc, indent=1))
    
    def run_deployment(self):
        orchestrators = []
        for m in self.__desc['modules']:
            o = VMOrchestrator(self.__queue, m, self.__aura_conf['prv_key'])
            orchestrators.append(o)

        for o in orchestrators:
            o.wait_until_booted()

        # parallel orchestrator execution
        threads = []
        for o in orchestrators:
            threads.append(Thread(target = o.execute_scripts))

        for t in threads:
            t.start()

        for t in threads:
            t.join()


