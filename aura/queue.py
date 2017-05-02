#!/usr/bin/python
import logging
from time import sleep
from threading import Lock

class Queue:
    """
    Queue class implements a simple queing mechanism used by different VMOrchestrators
    to exchange messages
    """
    def __init__(self):
        self.__queue = dict()
        self.__health_check_flag = False
        self.__finished_list = []
        self.__lock = Lock()

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
