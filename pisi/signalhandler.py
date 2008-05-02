# -*- coding: utf-8 -*-
#
# Copyright (C) 2006, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

import signal

exception = {
    signal.SIGINT:KeyboardInterrupt
    }

class Signal:
    def __init__(self, sig):
        self.signal = sig
        self.oldhandler = signal.getsignal(sig)
        self.pending = False

class SignalHandler:

    def __init__(self):
        self.signals = {}

    def signal_handler(self, sig, frame):
        signal.signal(sig, signal.SIG_IGN)
        self.signals[sig].pending = True

    def disable_signal(self, sig):
        if sig not in self.signals.keys():
            self.signals[sig] = Signal(sig)
            signal.signal(sig, self.signal_handler)

    def enable_signal(self, sig):
        if sig in self.signals.keys():
            oldie = self.signals[sig].oldhandler
            oldhandler =  oldie if oldie else signal.SIG_DFL
            pending = self.signals[sig].pending
            del self.signals[sig]
            signal.signal(sig, oldhandler)
            if pending:
                raise exception[sig]

    def signal_disabled(self, sig):
        return sig in self.signals.keys()

    def signal_pending(self, sig):
        return self.signal_disabled(sig) and self.signals[sig].pending
