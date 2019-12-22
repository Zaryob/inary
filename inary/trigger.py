
import os
import inary.context as ctx
import inary.util as util

class Trigger:
    def __init__(self):
        self.specdir=None
        self.Locals = None
        self.Globals = None
        self.postscript = None

    def load_script(self):
        """Compiles and executes the script"""
        compiled_script = self.compile_script()

        try:
            localSymbols = globalSymbols = {}
            exec(compiled_script, localSymbols, globalSymbols)
        except Exception as e:
            raise (e)

        self.Locals = localSymbols
        self.Globals = globalSymbols

    def compile_script(self):
        """Compiles the script and returns a code object"""

        fname = util.join_path(self.postscript)
        try:
            buf = open(fname).read()
            return compile(buf, fname, "exec")
        except IOError as e:
            raise Error(_("Unable to read Post Operations Script ({0}): {1}").format(
                fname, e))
        except SyntaxError as e:
            raise Error(_("SyntaxError in Post Operations Script ({0}): {1}").format(
                fname, e))

    def run_command(self, func):
        """"""
        curDir = os.getcwd()
        os.chdir(ctx.config.dest_dir())
        if func in self.Locals:
            self.Locals[func]()

        else:
            pass

        os.chdir(curDir)
        return True

    def preinstall(self, specdir):
        self.specdir=specdir
        self.postscript = util.join_path(self.specdir, ctx.const.postops)
        self.load_script()
        self.run_command("preInstall")

    def postinstall(self, specdir):
        self.specdir=specdir
        self.postscript = util.join_path(self.specdir, ctx.const.postops)
        self.load_script()
        self.run_command("postInstall")

    def postremove(self, specdir):
        self.specdir=specdir
        self.postscript = util.join_path(self.specdir, ctx.const.postops)
        self.load_script()
        self.run_command("postRemove")

    def preremove(self, specdir):
        self.specdir=specdir
        self.postscript = util.join_path(self.specdir, ctx.const.postops)
        self.load_script()
        self.run_command("preRemove")
