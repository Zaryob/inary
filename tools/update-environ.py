#!/usr/bin/python
# -*- coding: utf-8 -*-

# Generates /etc/ld.so.conf and /etc/profile.env according to /etc/env.d directory

import sys

sys.path.append('.')
import pisi.util as util

if __name__ == "__main__":
    util.env_update()
