import unittest

from inary.mirrors import Mirrors


class MirrorsTestCase(unittest.TestCase):
    def testGetMirrors(self):
        with open("tests/mirrors.conf", "w") as mirror:
            mirror.write(
                """apache http://www.eu.apache.org/dist/
apache http://www.apache.org/dist/
apache http://apache.planetmirror.com.au/dist/
apache http://gd.tuwien.ac.at/infosys/servers/http/apache/dist/
apache http://apache.fastorama.com/dist/
apache http://mir2.ovh.net/ftp.apache.org/dist/
cpan http://www.perl.com/CPAN/
cpan http://mirrors.jtlnet.com/CPAN/
cpan ftp://ftp.ncsu.edu/pub/mirror/CPAN/
cpan ftp://ftp.duke.edu/pub/perl/
gnu http://ftp.gnu.org/gnu/""")
            mirror.flush()
            mirror.close()
        mirrors = Mirrors("tests/mirrors.conf")
        assert "http://www.eu.apache.org/dist/" in mirrors.get_mirrors(
            "apache")
        assert ['http://www.perl.com/CPAN/', 'http://mirrors.jtlnet.com/CPAN/',
                'ftp://ftp.ncsu.edu/pub/mirror/CPAN/', 'ftp://ftp.duke.edu/pub/perl/'] == mirrors.get_mirrors("cpan")
        assert ["http://ftp.gnu.org/gnu/"] == mirrors.get_mirrors("gnu")
