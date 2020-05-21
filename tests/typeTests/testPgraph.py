import unittest
import os
import inary
from inary.data import pgraph


class GraphTestCase(unittest.TestCase):
    def setUp(self):
        self.g0 = pgraph.Digraph()
        self.g0.add_edge(1, 2)
        self.g0.add_edge(1, 3)
        self.g0.add_edge(2, 3)
        self.g0.add_edge(3, 4)
        self.g0.add_edge(4, 1)

        self.g1 = pgraph.Digraph()
        self.g1.add_edge(0, 2)
        self.g1.add_edge(0, 3)
        self.g1.add_edge(2, 4)
        self.g1.add_edge(3, 4)

    def testHasVertex(self):
        assert not self.g0.has_vertex(5)
        assert not self.g1.has_vertex(1)

    def testHasEdge(self):
        assert not self.g0.has_edge(5, 6)
        assert not self.g0.has_edge(3, 5)
        assert not self.g1.has_edge(2, 3)

    def testCycle(self):
        assert not self.g0.cycle_free()
        assert self.g1.cycle_free()

    def testTopologicalSort(self):
        order = self.g1.topological_sort()
        assert order[0] == 0
        assert order[-1] == 4
