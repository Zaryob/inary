import unittest
import inary
import inary.api
import inary.context as ctx

import inary.db.repodb
import inary.operations.repository as repository


class TestCase(unittest.TestCase):

    def setUp(self):
        options = inary.config.Options()
        options.destdir = 'tests/tmp_root'
        inary.api.set_options(options)
        inary.api.set_scom(False)
        ctx.config.values.general.distribution = "Sulin"
        ctx.config.values.general.distribution_release = "2019"
        ctx.config.values.general.ignore_safety = True

        if not inary.db.repodb.RepoDB().list_repos():
            #repository.add_repo("core-src", "https://gitlab.com/Zaryob/SulinRepository/raw/master/inary-index.xml")
            #repository.add_repo("core-binary", "https://sourceforge.net/projects/sulinos/files/packages/indispensable/inary-index.xml")
            repository.add_repo(
                "core-src",
                "http://127.0.0.1/SulinRepository/inary-index.xml")
            repository.add_repo(
                "core-binary",
                "http://127.0.0.1/indispensable/inary-index.xml.xz")
        repository.update_repo("core-src")
        repository.update_repo("core-binary")
