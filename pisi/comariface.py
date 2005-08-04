# -*- coding: utf-8 -*-
#
# Copyright (C) 2005, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

import socket
import struct

class ComarIface:
	"""A class for communicating with comard."""
	RESULT = 0
	FAIL = 1
	RESULT_START = 2
	RESULT_END = 3
	NOTIFY = 4
	__LOCALIZE = 5
	__REGISTER = 6
	__REMOVE = 7
	__CALL = 8
	
	def __init__(self):
		try:
			self.sock = socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
			self.sock.connect("/tmp/comar")
		except:
			# should raise an exception here
			print "Cannot connect to COMAR"
	
	def __pack(self, cmd, id, args):
		size = 0
		args2 = []
		# NOTE: COMAR RPC is using network byte order (big endian)
		fmt = "!ii"
		for a in args:
                        a = str(a) # damn unicode
			fmt += "h%dsB" % (len(a))
			size += 2 + len(a) + 1
			args2.append(len(a))
			args2.append(a.encode("utf-8"))
			args2.append(0)
		pak = struct.pack(fmt, (cmd << 24) | size, id, *args2)
		return pak
	
	def read_reply(self):
		pass
	
	def localize(self, localename):
		"""Sets the language for translated replies.
		
		Since comard has no way to detect caller's locale, this command
		is used for sending user's language to the comard. Afterwards,
		all the jobs started with API calls uses translated messages in
		their replies.
		
		You can get the localename parameter from setlocale(NULL) call.
		"""
		pass
	
	def register(self, classname, packagename, cslfile, id = 0):
		"""Registers a package script on the system model.
		"""
		pak = self.__pack(self.__REGISTER, id,
                                  [ classname, packagename, cslfile ]
		)
		self.sock.send(pak)
	
	def remove(self, packagename, id = 0):
		"""Remove package's all scripts from system.
		"""
		pak = self.__pack(self.__REMOVE, id, [ packagename ])
		self.sock.send(pak)
	
	def call(self, methodname, args, id = 0):
		"""Makes a configuration call on the system model.
		"""
		a = [ methodname ]
		a.extend(args)
		pak =self.__pack(self.__CALL, id, a)
		self.sock.send(pak)
	
	def call_package(self, methodname, packagename, args, id = 0):
		"""Makes a configuration call directed to a package.
		"""
		pass
	
	def call_instance(self, methodname, packagename, instancename, args, id = 0):
		# not yet decided
		pass
	
	def get_packages(self, classname, id = 0):
		"""Returns registered packages for a given system model class.
		"""
		pass
	
	def ask_notify(self, notifyname, id = 0):
		"""Asks for a notification event to be delivered.
		"""
		pass

comard = ComarIface()
