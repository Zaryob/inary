
import unittest
import os

from pisi import graph
from pisi.config import config

class GraphTestCase(unittest.TestCase):
    def setUp(self):
        g0 = graph.digraph()
        g0.from_list([ (1,2), (1,3), (2,3), (3,4), (4, 5), (4,1)])
        
        g1 = graph.digraph()
        g1.from_list([ (0,2), (0,3), (3,4), (2,4), (0,5), (5,4) ])
        self.g1 = g1

    def testCycle(self):
        pass

    def testTopologicalSort(self):
        order = self.g1.topological_sort()
        self.assertEqual(order[0], 0)
        self.assertEqual(order[len(order)-1], 4)
    
suite = unittest.makeSuite(GraphTestCase)
