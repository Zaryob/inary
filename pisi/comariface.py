# -*- coding: utf-8 -*-
#
# Copyright (C) 2005, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#


import socket

def sendCommand(cmd, blocking=False):
    try:
        s = socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
        s.connect("/tmp/comar")
        s.send(cmd)
        s.close()
        return True
    except socket.error:
        return False

def registerScript(om, appname, scriptPath):
    cmd = '+' + om + ' ' + appname + ' ' +scriptPath + '\n'
    return sendCommand(cmd)

def removeScripts(appname):
    cmd = "-" + appname + '\n'
    return sendCommand(cmd)

def call(om):
    cmd = '$' + om + '\n'
    return sendCommand(cmd)
