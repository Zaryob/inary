
from ui import ui

from xmlfile import *
from specfile import *


class MetaData(XmlFile):
    """Package metadata. Metadata is composed of Specfile and various
other information."""
    def __init__(self):
        XmlFile.__init__(self, "METADATA")

    def read(self, filename):
        self.readxml(filename)

        getNodeText = self.getNodeText

        self.name = getNodeText("Name")
        # self.summary # birden fazla olabilir (tr, en) SummaryInfo
                       # icerisine almakta yarar var. SpecFile'da da
                       # bu sekilde bir duzenleme gerekiyor.
        self.homepage = getNodeText("Homepage")
        self.license = getNodeText("License")
	
        historyElts = self.getAllNodes("History/Update")
        self.history = [HistoryInfo(x) for x in historyElts]
        self.version = self.history[0].version
        self.release = self.history[0].release

        self.distribution = getNodeText("Distribution")
        self.distributionRelease = getNodeText("DistributionRelease")
        self.architecture = getNodeText("Architecture")
        size = self.getNodeText("InstalledSize")
        if size:
            self.installedSize = int(size)

    def write(self, filename):
        ui.info("METADATA WRITE NOT IMPLEMENTED\n")
        pass

    def verify():
        return True
