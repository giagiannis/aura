#!/usr/bib/python
import unittest
from aura.core import Queue

class TestQueue(unittest.TestCase):
    def test_send_receive(self):
        q = Queue()
        orig, dst, msg = "12", "34", "hello world"
        q.send(orig, dst, msg)
        msg2 = q.block_receive(dst, orig)
        self.assertEqual(msg2, msg)



