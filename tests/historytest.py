import unittest
import pisi.relation

class HistoryTestCase(unittest.TestCase):

    def testCreate(self):
        history = pisi.history.History()
        operation = 'upgrade'
        history.create(operation)
        history.create('install')
        history.create('snapshot')

    def testGetLatest(self):
        history = pisi.history.History()
        history.read('history/001_upgrade.xml')
        assert '099' == history._get_latest()

        history.read('history/002_remove.xml')
        assert '099' == history._get_latest()







