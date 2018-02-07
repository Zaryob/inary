Inary Packet Yöneticisinin Kurulumu
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

* Portable Kurulumu: Herhangi başka bir yazılıma ihtiyaç duymadan inary ve python3'ün
  MacOS, Solaris ve benzeri sistemlerde tek tıkla kurulumuna olanak verir. Geriye
  kalan tüm özellikleri sınırlandırılmış kurulum ile aynıdır


.. note:: Inary paket yöneticisi herbir kurulum şekli için ayrı bir paket 
  deposu içerir. Kurulum şeklinize uygun depo kullanmanız önemle rica edilir.


Tam Kurulum
```````````

Eğer geliştirilen son sürümü kullanmak istiyorsanız
.. code-block:: shell

    git clone https://git.sulin.org/inary.git
    sudo python3 setup.py install
    inary-rebuild-system
    inary rdb

Eğer mevcut bulunan en kararlı sürümü kullanmak istiyorsanız
.. code-block:: shell

    wget https://sulin.org/inary/download/lastest.tar.gz
    tar xvf lastest.tar.gz
    cd inary/
    sudo python3 setup.py install
    inary-rebuild-system
    inary rdb

.. note:: setup.py scripti ile kurulum yaparken otomatik olarak
   tüm bağımlılıklar internet üzerinden indirilir.

Sınırlandırılmış kurulum
````````````````````````

Eğer geliştirilen son sürümü kullanmak istiyorsanız
.. code-block:: shell

    mkdir ~/.inary
    git clone https://git.sulin.org/inary.git
    python3 setup.py build
    python3 setup.py install --root=~/.inary
    inary rdb

Eğer mevcut bulunan en kararlı sürümü kullanmak istiyorsanız
.. code-block:: shell

    mkdir ~/.inary
    wget https://sulin.org/inary/download/lastest.tar.gz
    tar xvf lastest.tar.gz
    cd inary/
    python3 setup.py build
    python3 setup.py install --root=~/.inary
    inary rdb


Portable kurulum
````````````````

.. code-block:: shell

    wget https://sulin.org/inary/download/portable.tar.gz
    tar xvf portable.tar.gz
    mv portable ~/.inary
    inary rdb



Inary'i Güncelleştirmek
```````````````````````
Inary kullandığınız inary'i kullanarak güncelleştirmeye olanak verir.
.. code-block:: shell
    inary ur
    inary up inary


Scom Kullanmadan Paket İşlemi Yapmak
````````````````````````````````````
Inary paket yönetim sistemi eski pisi bağımlılığı olan ve pisi packet konfigurasyon
betiklerini içerisinde bulunduran comar sistemini forklayıp geliştirmiştir.
Ancak mevcut inary eskiden farklı olarak scom kullanmadan paket işlemi yapmaya
olanak verir. Ancak bu durumda paketlerin kurulumundan sonraki konfigurasyon 
tamamen kullanıcıya bırakılmıştır.


