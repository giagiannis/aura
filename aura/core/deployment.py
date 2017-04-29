#!/usr/bin/python

from parsers import ApplicationDescriptionParser
from orchestrators import CloudOrchestrator, VMOrchestrator
from queue import Queue
from threading import Thread

class ApplicationDeployment:
    def __init__(self, description_file):
        desc = ApplicationDescriptionParser(description_file)
        self.__desc = desc.get_description()
        self.__queue = Queue()

    def allocate_resources(self, cloud_config):
        cloud = CloudOrchestrator(cloud_config)
        for m in self.__desc['modules']:
            address = cloud.create_vm(m['flavor_id'], m['image_id'], None)
            m['address'] = address

    def run_deployment(self):
        orchestrators = []
        for m in self.__desc['modules']:
            o = VMOrchestrator(m['address'], self.__queue, m['scripts'], m['name'])
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

if __name__ == "__main__":
    a = ApplicationDeployment("example/demo.tar")
    a.allocate_resources(None)
    a.run_deployment()
