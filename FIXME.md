2018-03-17 Suleyman POYRAZ <nipalensisaquila@gmail.com>
    * inary.fetcher.py: --- status: not fixed; flag: critical ---:
    Neden local dosyaları çekmiyor bu?
    """
    $ inary fc dbus
    dbus package found in binrepo repository
    Error: Program terminated.
    Error: A problem occurred. Please check the archive address and/or permissions again. Could not fetch destination file: "/home/zaryob/Repositories/binrepo/d/dbus/dbus-1.11.8-1-s18-x86_64.inary"
    Raised Value error: "unknown url type: '/home/zaryob/Repositories/binrepo/d/dbus/dbus-1.11.8-1-s18-x86_64.inary'"
    Please use 'inary help' for general help.
    """

    * ayrıca yine fetcher:
    sudo inary it dbus -f diyince nereye indiriyor yaw bu 


2018-03-17 Suleyman POYRAZ <nipalensisaquila@gmail.com>
    * inary.db.installdb.py: --- status: fixed; flag: critical ---:
    -> Programcı Hatası
    Şu satır bir kontrol edilmeli:

2018-03-17 Suleyman POYRAZ <nipalensisaquila@gmail.com>
    * inary searchfile command: --- status: fixed; flag: critical ---:
    -> filesdb modulune dayalı bir hata tespit edildi.


2018-01-26 Suleyman POYRAZ <nipalensisaquila@gmail.com>
  * inary/db/filesdb.py: --- status: fixed; flag: critical ---:
    -> Pylvel yerine shelve kullanarak fixe edildi
    plyvel yerine shelve kullanarak fixe edildi
    Bir hata var bu leveldb içinde, çokça kullanmaya çalışınca kafayı yiyor



2018-01-26 Suleyman POYRAZ <nipalensisaquila@gmail.com>

    * inary/sxml/xmlext --- status: fixed; flag: cosmetical ---:
    -> Minidom kullanarak fixe edildi
    -> Ciksemel için gzip modulu kullanımındaki hata fixe edildi.
    xmlext modulunde bulunan getNodeText olayinda ciktilar utf-8 ile
    decode edilmeli. Yoksa Localtext ve Text type veriler ile ilgili sorun
    cıkıyor
     '\xc3\xb6':
    şimdi olay şu yandaki bytes olarak encode edilmiş bir ö harfi.
    bu harfi öldürsen string içerisine bu hali ile ALAMAZSIN.
    ama nasil olmuşsa ö ve bütün Türkçe karakterler bu şekilde
    girmiş xmlden alinan veriler içerisine


2018-01-14 Suleyman POYRAZ <nipalensisaquila@gmail.com>
    * inary/atomicoperations.py --- status: not fixed flag: critical ---
    In removing not asking "Do you want remove conflicted files "
    Now remove all package files and conflicted files
