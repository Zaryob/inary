#!/usr/bin/python3
import sys
esc = "\x1b"


class logger:

    logfile = None
    nocolor = False
    nodebug = True
    noverbose = True
    noinfo = False

    BLACK = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    PURPLE = 35
    CYAN = 36
    WHITE = 37

    RESET = 0
    BOLD = 1
    DIM = 2
    ITALIC = 3
    UNDERLINE = 4
    BLINK = 5
    REVERSE = 7
    HIDDEN = 8

    def print(self, msg, color=0, attr=0, fd=sys.stdout, nowrite=False):
        if(not nowrite):
            fd.write(self.colorize(msg, color, attr))
        if(self.logfile):
            self.logfile.write(msg)

    def println(self, msg, color=0, attr=0, fd=sys.stdout, nl=True, nowrite=False):
        if(nl):
            self.print(msg+"\n", color, attr, fd, nowrite)
        else:
            self.print(msg, color, attr, fd, nowrite)

    def colorize(self, msg, color=None, attr=None):
        if((not self.nocolor) or ((not attr) and (not color))):
            ret = ""
            if (attr):
                ret = "{0}{1}[{2}m".format(ret, esc, str(attr))
            if (color):
                ret = "{0}{1}[{2}m".format(ret, esc, str(color))
            ret = "{0}{1}{2}[;0m".format(ret, msg, esc)
            return ret
        else:
            return msg

    def output(self, msg, newline=True):
        """Level 1 output"""
        self.println(msg, nl=newline)

    def info(self, msg, newline=True):
        """Level 2 output"""
        self.println(msg, color=self.BLUE, attr=self.BOLD,
                     nl=newline, nowrite=self.noinfo)

    def verbose(self, msg, newline=True):
        """Level 3 output"""
        self.println(msg, color=self.CYAN, nl=newline, nowrite=self.noverbose)

    def debug(self, msg, newline=True):
        """Level 4 output"""
        self.println(msg, color=self.GREEN, attr=self.ITALIC,
                     nl=newline, nowrite=self.nodebug)

    def warning(self, msg, newline=True):
        """Level 5 output"""
        self.println(msg, color=self.YELLOW, attr=self.BOLD,
                     fd=sys.stderr, nl=newline)

    def error(self, msg, newline=True):
        """Level 6 output"""
        self.println(msg, color=self.PURPLE, attr=self.UNDERLINE,
                     fd=sys.stderr, nl=newline)

    def fatal(self, msg, status=1, newline=True):
        """Level 7 output"""
        self.println(msg, color=self.RED, attr=self.BOLD,
                     fd=sys.stderr, nl=newline)
        exit(status)
