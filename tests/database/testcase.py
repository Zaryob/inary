import unittest

import inary
import inary.context as ctx

class TestCase(unittest.TestCase):

    def setUp(self):
        options = inary.config.Options()
        options.destdir = 'repos/tmp'
        inary.api.set_options(options)
        inary.api.set_scom(False)

        ctx.config.values.general.distribution = "Pardus"
        ctx.config.values.general.distribution_release = "2007"

        if not inary.api.list_repos():
            inary.api.add_repo("pardus-2007", "repos/pardus-2007-bin/pisi-index.xml")
            inary.api.add_repo("contrib-2007", "repos/contrib-2007-bin/pisi-index.xml")
            inary.api.add_repo("pardus-2007-src", "repos/pardus-2007/pisi-index.xml")
            inary.api.update_repo("pardus-2007")
            inary.api.update_repo("contrib-2007")
            inary.api.update_repo("pardus-2007-src")
