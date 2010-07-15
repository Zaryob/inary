
from pisi.actionsapi import pisitools

WorkDir = "skeleton"

def install():
    pisitools.dobin("skeleton.py")
    pisitools.rename("/usr/bin/skeleton.py", "bar")
