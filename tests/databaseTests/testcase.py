import unittest
import inary
import inary.context as ctx

class TestCase(unittest.TestCase):

    def setUp(self):
        options = inary.config.Options()
        options.destdir = 'repos/tmp'
        inary.api.set_options(options)
        inary.api.set_scom(False)
        ctx.config.values.general.distribution = "Sulin"
        ctx.config.values.general.distribution_release = "2018"

        if not inary.api.list_repos():
            inary.api.add_repo("repo1", "repos/repo1-bin/inary-index.xml")
            inary.api.add_repo("repo2", "repos/repo2-bin/inary-index.xml")
            inary.api.add_repo("repo1-src", "repos/repo1/inary-index.xml")
        inary.api.update_repo("repo1")
        inary.api.update_repo("repo2")
        inary.api.update_repo("repo1-src")
