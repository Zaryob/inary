import unittest

import pisi
import pisi.context as ctx

class TestCase(unittest.TestCase):

    def setUp(self):
        options = pisi.config.Options()
        options.destdir = 'repos/tmp'
        pisi.api.set_options(options)
        pisi.api.set_comar(False)

        ctx.config.values.general.distribution = "Pardus"
        ctx.config.values.general.distribution_release = "2007"

        if not pisi.api.list_repos():
            pisi.api.add_repo("pardus-2007", "repos/pardus-2007-bin/pisi-index.xml")
            pisi.api.add_repo("contrib-2007", "repos/contrib-2007-bin/pisi-index.xml")
            pisi.api.add_repo("pardus-2007-src", "repos/pardus-2007/pisi-index.xml")
            pisi.api.update_repo("pardus-2007")
            pisi.api.update_repo("contrib-2007")
            pisi.api.update_repo("pardus-2007-src")
