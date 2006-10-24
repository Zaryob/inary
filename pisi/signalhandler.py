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

class SignalHandler:

    def __init__(self):
        self.pending_signals = []
        self.disabled_signals = []

    def signal_handler(self, sig, frame):
        signal.signal(sig, signal.SIG_IGN)
        if sig not in self.pending_signals:
            self.pending_signals.append(sig)
            
    def clear_pending_signal(self, sig):
        if sig in self.pending_signals:
            self.pending_signals.remove(sig)

    def disable_signal(self, sig):
        signal.signal(sig, self.signal_handler)

        if sig not in self.disabled_signals:
            self.disabled_signals.append(sig)

    def enable_signal(self, sig):
        signal.signal(sig, signal.SIG_DFL)

        if sig in self.disabled_signals:
            self.disabled_signals.remove(sig)

        if sig in self.pending_signals:
            self.clear_pending_signal(sig)
            raise exception[sig]

    def signal_disabled(self, sig):
        return sig in self.disabled_signals

    def signal_pending(self, sig):
        return sig in self.pending_signals
