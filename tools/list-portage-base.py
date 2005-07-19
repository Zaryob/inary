#!/usr/bin/python
# -*- coding: utf-8 -*-

import portage

for package in portage.settings.packages:
    print package
