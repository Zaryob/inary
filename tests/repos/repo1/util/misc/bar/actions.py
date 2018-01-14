from spam.actionsapi import pythonmodules
WorkDir = "gonullu"

def install():
    pythonmodules.install(pyVer='3')

def afterinstall():
    print('hello')
