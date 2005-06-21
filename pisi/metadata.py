
import ui

from xmlfile import *
import specfile
from specfile import SpecFile

class MetaData(SpecFile):
    """This is a superset of the source spec definition"""

    def read(self, filename):
	super(MetaData, self).read(filename)
	distribution = self.getNodeText("Source/Distribution")
	distributionRelease = self.getNodeText("Source/DistributionRelease")
	architecture = self.getNodeText("Source/Architecture")
	installedSize = int(self.getNodeText("Source/InstalledSize"))

    def write(self, filename):
        ui.info("METADATA WRITE NOT IMPLEMENTED\n")
        pass

    def verify():
        if len(packages) != 1:
            return False
        return True
