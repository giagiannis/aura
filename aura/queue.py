#!/usr/bin/python
import logging
from time import sleep

class Queue:
    """
    Queue class implements a simple queing mechanism used by different VMOrchestrators
    to exchange messages
    """
    def __init__(self):
        self.__queue = dict()

    def send(self, orig, dst, msg):
        if dst not in self.__queue:
            self.__queue[dst] = dict()
        self.__queue[dst][orig] = msg
        logging.info("queue %s: added (%s, %s)"%(dst, orig, msg))


    def receive(self, dst, orig):
        if dst in self.__queue and orig in self.__queue[dst]:
            logging.info("receive request succesful for %s, %s", dst, orig)
            return self.__queue[dst][orig]
        logging.info("receive request failed for %s, %s", dst, orig)
        return None

    def block_receive(self, dst, orig):
        r = self.receive(dst, orig)
        while r == None:
            logging.info("blocking until %s, %s arrives", dst, orig)
            r = self.receive(dst, orig)
            sleep(1.0)
        return r

    def __str__(self):
        return str(self.__queue)
