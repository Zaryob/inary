import sys

import pisi.install
from pisi.ui import ui

def install(packagefile):
    try:
        ui.info('* Installing ' + packagefile + '\n')
        pisi.install.install(packagefile)
    except pisi.install.InstallError, e:
        print '*** An installation error has occured:'
        print '\t', e
        sys.exit(1)
