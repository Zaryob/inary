# -*- coding: utf-8 -*-
#
# Copyright (C) 2018, Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

"""diskutils module provides EDD class to query device boot order."""

import os
import struct
import binascii
import subprocess

sysfs_path = "/sys"

def sysValue(*paths):
    path = os.path.join(sysfs_path, *paths)
    f = open(path)
    data = f.read().rstrip("\n")
    f.close()
    return data

def idsQuery(name, vendor, device):
    f = file(name)
    flag = 0
    company = ""
    for line in f.readlines():
        if flag == 0:
            if line.startswith(vendor):
                flag = 1
                company = line[5:].strip()
        else:
            if line.startswith("\t"):
                if line.startswith("\t" + device):
                    return "{0} - {1}".format(line[6:].strip(), company)
            elif not line.startswith("#"):
                flag = 0
    if company != "":
        return "{0} ({1})".format(company, device)
    else:
        return "Unknown ({0}:{1})".format(vendor, device)

class EDD:
    def __init__(self):
        self.edd_dir = "/sys/firmware/edd"
        self.edd_offset = 440
        self.edd_len = 4

    def blockDevices(self):
        devices = []
        for sysfs_dev in [dev for dev in os.listdir("/sys/block") \
                if not dev.startswith(("fd", "loop", "ram", "sr"))]:
            dev_name = os.path.basename(sysfs_dev).replace("!", "/")
            devices.append("/dev/" + dev_name)

        devices.sort()
        return devices

    def match_sys(self, _a):
        b = struct.unpack("2s2s2s2s", _a)
        return "0x"+b[3]+b[2]+b[1]+b[0]

    def get_edd_sig(self, _n):
        sigfile = "{0}/int13_dev{1}/mbr_signature".format(self.edd_dir, _n)
        if os.path.exists(sigfile):
            sig = open(sigfile).read().strip("\n")
        else:
            sig = None

        return sig

    def get_mbr_sig(self, _f):
        f = open(_f)
        f.seek(self.edd_offset)
        a = f.read(self.edd_len)
        f.close()

        sig = self.match_sys(binascii.b2a_hex(a))
        return sig

    def list_edd_signatures(self):
        sigs = {}
        if os.path.exists(self.edd_dir):
            for d in os.listdir(self.edd_dir):
                bios_num = d[9:]
                sig = self.get_edd_sig(bios_num)
                if sig:
                    sigs[bios_num] = sig
        else:
            print("please insert edd module")
        return sigs

    def list_mbr_signatures(self):
        sigs = {}
        for d in self.blockDevices():
            try:
                sigs[self.get_mbr_sig(d)] = d
            except IOError:
                pass
        return sigs

def getDeviceMap():
    """
        Returns list of devices and their GRUB reprensentations.

        Returns:
            List of devices in ("hd0", "/dev/sda") format.
    """

    # edd module is required
    subprocess.call(["/sbin/modprobe", "edd"])

    # get signatures
    edd = EDD()
    mbr_list = edd.list_mbr_signatures()
    edd_list = edd.list_edd_signatures()

    # sort keys
    edd_keys = list(edd_list.keys())
    edd_keys.sort()

    devices = []

    # build device map
    i = 0
    for bios_num in edd_keys:
        edd_sig = edd_list[bios_num]
        if edd_sig in mbr_list:
            devices.append(("hd{}".format(i), mbr_list[edd_sig]))
            i += 1

    return devices

def parseLinuxDevice(device):
    """
        Parses Linux device address and returns disk, partition and their GRUB representations.

        Arguments:
            device: Linux device address (e.g. "/dev/sda1")
        Returns:
            None on error, (LinuxDisk, PartNo, GrubDev, GrubPartNo) on success
    """

    for grub_disk, linux_disk in getDeviceMap():
        if device.startswith(linux_disk):
            part = device.replace(linux_disk, "", 1)
            if part:
                # If device address ends with a number,
                # "p" is used before partition number
                if part.startswith("p"):
                    grub_part = int(part[1:]) - 1
                else:
                    grub_part = int(part) - 1
                return linux_disk, part, grub_disk, grub_part
    return None

def parseGrubDevice(device):
    """
        Parses GRUB device address and returns disk, partition and their Linux representations.

        Arguments:
            device: GRUB device address (e.g. "(hd0,0)")
        Returns:
            None on error, (GrubDev, GrubPartNo, LinuxDisk, PartNo) on success
    """

    try:
        disk, part = device.split(",")
    except ValueError:
        return None
    disk = disk[1:]
    part = part[:-1]
    if not part.isdigit():
        return None
    for grub_disk, linux_disk in getDeviceMap():
        if disk == grub_disk:
            linux_part = int(part) + 1
            # If device address ends with a number,
            # "p" is used before partition number
            if linux_disk[-1].isdigit():
                linux_part = "p{}".format(linux_part)
            return grub_disk, part, linux_disk, linux_part
    return None

def grubAddress(device):
    """
        Translates Linux device address to GRUB address.

        Arguments:
            device: Linux device address (e.g. "/dev/sda1")
        Returns:
            None on error, GRUB device on success
    """

    try:
        linux_disk, linux_part, grub_disk, grub_part = parseLinuxDevice(device)
    except (ValueError, TypeError):
        return None
    return "({0},{1})".format(grub_disk, grub_part)

def linuxAddress(device):
    """
        Translates GRUB device address to Linux address.

        Arguments:
            device: GRUB device address (e.g. "(hd0,0)")
        Returns:
            None on error, Linux device on success
    """

    try:
        grub_disk, grub_part, linux_disk, linux_part = parseGrubDevice(device)
    except (ValueError, TypeError):
        return None
    return "{0}{1}".format(linux_disk, linux_part)

def getDeviceByLabel(label):
    """
        Find Linux device address from it's label.

        Arguments:
            label: Device label
        Returns:
            None on error, Linux device on success
    """

    fn = os.path.join("/dev/disk/by-label/{}".format(label))
    if os.path.islink(fn):
        return "/dev/{}".format(os.readlink(fn)[6:])
    else:
        return None

def getDeviceByUUID(uuid):
    """
        Find Linux device address from it's UUID.

        Arguments:
            uuid: Device UUID
        Returns:
            None on error, Linux device on success
    """

    fn = os.path.join("/dev/disk/by-uuid/{}".format(uuid))
    if os.path.islink(fn):
        return "/dev/{}".format(os.readlink(fn)[6:])
    else:
        return None

def getDevice(path):
    """
        Gives device address of a path.

        Arguments:
            path: Directory path
        Returns:
            Device address (e.g. "/dev/sda1")
    """
    for mount in os.popen("/bin/mount").readlines():
        mount_items = mount.split()
        if mount_items[2] == path:
            if mount_items[0].startswith("/dev"):
                return mount_items[0]
            elif mount_items[0].startswith("LABEL="):
                return getDeviceByLabel(mount_items[0].split('=', 1)[1])
            elif mount_items[0].startswith("UUID="):
                return getDeviceByUUID(mount_items[0].split('=', 1)[1])

def getPartitions():
    """
        Returns list of all partitions.

        Returns:
            List of partitions which includes metadata of partition
            or None (if blkid not found) e.g.:

            {'/dev/sda1': {label  :'PARDUS_ROOT', # (if exists)
                           uuid   :'b3cf94b9-ed79-43e2-8b22-b9054a529f01',
                           fstype :'ext4'}, ... }
    """
    if not os.path.exists('/sbin/blkid'):
        return None

    cmd = os.popen('/sbin/blkid')
    result = {}
    try:
        for line in cmd.readlines():
            partition = line.split(':')[0]
            if partition not in result:
                result[partition] = {}
                for info in line.split():
                    if info.startswith('LABEL='):
                        result[partition]['label'] = info[6:].strip('"')
                    if info.startswith('UUID='):
                        result[partition]['uuid'] = info[5:].strip('"')
                    if info.startswith('TYPE='):
                        result[partition]['fstype'] = info[5:].strip('"')
    except:
        return None
    else:
        return result

def getRoot():
    """
        Gives current root device address.

        Returns:
            Device address (e.g. "/dev/sda1")
    """
    return getDevice("/")

def getBoot():
    """
        Gives current boot device address.

        Returns:
            Device address (e.g. "/dev/sda1")
    """
    if os.path.ismount("/boot"):
        return getDevice("/boot")
    else:
        return getRoot()
