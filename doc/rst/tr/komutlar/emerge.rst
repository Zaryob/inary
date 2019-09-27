.. -*- coding: utf-8 -*-

============
inary emerge
============



`inary emerge` komutu kaynak depodan kaynak paket inşa edip ikili paket olarak \
sisteme kurmak için kullanılır.kaynak depo içerisindeki paket ismi verilerek kurulum yapılır.

**Yardım Çıktısı**
------------------

.. code-block:: shell

            $ inary emerge --help
            emerge (em): INARY kaynak paketlerini depodan inşa et ve kur

            Kullanım: emerge <kaynakismi> ...

            Bir kaynak depodan indirilecek kaynak paketin ismini
            vermelisiniz.

            Bir bileşen adı da verebilirsiniz.

            Seçenekler:
             --version                    : programın sürüm numarasını göster ve çık
             -h [--help]                  : bu yardım iletisini göster ve çık

             emerge seçenekleri:
              -c [--component] arg        : Bileşen altındaki paketleri derleyip kur
              --ignore-file-conflicts     : Dosya çakışmalarını gözardı et.
              --ignore-package-conflicts  : Paket çakışmalarını gözardı et.
              --ignore-scom               : Scom yapılandırma yöneticisini es geç.

             genel seçenekler:
              -D [--destdir] arg          : INARY komutları için sistem kökü dizinini
                                            değiştir.
              -y [--yes-all]              : Bütün evet/hayır sorularında cevabı evet kabul
                                            et.
              -u [--username] arg
              -p [--password] arg
              -L [--bandwidth-limit] arg  : Bant genişliği kullanımını belirtilen kilobaytın
                                            altında tut.
              -v [--verbose]              : Detaylı çıktı
              -d [--debug]                : Hata ayıklama bilgisini göster.
              -N [--no-color]             : INARY çıktılarında renk kullanılmasını engeller.

**Örnek bir çalışma çıktısı**
-----------------------------

.. code-block:: shell

        $ inary emerge expat
        İkili paketler paket önbelleğine yazılıyor.
        Kaynak paket inşa ediliyor: "expat"
        expat-2.2.6.tar.bz2 [önbellekte]
        >>> Arşiv(ler) açılıyor...
         -> (/var/inary/expat-2.2.6-1/work) açıldı
        >>> Kaynak yapılandırılıyor...
        GNU Yapılandırma Güncellemesi Bitti.
        GNU Yapılandırma Güncellemesi Bitti.
        [Running Command]: ./configure                 --prefix=/usr                 --build=x86_64-pc-linux-gnu                 --mandir=/usr/share/man                 --infodir=/usr/share/info                 --datadir=/usr/share                 --sysconfdir=/etc                 --localstatedir=/var                 --libexecdir=/usr/libexec                 --disable-static
        >>> Kaynak inşa ediliyor...
        [Running Command]: make -j5
        >>> Kuruluyor...
        [Running Command]: make DESTDIR=/var/inary/expat-2.2.6-1/install man1dir=/usr/share/man/man1 install
        [Running Command]: install -m 0644 "doc/expat.png" /var/inary/expat-2.2.6-1/install/usr/share/doc/expat/html
        [Running Command]: install -m 0644 "doc/valid-xhtml10.png" /var/inary/expat-2.2.6-1/install/usr/share/doc/expat/html
        [Running Command]: install -m 0644 "doc/reference.html" /var/inary/expat-2.2.6-1/install/usr/share/doc/expat/html
        [Running Command]: install -m 0644 "doc/style.css" /var/inary/expat-2.2.6-1/install/usr/share/doc/expat/html
        [Running Command]: install -m 0644 "Changes" /var/inary/expat-2.2.6-1/install/usr/share/doc/expat
        [Running Command]: install -m 0644 "README.md" /var/inary/expat-2.2.6-1/install/usr/share/doc/expat
        Özel dosya "libtool",  "/var/inary/expat-2.2.6-1/install/usr/lib/libexpat.la" için siliniyor...
        Paket inşa ediliyor: "expat"
        "expat-2.2.6-1-s19-x86_64.inary" oluşturuluyor...
        Paket inşa ediliyor: "expat-devel"
        "expat-devel-2.2.6-1-s19-x86_64.inary" oluşturuluyor...
        Paket inşa ediliyor: "expat-docs"
        "expat-docs-2.2.6-1-s19-x86_64.inary" oluşturuluyor...
        Paket inşa ediliyor: "expat-pages"
        "expat-pages-2.2.6-1-s19-x86_64.inary" oluşturuluyor...
        İnşa dizini bırakılıyor
        "expat" paketi 2.2.6 sürümü 1 yayımı kuruluyor
        "expat" dosyaları arşivden çıkartılıyor.
        "expat" paketinin dosya/dizin bilgileri veritabanına ekleniyor...
        "expat" kuruldu.
