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
    * ciksemel.data() fonksiyonu:
    Acaba o acaip geri donutler bununla alakali olabilir mi??


2018-01-14 Suleyman POYRAZ <nipalensisaquila@gmail.com>
    * inary/atomicoperations.py --- status: not fixed flag: critical ---
    In removing not asking "Do you want remove conflicted files "
    Now remove all package files and conflicted files

