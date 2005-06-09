#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, glob, fileinput, string, sys, os, re
 
def kde_src_unpack( path ): 

#   fix the 'languageChange undeclared' bug group: touch all .ui files, so that the
#   makefile regenerate any .cpp and .h files depending on them.

    for roots, dirs, files in os.walk( path ):
        filtered_files = glob.glob( roots + '/*.ui' )
        if len( filtered_files ) > 0:
            for file in filtered_files:
                        os.utime( file, None )

#   Visiblity stuff is way broken! Just disable it when it's present
#   until upstream finds a way to have it working right.

    source_string = 'KDE_ENABLE_HIDDEN_VISIBILITY'

    if os.path.isfile( path + '/configure.in' ):    
        for line in fileinput.input( path + '/configure.in', inplace = 1 ):
            if re.search( source_string, line ):
                line = line.replace( source_string, '' )
            print line,
