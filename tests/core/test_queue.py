import unittest
from aura.core.queue import Queue

class TestQueue(unittest.TestCase):
    def test_send(self):
        q = Queue()
        orig, dst, msg = "12", "34", "hello world"
        q.send(orig, dst, msg)
        a = q.receive(dst)[0]
        self.assertEqual(a[0], orig)
        self.assertEqual(a[1], msg)



