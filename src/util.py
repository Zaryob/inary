# -*- coding: utf-8 -*-
import os
import string

def information(message):
    print message

# run a command non-interactively
def run_batch(cmd):
    print 'running ', cmd
    a = os.popen(cmd)
    lines = a.readlines()
    ret = a.close()
    print 'return value ', ret
    successful = ret == None
    if not successful:
      print 'ERROR: executing command', cmd
      for x in lines:
        print x
    return (successful,lines)

# print a list
def strlist(l):
    return string.join(map(lambda x: str(x) + ' ', l))
