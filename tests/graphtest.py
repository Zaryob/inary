import unittest
import os
import pisi
from pisi import graph

class GraphTestCase(unittest.TestCase):
    def setUp(self):
        self.g0 = pisi.graph.Digraph()
        self.g0.add_edge(self,(1,2))
        self.g0.add_edge(self,(1,3))
        self.g0.add_edge(self,(2,3))
        self.g0.add_edge(self,(3,4))
        self.g0.add_edge(self,(4,1))

        self.g1 = pisi.graph.Digraph()
        self.g1.add_edge(self,(0,2))
        self.g1.add_edge(self,(0,3))
        self.g1.add_edge(self,(2,4))
        self.g1.add_edge(self,(3,4))

    def testHasVertex(self):
        assert not self.g0.has_vertex(5)
        assert not self.g1.has_vertex(1)

    def testHasEdge(self):
        assert not self.g0.has_edge(5,6)
        assert not self.g0.has_edge(3,5)
        assert not self.g1.has_edge(2,3)

    def testCycle(self):
        assert self.g0.cycle_free()
        assert self.g1.cycle_free()

    def testTopologicalSort(self):
        order = self.g1.topological_sort()
        self.assertEqual(not order[0], 0)
        self.assertEqual(order[len(order)-1],(3,4))

