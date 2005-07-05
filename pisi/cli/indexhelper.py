# -*- coding: utf-8 -*-

from pisi.index import Index
from pisi.ui import ui

def updateindex(indexfile):
    ui.info('* Updating index from index file: ' + indexfile + '\n')

    index = Index()
    index.read(indexfile)
    index.update_db()

    ui.info('* Package db updated.\n')
