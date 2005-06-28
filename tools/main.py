#!/usr/bin/python

import os
import string

os.mkdir('packages')
for i in string.ascii_letters:
    os.mkdir('packages' + '/' + i)
