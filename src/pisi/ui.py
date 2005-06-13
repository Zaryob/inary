# generic user interface

import sys

# put the interface directly in the module
# since the UI is _unique_

def register(_impl):
    """ Register a UI implementation"""
    impl = _impl

def info(msg):
    impl.info(msg)

# default UI implementation
class CLI:
    def info(self, msg):
        sys.stdout.write(msg)
        sys.stdout.flush()

# default UI is CLI
impl = CLI()

