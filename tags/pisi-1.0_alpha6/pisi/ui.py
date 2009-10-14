# Copyright (C) 2005, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#
# generic user interface
#
# Authors:  Eray Ozkural <eray@uludag.org.tr>
#           Murat Eren <meren@uludag.org.tr>

import sys

import pisi
import pisi.context as ctx

class UI(object):
    "Abstract class for UI operations, derive from this."

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

    def __init__(self, debuggy = False, verbose = False):
        self.show_debug = debuggy
        self.show_verbose = verbose

    def set_verbose(self, flag):
        self.show_verbose = flag

    def set_debug(self, flag):
        self.show_debug = flag

    def info(self, msg, verbose = False, noln = False):
        "give an informative message"
        pass

    def ack(self, msg):
        "inform the user of an important event and wait for acknowledgement"
        pass

    def debug(self, msg):
        "show debugging info"
        if self.show_debug:
            self.info('DEBUG: ' + msg)

    def warning(self,msg):
        "warn the user"
        pass

    def error(self,msg):
        "inform a (possibly fatal) error"
        pass

    def action(self,msg):
        "uh?"
        pass

    def choose(self, msg, list):
        "ask the user to choose from a list of alternatives"
        pass

    def confirm(self, msg):
        "ask a yes/no question"
        pass
    
    def display_progress(self, pd):
        "display progress"
        pass
