# -*- coding: utf-8 -*-

import socket

def registerScript(om, scriptPath):
    s = socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
    s.connect("/tmp/comar")
    cmd = '+' + om + ' ' + scriptPath + '\n'
    s.send(cmd)
    s.close()
    return True

def call(om):
    s = socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
    s.connect("/tmp/comar")
    cmd = '$' + om + '\n'
    s.send(cmd)
    return s.recv(500)
