import inary.actionsapi.shelltools as shelltools

sourcefile = "action.sh"


def prepare(args=''):
    shelltools.system("source {} ; _prepare {}".format(sourcefile, args))


def pkgver(args=''):
    shelltools.system("source {} ; _pkgver {}".format(sourcefile, args))


def build(args=''):
    shelltools.system("source {} ; _build {}".format(sourcefile, args))


def check(args=''):
    shelltools.system("source {} ; _check {}".format(sourcefile, args))


def install(args=''):
    shelltools.system("source {} ; _install {}".format(sourcefile, args))
