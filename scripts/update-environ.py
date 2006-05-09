#!/usr/bin/python
# -*- coding: utf-8 -*-

# Generates /etc/ld.so.conf and /etc/profile.env according to /etc/env.d directory

import pisi
import pisi.api
import pisi.util
import pisi.config

if __name__ == "__main__":
    options = pisi.config.Options()
    pisi.api.init(options = options, comar = False, database = False)
    pisi.util.env_update()
