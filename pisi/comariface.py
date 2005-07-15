# -*- coding: utf-8 -*-

import socket

def sendCommand(cmd, blocking=False):
    s = socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
    s.connect("/tmp/comar")
    s.send(cmd)
    s.close()

def registerScript(om, appname, scriptPath):
    cmd = '+' + om + ' ' + appname + ' ' +scriptPath + '\n'
    sendCommand(cmd)

def removeScript(appname):
    cmd = "-" + appname + '\n'
    sendCommand(cmd)

def call(om):
    cmd = '$' + om + '\n'
    sendCommand(cmd)
