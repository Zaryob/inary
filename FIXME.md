2018-05-05 Suleyman POYRAZ <zaryob.dev@gmail.com>
    * inary.data.pgraph.py --status: not fixed; flag: critical ---:
    ->inary kurulum için mevcut dizin olarak farklı bir yer kulllanılınca pgraph.Digraph()
    sınıfındaki dfs fonksiyonlarından KeyError yükseliyor.
    ```
    Traceback (most recent call last):
    File "/home/zaryob/Developing/Sulin/inary/tests/packageTests/testDependency.py", line 30, in testRepoSatisfiesDependency
    inary.api.install(["uif2iso"])
    File "/usr/local/lib/python3.5/dist-packages/inary/atomicoperations.py", line 742, in wrapper
      ret = func(*__args,**__kw)
    File "/usr/local/lib/python3.5/dist-packages/inary/atomicoperations.py", line 796, in install
      return inary.operations.install.install_pkg_names(packages, reinstall)
    File "/usr/local/lib/python3.5/dist-packages/inary/operations/install.py", line 58, in install_pkg_names
      A |= operations.upgrade.upgrade_base(A)
    File "/usr/local/lib/python3.5/dist-packages/inary/operations/upgrade.py", line 369, in upgrade_base
      G_f, install_order = operations.install.plan_install_pkg_names(extra_installs)
    File "/usr/local/lib/python3.5/dist-packages/inary/operations/install.py", line 302, in plan_install_pkg_names
      order = G_f.topological_sort()
    File "/usr/local/lib/python3.5/dist-packages/inary/data/pgraph.py", line 140, in topological_sort
      self.dfs(lambda u: list.append(u))
    File "/usr/local/lib/python3.5/dist-packages/inary/data/pgraph.py", line 107, in dfs
      if self.color[u] == 'w':
    KeyError: 'libidn'
    ```
    bu koddaki gibi


2018-03-17 Suleyman POYRAZ <zaryob.dev@gmail.com>
    * inary.fetcher.py: --- status: fixed; flag: critical ---:
    ->Ufak bir sihirli dokunuş düzeltmeye yetti.
    Neden local dosyaları çekmiyor bu?
    """
    $ inary fc dbus
    dbus package found in binrepo repository

    * ayrıca yine fetcher:
    -> local dosyalar indirilmiyor. Olduğu yerin path bilgisi alınıp kuruluyor
    Oldukça temiz bir bakış açısı
    sudo inary it dbus -f diyince nereye indiriyor yaw bu


2018-03-17 Suleyman POYRAZ <zaryob.dev@gmail.com>
    * inary.db.installdb.py: --- status: fixed; flag: critical ---:
    -> Programcı Hatası
    Şu satır bir kontrol edilmeli:

2018-03-17 Suleyman POYRAZ <zaryob.dev@gmail.com>
    * inary searchfile command: --- status: fixed; flag: critical ---:
    -> filesdb modulune dayalı bir hata tespit edildi.


2018-01-26 Suleyman POYRAZ <zaryob.dev@gmail.com>
  * inary/db/filesdb.py: --- status: fixed; flag: critical ---:
    -> Pylvel yerine shelve kullanarak fixe edildi
    plyvel yerine shelve kullanarak fixe edildi
    Bir hata var bu leveldb içinde, çokça kullanmaya çalışınca kafayı yiyor



2018-01-26 Suleyman POYRAZ <zaryob.dev@gmail.com>

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


2018-01-14 Suleyman POYRAZ <zaryob.dev@gmail.com>
    * inary/atomicoperations.py --- status: fixed flag: critical ---
    -> Dosya veritabanına bağlı hata düzeltildi.
    In removing not asking "Do you want remove conflicted files "
    Now remove all package files and conflicted files
