# -*- coding: utf-8 -*-

from pisi.index import Index
from pisi.ui import ui

def index(repo_dir = '.'):
    ui.info('* Building index of PISI files under ' + repo_dir + '\n')

    index = Index()
    index.index(repo_dir)
    index.write('pisi-index.xml')
    
    ui.info('* Index file written')

def updatedb(indexfile):
    ui.info('* Updating DB from index file: ' + indexfile + '\n')

    index = Index()
    index.read(indexfile)
    index.update_db()

    ui.info('* Package db updated.\n')
