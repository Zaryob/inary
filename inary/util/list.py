# -*- coding: utf-8 -*-
#
#
# Copyright (C) 2021 , Ali Rıza KESKİN (sulincix)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

"""Advanced list can compare lists that has ultra large amount of items."""

class AdvancedList:

    def __init__(self,fpar=3,lpar=4):
        """fpar is calculate hash first character parameter, lpar is max key length parameter"""
        self.__liststore = {}
        self.__f=fpar
        self.__l=lpar
        self.__lengthstore = {}
        from hashlib import sha1 as sha1
        self.sha1 = sha1
        

    def __get_path(self,element):
        return self.sha1(str(element)[:self.__f].encode("utf-8")).hexdigest()[:self.__l]

    def __get_array(self,path):
        if path not in self.__liststore:
            self.__liststore[path] = []
            self.__lengthstore[path] = 0
        return self.__liststore[path]

    def __sync(self,path):
        self.__lengthstore[path] = len(self.__get_array(path))

    def add(self,element=None):
        """add element by auto generated key"""
        path = self.__get_path(element)
        self.__get_array(path).append(element)
        self.__sync(path)

    def remove(self,element=None):
        """remove element from list"""
        path = self.__get_path(element)
        self.__get_array(path).remove(element)
        self.__sync(path)

    def all(self):
        """return simple array of all element"""
        ret = []
        for i in self.__liststore.keys():
            for j in self.__liststore[i]:
                ret.append(j)
        return ret

    def exists(self,element):
        """check element available in list"""
        path = self.__get_path(element)
        return path in self.__liststore and element in self.__liststore[path]

    def length(self):
        """return list length"""
        ret = 0
        for i in self.__lengthstore :
            ret += self.__lengthstore[i]
        return ret

    def keys(self):
        """return array of list keys"""
        return self.__liststore.keys()
