#!/usr/bin/python

class Queue:
    """
    Queue class implements a simple queing mechanism used by different VMOrchestrators
    to exchange messages
    """
    def __init__(self):
        self.__queue = dict()

    def send(self, orig, dst, msg):
        if orig not in self.__queue:
            self.__queue[dst] = []
        self.__queue[dst].append((orig, msg))

    def receive(self, dst):
        msgs = self.__queue[dst]
        self.__queue[dst] = []
        return msgs

    def __str__(self):
        return str(self.__queue)
