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

    def info(self, msg):
        sys.stdout.write(colorize(msg, 'blue'))
        sys.stdout.flush()

    def debug(self, msg):
        if self.showDebug:
            sys.stdout.write(msg)
            sys.stdout.flush()

    def error(self,msg):
        sys.stdout.write(colorize(msg, 'red'))
        sys.stdout.flush()

    def action(self,msg):
        sys.stdout.write(colorize(msg, 'green'))
        sys.stdout.flush()

    def confirm(self, msg):
        while True:
            s = raw_input(msg + colorize('(yes/no)', 'red'))
            if s.startswith('y') or s.startswith('Y'):
                return True
            if s.startswith('n') or s.startswith('N'):
                return False

    class Progress:
        def __init__(self, totalsize):
            self.totalsize = totalsize
            self.percent = 0

        def update(self, size):
            if not self.totalsize:
                return 100

            percent = (size * 100) / self.totalsize
            if percent and self.percent is not percent:
                self.percent = percent
                return percent
            else:
                return 0

    def displayProgress(self, pd):
        out = '\r%-30.30s %3d%% %12.2f %s' % \
            (pd['filename'], pd['percent'], pd['rate'], pd['symbol'])
        self.info(out)

# default UI is CLI
ui = CLI()
