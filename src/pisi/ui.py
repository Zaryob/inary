# generic user interface

import sys
from colors import colorize

# put the interface directly in the module
# since the UI is _unique_

def register(_impl):
    """ Register a UI implementation"""
    impl = _impl

def info(msg):
    impl.info(msg)

def error(msg):
    impl.error(msg)

# default UI implementation
class CLI:
    def info(self, msg):
        sys.stdout.write(colorize(msg, 'blue'))
        sys.stdout.flush()

    def error(self,msg):
        sys.stdout.write(colorize(msg, 'red'))
        sys.stdout.flush()
# default UI is CLI
impl = CLI()

