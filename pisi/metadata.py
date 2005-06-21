
from ui import ui

from xmlfile import *
import specfile
from specfile import SpecFile

class MetaData(SpecFile):
    """This is a superset of the source spec definition"""
    def __init__(self):
	XmlFile.__init__(self, "METADATA")

    def read(self, filename):
	self.readxml(filename)

        self.distribution = self.getNodeText("Distribution")
        self.distributionRelease = self.getNodeText("DistributionRelease")
        self.architecture = self.getNodeText("Architecture")
	size = self.getNodeText("InstalledSize")
	if size:
	    self.installedSize = int(size)

    def write(self, filename):
        ui.info("METADATA WRITE NOT IMPLEMENTED\n")
        pass

    def verify():
        if len(packages) != 1:
            return False
        return True
