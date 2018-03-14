2018-03-17 Suleyman POYRAZ <nipalensisaquila@gmail.com>
    * inary.fetcher.py:
    Neden local dosyaları çekmiyor bu?
    """
    $ inary fc dbus 
    dbus package found in binrepo repository
    Error: Program terminated.
    Error: A problem occurred. Please check the archive address and/or permissions again. Could not fetch destination file: "/home/zaryob/Repositories/binrepo/d/dbus/dbus-1.11.8-1-s18-x86_64.inary" 
    Raised Value error: "unknown url type: '/home/zaryob/Repositories/binrepo/d/dbus/dbus-1.11.8-1-s18-x86_64.inary'"
    Please use 'inary help' for general help.
    """


2018-03-17 Suleyman POYRAZ <nipalensisaquila@gmail.com>
    * inary.db.installdb.py:
    Şu satır bir kontrol edilmeli:

    """
    DEBUG: InstallDB initialized in 0.0029578208923339844.
    File "/bin/inary-cli", line 82, in <module>
      cli.run_command()
    File "/usr/lib/python3.6/site-packages/inary/cli/inarycli.py", line 144, in run_command
      self.command.run()
    File "/usr/lib/python3.6/site-packages/inary/cli/listupgrades.py", line 52, in run
      upgradable_pkgs = op_wrappers.list_upgradable()
    File "/usr/lib/python3.6/site-packages/inary/operations/op_wrappers.py", line 119, in list_upgradable
      upgradable = list(filter(is_upgradable, installdb.list_installed()))
    File "/usr/lib/python3.6/site-packages/inary/operations/upgrade.py", line 402, in is_upgradable
      (i_version, i_release, i_build, i_distro, i_distro_release) = installdb.get_version_and_distro_release(name)
    File "/usr/lib/python3.6/site-packages/inary/db/installdb.py", line 173, in get_version_and_distro_release
      return self.__get_version(meta_doc) + self.__get_distro_release(meta_doc)
    File "/usr/lib/python3.6/site-packages/inary/db/installdb.py", line 151, in __get_version
      version = history.getElementsByTagName("Update")[0].getElementsByTagName("Version")[0].firstChild.data

    Error: System error. Program terminated.
    Error: <class 'AttributeError'>: 'str' object has no attribute 'getElementsByTagName'
    Please use 'inary help' for general help.
    """

2018-03-17 Suleyman POYRAZ <nipalensisaquila@gmail.com>
    * inary.fetcher.py:
    Traceback:
    Program terminated.
    You have to be root for this operation.
    Please use 'inary help' for general help.




2018-01-26 Suleyman POYRAZ <nipalensisaquila@gmail.com>
  * inary/db/filesdb.py:
    Bir hata var bu leveldb içinde, çokça kullanmaya çalışınca kafayı yiyor

```Traceback (most recent call last):
  File "checkelf", line 89, in check_objdump
    dependency_name = inary.api.search_file(objdump_needed)[0][0]
  File "/usr/local/lib/python3.5/dist-packages/inary/api.py", line 306, in search_file
    ctx.filesdb = inary.db.filesdb.FilesDB()
  File "/usr/local/lib/python3.5/dist-packages/inary/db/filesdb.py", line 31, in __init__
    self.filesdb = plyvel.DB(self.files_ldb_path, create_if_missing=True)
  File "_plyvel.pyx", line 236, in plyvel._plyvel.DB.__init__ (plyvel/_plyvel.cpp:3129)
  File "_plyvel.pyx", line 80, in plyvel._plyvel.raise_for_status (plyvel/_plyvel.cpp:1698)
plyvel._plyvel.IOError: b'IO error: lock /var/lib/inary/info/files.ldb/LOCK: already held by process'
Exception ignored in: <bound method FilesDB.__del__ of <inary.db.filesdb.FilesDB object at 0x7f5b46c8ed68>>
Traceback (most recent call last):
  File "/usr/local/lib/python3.5/dist-packages/inary/db/filesdb.py", line 37, in __del__
    self.close()
  File "/usr/local/lib/python3.5/dist-packages/inary/db/filesdb.py", line 82, in close
    self.filesdb.close()
AttributeError: 'FilesDB' object has no attribute 'filesdb'
```



2018-01-26 Suleyman POYRAZ <nipalensisaquila@gmail.com>

    * inary/sxml/xmlext --- status: not fixed; flag: cosmetical ---:
    xmlext modulunde bulunan getNodeText olayinda ciktilar utf-8 ile
    decode edilmeli. Yoksa Localtext ve Text type veriler ile ilgili sorun
    cıkıyor

    * '\xc3\xb6':
    şimdi olay şu yandaki bytes olarak encode edilmiş bir ö harfi.
    bu harfi öldürsen string içerisine bu hali ile ALAMAZSIN.
    ama nasil olmuşsa ö ve bütün Türkçe karakterler bu şekilde
    girmiş xmlden alinan veriler içerisine


2018-01-14 Suleyman POYRAZ <nipalensisaquila@gmail.com>
    * inary/atomicoperations.py --- status: not fixed flag: critical ---
    In removing not asking "Do you want remove conflicted files "
    Now remove all package files and conflicted files


