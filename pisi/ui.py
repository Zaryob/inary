# generic user interface
# Authors:  Eray Ozkural <eray@uludag.org.tr>
#           Murat Eren <meren@uludag.org.tr>

import sys
from colors import colorize

def register(_impl):
    """ Register a UI implementation"""
    ui = _impl

# default UI implementation
class CLI:
    def __init__(self, debuggy = True):
        self.showDebug = debuggy

    class Progress:
        def __init__(self, name, symbol):
            self.name = name
            self.percent = 0
            self.rate = 0
            self.symbol = symbol

    def info(self, msg):
        sys.stdout.write(colorize(msg, 'blue'))
        sys.stdout.flush()

    def debug(self, msg):
        if showDebug:
            sys.stdout.write(msg)
            sys.stdout.flush()

    def error(self,msg):
        sys.stdout.write(colorize(msg, 'red'))
        sys.stdout.flush()

    def startProgress(self, name, symbol):
        ## support one progress for now
        self.activeProgress = Progress(name, symbol)

    def updateProgress(self, percent, rate):
        self.activeProgress.percent = percent
        self.activeProgress.rate = rate
        self.displayProgress(pd)

    def displayProgress(pd):
        out = '\r%-30.30s %3d%% %12.2f %s' % \
              (self.name, self.percent, self.rate, self.symbol)
        self.info(out)

# default UI is CLI
ui = CLI()
