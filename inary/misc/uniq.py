from inary.misc.mergesort import *

def uniq(list,sort=False):
    newlist=[]
    if list != []:
        if sort:
            list.sort()
            mcout=len(list)
            cout=0
            newlist.append(list[0])
            while cout < mcout-1:
                if list[cout+1] != list[cout]:
                    newlist.append(list[cout])
                cout=cout+1
        else:
            for item in list:
                if item not in newlist:
                    newlist.append(item)
    else:
        newlist=[]
    return newlist

