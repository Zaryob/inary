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

"""/etc/fstab parser facility."""

import os
import subprocess

REMOTE_FS_LIST = [
                    "nfs",
                    "nfs4",
                    "cifs",
                    "ncpfs",
                 ]

def get_device_by_label(label):
    """Returns the devpath associated with the given label."""
    devpath = os.path.join("/dev/disk/by-label", label)
    device = None
    try:
        device = os.path.basename(os.readlink(devpath))
    except OSError:
        pass
    else:
        return os.path.join("/dev", device)

def get_device_by_uuid(uuid):
    """Returns the devpath associated with the given UUID."""
    devpath = os.path.join("/dev/disk/by-uuid", uuid)
    device = None
    try:
        device = os.path.basename(os.readlink(devpath))
    except OSError:
        pass
    else:
        return os.path.join("/dev", device)


class FstabEntry(object):
    """Class representing an fstab entry."""
    def __init__(self, entry):
        """
        fs: First field in fstab file which determines either the device or
        special filesystems like proc, sysfs, debugfs, etc.
        mountpoint: The mountpoint to which the fs will be mounted.
        type: Filesystem type. Can be none, ignore or VFSTYPE.
        opts: Extra options to pass to the mount helper.
        dump: Defines whether the filesystem will be dumped, optional field.
        fsck: Defines whether the filesystem will be fsck'ed regularly.
        """

        fields = entry.strip().split()

        # If number of fields is < 6, either fs_freq or fs_passno is
        # not given. So we omit them first
        self.__fs_freq = None
        self.__fs_passno = None

        self.__fs_spec = fields[0]
        self.__fs_file = fields[1]
        self.__fs_vfstype = fields[2]
        self.__fs_mntopts = fields[3]

        if len(fields) == 6:
            self.__fs_freq = fields[4]
            self.__fs_passno = fields[5]

        self.__volume_label = None
        self.__volume_uuid = None
        self.__device = None

        # Entry properties
        self.__is_swap = self.__fs_vfstype == "swap"
        self.__entry_ignored = self.__fs_vfstype == "ignore"
        self.__bind_move_mount = self.__fs_vfstype == "none"

        if self.__fs_spec.startswith("UUID="):
            self.__volume_uuid = self.__fs_spec.split("=")[-1]
            self.__device = get_device_by_uuid(self.__volume_uuid)

        if self.__fs_spec.startswith("LABEL="):
            self.__volume_label = self.__fs_spec.split("=")[-1]
            self.__device = get_device_by_label(self.__volume_label)

    def __str__(self):
        return """\
fs_spec: {0}
fs_file: {1}
fs_vfstype: {2}
fs_mntopts: {3}
fs_freq: {4}
fs_passno: {5}
""".format(self.__fs_spec,
                    self.__fs_file,
                    self.__fs_vfstype,
                    self.__fs_mntopts,
                    self.__fs_freq,
                    self.__fs_passno)

    def get_mount_command(self):
        """Returns the UNIX command line for mounting this entry."""
        cmd = ["/bin/mount"]

        # Append vfs type
        #cmd.append("-t %s" % self.get_fs_vfstype())

        # Append mount options
        #cmd.append("-o %s" % self.get_fs_mntopts())

        #cmd.append(self.get_fs_spec())
        cmd.append(self.get_fs_file())

        return cmd

    def get_umount_command(self):
        """Returns the UNIX command line for unmounting this entry."""
        cmd = ["/bin/umount"]
        cmd.append(self.get_fs_file())

        return cmd

    def mount(self):
        """Mounts the given entry if not mounted."""
        if not self.is_mounted():
            return subprocess.call(self.get_mount_command())

    def unmount(self):
        """Unmounts the given entry if mounted."""
        if self.is_mounted():
            return subprocess.call(self.get_umount_command())

    def get_volume_label(self):
        """Returns the volume label."""
        return self.__volume_label

    def get_volume_uuid(self):
        """Returns the volume UUID."""
        return self.__volume_uuid

    def get_device_path(self):
        """Returns /dev/path path for the given entry."""
        return self.__device

    def get_fs_spec(self):
        """Returns the first field (fs_spec) of the entry."""
        return self.__fs_spec

    def get_fs_file(self):
        """Returns the second field (fs_file) of the entry."""
        return self.__fs_file

    def get_fs_vfstype(self):
        """Returns the third field (fs_vfstype) of the entry."""
        return self.__fs_vfstype

    def get_fs_mntopts(self, split=False):
        """Returns the fourth field (fs_mntopts) of the entry."""
        opts = self.__fs_mntopts
        if split:
            opts = opts.split(",")
        return opts

    def get_fs_freq(self):
        """Returns the fifth field (fs_freq) of the entry."""
        return self.__fs_freq

    def get_fs_passno(self):
        """Returns the sixth field (fs_passno) of the entry."""
        return self.__fs_passno

    def has_mount_option(self, opt):
        """Checks whether the given option exists in fs_mntops."""
        return opt in self.get_fs_mntopts(split=True)

    def is_swap_entry(self):
        """Returns True if the entry corresponds to a swap area."""
        return self.__is_swap

    def is_rootfs(self):
        """Returns True if the entry corresponds to /."""
        return self.__fs_file == "/"

    def is_ignored(self):
        """Returns True if the entry should be ignored."""
        return self.__entry_ignored

    def is_remote_mount(self):
        """Returns True if the entry corresponds to a remote mount."""
        return self.get_fs_vfstype() in REMOTE_FS_LIST

    def is_nfs(self):
        """Returns True if the entry corresponds to NFS or NFS4."""
        return self.get_fs_vfstype() in ("nfs", "nfs4")

    def is_mounted(self):
        """Returns True if the entry is currently mounted."""
        # Always parse /proc/mounts for maximum atomicity
        for mount in open("/proc/mounts", "r").read().strip().split("\n"):
            if mount.split()[1] == self.__fs_file:
                return True
        return False


class Fstab(object):
    """Class representing an fstab file."""
    def __init__(self, _fstab="/etc/fstab"):
        """Parses fstab file given as the first parameter."""
        self.fstab_file = _fstab
        self.__entries = []

        with open(self.fstab_file, "r") as fstab_entries:
            for entry in fstab_entries:
                if entry.strip() and not entry.startswith("#"):
                    self.__entries.append(FstabEntry(entry))

    def get_entries(self):
        """Returns fstab entries in a list."""
        return self.__entries

    def contains_remote_mounts(self):
        """Returns True if the fstab file contains remote mounts."""
        for entry in self.get_entries():
            if entry.is_remote_mount():
                return True
        return False

    def mount_file_systems_with_type(self, vfs_types):
        """Mounts all file systems having a
           vfstype in [vfs_types] if not mounted."""
        for entry in self.get_entries():
            if not entry.is_mounted() and entry.get_fs_vfstype() in vfs_types:
                entry.mount()

    def unmount_file_systems_with_type(self, vfs_types):
        """Unmounts all file systems having a
           vfstype in [vfs_types] if mounted."""
        for entry in self.get_entries():
            if entry.is_mounted() and entry.get_fs_vfstype() in vfs_types:
                entry.unmount()
