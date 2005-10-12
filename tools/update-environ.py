#!/usr/bin/python
# -*- coding: utf-8 -*-

# Generates /etc/ld.so.conf and /etc/profile.env according to /etc/env.d directory

import os
import re

def env_update():
    if not os.path.exists("/etc/env.d"):
        os.makedirs("/etc/env.d", 0755)

    list = []
    for file in os.listdir("/etc/env.d"):
        if not os.path.isdir(os.path.join("/etc/env.d", file)):
            list.append(file)

    list.sort()

    keys = {}
    for file in list:
        f = open(os.path.join("/etc/env.d", file), "r")
        for line in f:
            if not re.search("^#", line.strip()):
                currentLine = line.strip().split("=")
                
                try:
                    if keys.has_key(currentLine[0]):
                        keys[currentLine[0]] += ":" + currentLine[1].replace("\"", "")
                    else:
                        keys[currentLine[0]] = currentLine[1].replace("\"", "")
                except IndexError:
                    pass

    keys["PATH"] += ":/bin/:/sbin/:/usr/bin/"
    f = open("/etc/profile.env", "w")
    for key in keys:
        f.write("export %s=\"%s\"\n" % (key, keys[key]))
    f.close()

    f = open("/etc/ld.so.conf", "w")
    for path in keys["LDPATH"].split(":"):
        f.write("%s\n" % path)
    f.close()
       

if __name__ == "__main__":
    env_update()                      
