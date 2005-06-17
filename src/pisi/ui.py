# generic user interface

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
        if showDebug:
            sys.stdout.write(msg)
            sys.stdout.flush()

    def error(self,msg):
        sys.stdout.write(colorize(msg, 'red'))
        sys.stdout.flush()

# default UI is CLI
ui = CLI()

