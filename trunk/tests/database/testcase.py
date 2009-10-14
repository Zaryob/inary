import unittest

import pisi

class TestCase(unittest.TestCase):

    def setUp(self):
        options = pisi.config.Options()
        options.ignore_build_no = False
        options.destdir = 'repos/tmp'
        pisi.api.set_options(options)
        pisi.api.set_comar(False)

        if not pisi.api.list_repos():
            pisi.api.add_repo("pardus-2007", "repos/pardus-2007-bin/pisi-index.xml.bz2")
            pisi.api.add_repo("contrib-2007", "repos/contrib-2007-bin/pisi-index.xml.bz2")
            pisi.api.add_repo("pardus-2007-src", "repos/pardus-2007/pisi-index.xml.bz2")
            pisi.api.update_repo("pardus-2007")
            pisi.api.update_repo("contrib-2007")
            pisi.api.update_repo("pardus-2007-src")
            
