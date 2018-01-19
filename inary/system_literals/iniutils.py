# -*- coding: utf-8 -*-
#
# Copyright (C) 2018, Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

"""initutils module provides ini style configuration file utils."""

import os
import configparser

from .fileutils import FileLock

class iniDB:
    def __init__(self, db_file, db_mode=0o600):
        try:
            os.makedirs(os.path.dirname(db_file))
        except OSError:
            pass
        self.db_file = db_file
        if not os.path.exists(db_file):
            self.__writelock()
            open(db_file, "w").close()
            os.chmod(db_file, db_mode)
            self.__unlock()
        self.__readlock()
        self.cp = configparser.ConfigParser()
        try:
            self.cp.read(db_file)
        except:
            print(("Network configuration file {} is corrupt".format(db_file)))
        self.__unlock()

    def __writelock(self):
        self.fl = FileLock(self.db_file)
        self.fl.lock(shared=False)

    def __readlock(self):
        self.fl = FileLock(self.db_file)
        self.fl.lock(shared=True)

    def __unlock(self):
        self.fl.unlock()

    def listDB(self):
        profiles = self.cp.sections()
        if "general" in profiles:
            profiles.remove("general")
        return profiles

    def getDB(self, name):
        dct = {}
        if name in self.cp.sections():
            dct = dict(self.cp.items(name))
        return dct

    def setDB(self, name, dct):
        for key, value in list(dct.items()):
            if value:
                if name not in self.cp.sections():
                    self.cp.add_section(name)
                self.cp.set(name, key, value)
            elif name in self.cp.sections():
                self.cp.remove_option(name, key)
        # FIXME: This is an ugly hack...
        db = iniDB(self.db_file)
        for nm in db.listDB():
            if nm == name:
                continue
            for key, value in list(db.getDB(nm).items()):
                self.cp.set(nm, key, value)
        self.__writelock()
        fp = open(self.db_file, "w")
        self.cp.write(fp)
        fp.close()
        self.__unlock()

    def remDB(self, name):
        self.cp.remove_section(name)
        self.__writelock()
        fp = open(self.db_file, "w")
        self.cp.write(fp)
        fp.close()
        self.__unlock()

class iniParserError(Exception):
    """
        Base exception for iniParser errors.
    """
    pass

class iniParser:
    """
        INI file parsing and manipulation class.

        ip = iniParser("my.ini", [chmod=0600, [quiet=False]])
        ip.listSections() => ["section1", "section2", ...]
        ip.getSection("section1") => {"field1": "value1", "field2": "value2"}
        ip.setSection("section1",{"field1": "value1", "field2": "value2"})
        ip.removeSection("section2")

    """

    def __init__(self, inifile, chmod=0o600, quiet=False):
        """
            Constuctor. Creates INI file if it doesn't exist and sets file mode.
        """
        self.inifile = inifile
        self.chmod = chmod
        self.quiet = quiet
        try:
            os.makedirs(os.path.dirname(inifile))
        except OSError:
            pass
        if not os.path.exists(inifile):
            self.__writeLock()
            open(inifile, "w").close()
            self.__unlock()
        os.chmod(inifile, chmod)

    def __writeLock(self):
        """
            Puts a write lock to file.
        """
        self.fl = FileLock(self.inifile)
        self.fl.lock(shared=False)

    def __readLock(self):
        """
            Puts a read lock to file.
        """
        self.fl = FileLock(self.inifile)
        self.fl.lock(shared=True)

    def __unlock(self):
        """
            Removes lock from file.
        """
        self.fl.unlock()

    def __readIni(self):
        """
            Gets content of the INI.
        """
        ini = configparser.ConfigParser()
        try:
            ini.read(self.inifile)
        except configparser.Error:
            ini = None
        return ini

    def __writeIni(self, ini):
        """
            Writes INI to file.
        """
        fp = open(self.inifile, "w")
        ini.write(fp)
        fp.close()

    def listSections(self):
        """
            Lists sections of INI file.
        """
        self.__readLock()
        ini = self.__readIni()
        self.__unlock()
        if not ini:
            if self.quiet:
                self.__fixIniFile()
                return []
            else:
                raise iniParserError("File is corrupt: {}".format(self.inifile))
        return ini.sections()

    def getSection(self, section):
        """
            Returns a section of INI file.
        """
        self.__readLock()
        ini = self.__readIni()
        self.__unlock()
        if not ini:
            if self.quiet:
                self.__fixIniFile()
                return {}
            else:
                raise iniParserError("File is corrupt: {}".format(self.inifile))
        if section not in ini.sections():
            return {}
        dct = {}
        if section in ini.sections():
            dct = dict(ini.items(section))
        return dct

    def setSection(self, section, dct):
        """
            Sets a section of INI file.
        """
        self.__writeLock()
        ini = self.__readIni()
        if not ini:
            self.__unlock()
            if self.quiet:
                self.__fixIniFile()
                self.setSection(section, dct)
                return
            else:
                raise iniParserError("File is corrupt: {}".format(self.inifile))
        if section not in ini.sections():
            ini.add_section(section)
        for key, value in list(dct.items()):
            if value:
                ini.set(section, key, value)
            elif section in ini.sections():
                ini.remove_option(section, key)
        self.__writeIni(ini)
        self.__unlock()

    def removeSection(self, section):
        """
            Removes a section from INI file.
        """
        self.__writeLock()
        ini = self.__readIni()
        if not ini:
            self.__unlock()
            if self.quiet:
                self.__fixIniFile()
                return
            else:
                raise iniParserError("File is corrupt: {}".format(self.inifile))
        ini.remove_section(section)
        self.__writeIni(ini)
        self.__unlock()

    def __fixIniFile(self):
        """
            Cleans bogus ini file.
        """
        self.__writeLock()
        open(self.inifile, "w").write("")
        self.__unlock()
