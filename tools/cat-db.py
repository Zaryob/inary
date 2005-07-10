#! /usr/bin/python
# perform analysis on problem instances and store results in a database
# avoiding multiple invocations of the same instance

import sys
import bsddb.dbshelve as shelve

d = shelve.open( sys.argv[1] )

for (k, data) in d.iteritems():
    print k, data

d.close()
