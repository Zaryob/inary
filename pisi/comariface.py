# -*- coding: utf-8 -*-

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
