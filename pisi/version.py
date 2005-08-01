# Copyright (C) 2005, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

# version structure

# Authors:  Eray Ozkural <eray@uludag.org.tr>

import util

class Version:
    def __init__(self, verstring):
        self.comps = map(lambda x: int(x), util.multisplit(verstring,'.-'))
        self.verstring = verstring

    def string():
        return self.verstring

    def pred(self,rhs,pred):
        for i in range(0, len(self.comps)-1):
            if pred(self.comps[i],rhs.comps[i]):
                return True
        else:
            return False

    def lt(self,rhs):
        return self.pred(rhs, lambda x,y: x<y)

    def le(self,rhs):
        return self.pred(rhs, lambda x,y: x<=y)

    def gt(self,rhs):
        return self.pred(rhs, lambda x,y: x>y)

    def ge(self,rhs):
        return self.pred(rhs, lambda x,y: x>=y)

