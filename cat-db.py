#! /usr/bin/python
# perform analysis on problem instances and store results in a database
# avoiding multiple invocations of the same instance

import sys
import string
import bsddb.dbshelve as shelve
import os

d = shelve.open( sys.argv[1] )

#print 'list serial time, db size ', len(d) 
for (k,data) in d.iteritems():
    print k, data

d.close()
