.. -*- coding: utf-8 -*-

===================================
Inary Paket Yöneticisinin Kurulumu
===================================

Inary paket yöneticisi üç farklı şekilde kurulabilir:

* Tam Kurulum: Sistemde tek başına bütün paket işlerini inary yapar ve sistemde
  bulunan tüm paketleri analiz edip mevcut kuruluma dokunmadan tüm kurulu
  uygulamalarınızı otomatik olarak inary veritabanına işler. Tercihe bağlı olarak
  diğer paket yönetim yazılımlarını siler.


* Sınırlandırılmış Kurulum: Kurulum yapılan kullanıcının kendi home dizini altında
  inary paketlerini kurup kaldırmasına olanak tanıyan bir kurulum çeşitidir.
  Sınırlandırılmış kurulumda sistemde mevcut başka bir paket yönerim yazılımı var
  ise dokunmaz, hiçbir dosya işlemi kök dizin altında yapılmaz ve inary ile yapılan
  tüm işler '~/.inary' dizini silinerek yok edilebilir.

Tam Kurulum
```````````

Eğer geliştirilen son sürümü sisteminizde paket yöneticisi olarak kullanmak istiyorsanız

.. code-block:: shell

    $ git clone https://git.sulin.org/inary.git
    $ sudo python3 setup.py install
    $ inary-rebuild-system
    $ inary rdb

Eğer mevcut bulunan en kararlı sürümü kullanmak istiyorsanız

.. code-block:: shell

    $ wget https://sulin.org/inary/download/lastest.tar.gz
    $ tar xvf lastest.tar.gz
    $ cd inary/
    $ sudo python3 setup.py install
    $ inary-rebuild-system
    $ inary rdb



.. note:: setup.py :term:`betik`i ile kurulum yaparken otomatik olarak  tüm bağımlılıklar internet üzerinden indirilir.


Sınırlandırılmış kurulum
````````````````````````

Eğer geliştirilen son sürümü kullanmak istiyorsanız

.. code-block:: shell

    $ mkdir ~/.inary
    $ git clone https://git.sulin.org/inary.git
    $ python3 setup.py build
    $ python3 setup.py install --root=~/.inary
    $ inary rdb

Eğer mevcut bulunan en kararlı sürümü kullanmak istiyorsanız

.. code-block:: shell

    $ mkdir ~/.inary
    $ wget https://sulin.org/inary/download/lastest.tar.gz
    $ tar xvf lastest.tar.gz
    $ cd inary/
    $ python3 setup.py build
    $ python3 setup.py install --root=~/.inary
    $ inary rdb


Inary'i Güncelleştirmek
```````````````````````
Inary kullandığınız inary'i kullanarak güncelleştirmeye olanak verir.

.. code-block:: shell

    $ inary ur
    $ inary up inary


Scom Kullanmadan Paket İşlemi Yapmak
````````````````````````````````````
Inary paket yönetim sistemi eski inary bağımlılığı olan ve pisi paket konfigurasyon
:term:`betik`'lerini içerisinde bulunduran comar sistemini forklayıp geliştirmiştir.
Ancak mevcut inary eskiden farklı olarak scom kullanmadan paket işlemi yapmaya
olanak verir. Ancak bu durumda paketlerin kurulumundan sonraki konfigurasyon
tamamen kullanıcıya bırakılmıştır.
