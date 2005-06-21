
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

        self.distribution = self.getNodeText("Source/Distribution")
        self.distributionRelease = self.getNodeText("Source/DistributionRelease")
        self.architecture = self.getNodeText("Source/Architecture")
        self.installedSize = self.getNodeText("Source/InstalledSize")

    def write(self, filename):
        ui.info("METADATA WRITE NOT IMPLEMENTED\n")
        pass

    def verify():
        if len(packages) != 1:
            return False
        return True
