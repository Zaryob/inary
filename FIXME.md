2018-01-26 Suleyman POYRAZ <nipalensisaquila@gmail.com>
  * inary/db/filesdb.py:
    Bir hata var bu leveldb içinde, çokça kullanmaya çalışınca kafayı yiyor

```Traceback (most recent call last):
  File "checkelf", line 89, in check_objdump
    dependency_name = inary.api.search_file(objdump_needed)[0][0]
  File "/usr/local/lib/python3.5/dist-packages/inary/reactor.py", line 306, in search_file
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

