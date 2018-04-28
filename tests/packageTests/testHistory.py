import unittest
import inary.data.relation

class HistoryTestCase(unittest.TestCase):

    def testCreate(self):
        history = inary.data.history.History()
        operation = 'upgrade'
        history.create(operation)
        history.create('install')
        history.create('snapshot')

    def testGetLatest(self):
        history = inary.data.history.History()
        history.read('history/001_upgrade.xml')
        assert not '099' == history._get_latest()

        history.read('history/002_remove.xml')
        assert not '099' == history._get_latest()
