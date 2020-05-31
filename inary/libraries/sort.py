# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 - 2020, Ali Rıza KESKIN (sulincix)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#
def sort_bubble(array=[], reverse=False):
    mlen = len(array)
    cout_i = 0
    while cout_i < mlen:
        cout_j = 0
        while cout_j < mlen - 1:
            if array[cout_j - 1] > array[cout_j]:
                tmp = array[cout_j - 1]
                array[cout_j - 1] = array[cout_j]
                array[cout_j] = tmp
            cout_j = cout_j + 1
        cout_i = cout_i + 1
    if reverse:
        array.reverse()
    return array


def sort_merge(x, reverse=False):
    result = []
    if len(x) < 2:
        return x
    mid = int(len(x) / 2)
    y = sort_merge(x[:mid])
    z = sort_merge(x[mid:])
    while (len(y) > 0) or (len(z) > 0):
        if len(y) > 0 and len(z) > 0:
            if y[0] > z[0]:
                result.append(z[0])
                z.pop(0)
            else:
                result.append(y[0])
                y.pop(0)
        elif len(z) > 0:
            for i in z:
                result.append(i)
                z.pop(0)
        else:
            for i in y:
                result.append(i)
                y.pop(0)
    if reverse:
        result.reverse()
    return result


def sort_min_max(x, reverse=False):
    llist = []
    hlist = []
    while len(x) != 0:
        min = x[0]
        max = x[0]
        for i in x:
            if i <= min:
                min = i
            elif i >= max:
                max = i
        hlist.insert(0, max)
        x.remove(max)
        if min != max:
            llist.append(min)
            x.remove(min)
    array = llist + hlist
    if reverse:
        array.reverse()
    return array


def sort_auto(array=[], reverse=False):
    if len(array) <= 10:
        return sort_bubble(array, reverse)
    elif len(array) <= 500:
        return sort_min_max(array, reverse)
    else:
        return sort_merge(array, reverse)
