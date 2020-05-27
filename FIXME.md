2019 - 01 - 08 Suleyman POYRAZ < zaryob.dev @ gmail.com >
   * dependency error - -status: not fixed; flag: critical - --:
   -> çalışma sırasında dependencylere göre paketler kurulum sıralamasına sokulmadığı içinde
   error veriyor sonuç olarak kurulumun ortasında hata yiyoruz. Önceden beri var olan bu hata giderilmeli.

2018 - 05 - 05 Suleyman POYRAZ < zaryob.dev @ gmail.com >
    * inary.data.pgraph.py - -status: fixed; flag: critical - --:
    ->inary kurulum için mevcut dizin olarak farklı bir yer kulllanılınca pgraph.Digraph()
    sınıfındaki dfs fonksiyonlarından KeyError yükseliyor.

2018 - 03 - 17 Suleyman POYRAZ < zaryob.dev @ gmail.com >
    * inary.fetcher.py: --- status: fixed; flag: critical - --:
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
