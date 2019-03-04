import inary.actionsapi
from inary.actionsapi.shelltools import system
from inary.actionsapi.shelltools import can_access_file
from inary.actionsapi import get

class MesonError(inary.actionsapi.Error):
    def __init__(self, value=''):
        inary.actionsapi.Error.__init__(self, value)
        self.value = value
        ctx.ui.error(value)

def meson_configure(parameters=""):
    if can_access_file('meson.build'):
        prefix = get.emul32prefixDIR() if get.buildTYPE() == "emul32" else get.defaultprefixDIR()
        args="meson \
              --prefix=/{0} \
              --buildtype=plain \
              --libdir=/{0}/lib{1} \
              --libexecdir={2} \
              --sysconfdir={3} \
              --localstatedir={4} \
              {5} inaryPackageBuild".format(
                      prefix,
                      "32 " if get.buildTYPE() == "emul32" else "",
                      get.libexecDIR(),
                      get.confDIR(),
                      get.localstateDIR(),
                      parameters)

        if system(args):
            raise MesonError(_('[Meson]: Configure failed.'))
    else:
            raise MesonError(_('[Meson]: Configure script cannot be reached'))

def ninja_build(parameters=""):
    if system("ninja {} {} -C inaryPackageBuild".format(get.makeJOBS(),parameters)):
        raise MesonError(_("[Ninja]: Build failed."))

def ninja_install(parameters=""):
    if system('DESTDIR="{}" ninja install {} -C inaryPackageBuild'.format(get.installDIR(),get.makeJOBS())):
        raise MesonError(_("[Ninja]: Installation failed."))

def ninja_check():
    if system('ninja test {} -C inaryPackageBuild'.format(get.makeJobs())):
        raise MesonError(_("[Ninja]: Test failed"))
