
from pisi.install import PisiInstall
from pisi.context import InstallContext
from pisi.purl import PUrl

def install(packagefile):
    url = PUrl(packagefile)
    if url.isRemoteFile():
        pass # bunu simdilik bosverelim, once bir calissin :)
    else:
        ctx = InstallContext(url.uri)

    pi = PisiInstall(ctx)
    pi.install()
