# -*- coding:utf-8 -*-
#
import time

letter='abcdefghijklmnopqrstuvwyzABCDEFGHIJKLMNOPQRSTUWYZ'
len_letter=len(letter)

def nextString(length=0):
  source=str(int(time.time()*10000000))
  if length > len(source) or length <= 0:
    length = len(source)
  sr=""
  while length > 1:
    sr=sr+letter[int(source[len(source)-length]+source[len(source)-length+1])%len(letter)]
    length=length-1
  return sr

