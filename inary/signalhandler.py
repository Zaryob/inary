# -*- coding: utf-8 -*-
#
# Main fork Pisi: Copyright (C) 2005 - 2011, Tubitak/UEKAE
#
# Copyright (C) 2016 - 2020, Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

# Standard Python Modules
import signal

exception = {
    signal.SIGINT: KeyboardInterrupt
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
        if sig not in list(self.signals.keys()):
            self.signals[sig] = Signal(sig)
            signal.signal(sig, self.signal_handler)

    def enable_signal(self, sig):
        if sig in list(self.signals.keys()):
            if self.signals[sig].oldhandler:
                oldhandler = self.signals[sig].oldhandler
            else:
                oldhandler = signal.SIG_DFL
            pending = self.signals[sig].pending
            del self.signals[sig]
            signal.signal(sig, oldhandler)
            if pending:
                raise exception[sig]

    def signal_disabled(self, sig):
        return sig in list(self.signals.keys())

    def signal_pending(self, sig):
        return self.signal_disabled(sig) and self.signals[sig].pending
