.. -*- coding: utf-8 -*-

===========
inary build
===========

`inary build` komutu kaynak paketten ikili paket derlemesi için kullanılır. \
pspec.xml veya kaynak depo içerisindeki paket ismi verilerek derleme yapılır.


**Seçenekler**
--------------

build seçenekleri:

      -q, --quiet                     Ekstra hata ayıklama bilgilerini basmadan inşa operasyonunu çalıştır.
      --ignore-dependency             Bağımlılık bilgilerini dikkate alma.
      -O, --output-dir                Üretilen paketler için çıktı dizini.
      --ignore-action-errors          ActionsAPI kaynaklı hataları yoksay.
      --ignore-safety                 Emniyet mandalını yoksay.
      --ignore-check                  Test adımını yoksay.
      --create-static                 Statik bir paketi ar dosyalarıyla yarat.
      -F, --package-format            İkili paketi verilen biçimde oluştur. Desteklenen biçimlerin listesini görmek için '-F help' kullanın.
      --use-quilt                     GNU patch yerine quilt yama yönetim sistemini kullan.
      --ignore-sandbox                İnşa işlemini inşa klasörüyle sınırlama.


**Yardım Çıktısı**
------------------

.. code-block::shell

            $ inary build --help
            kullanım: Verilen INARY paket(ler)ini inşa et

            Kullanım: build [<pspec.xml> | <kaynakadı>] ...

            Yerel veya uzak bir adresteki pspec.xml dosyasının adresinin verilmesi
            yeterlidir, INARY gerekli dosyaları indirip paketi inşa edecektir.

            Kaynak depo kullanıyorsanız, doğrudan kaynak depoda bulunan bir
            paketin adını vererek INARY'nin o paketi inşa etmesini sağlayabilirsiniz.


            Seçenekler:
             --version                    : programın sürüm numarasını göster ve çık
             -h [--help]                  : bu yardım iletisini göster ve çık

             inşa seçenekleri:
              -q [--quiet]                : Ekstra hata ayıklama bilgilerini basmadan inşa
                                            operasyonunu çalıştır.
              --ignore-dependency         : Bağımlılık bilgilerini dikkate alma.
              -O [--output-dir] arg       : Üretilen paketler için çıktı dizini.
              --ignore-action-errors      : ActionsAPI kaynaklı hataları yoksay.
              --ignore-safety             : Emniyet mandalını yoksay.
              --ignore-check              : Test adımını yoksay.
              --create-static             : Statik bir paketi ar dosyalarıyla yarat.
              -F [--package-format] arg   : İkili paketi verilen biçimde oluştur.
                                            Desteklenen biçimlerin listesini görmek için '-F
                                            help' kullanın.
              --use-quilt                 : GNU patch yerine quilt yama yönetim sistemini
                                            kullan.
              --ignore-sandbox            : İnşa işlemini inşa klasörüyle sınırlama.

             inşa adımları:
              --fetch                     : Kaynak arşivi indirdikten sonra inşayı
                                            sonlandır.
              --unpack                    : Kaynak arşivini açtıktan, sha1sum denetimi
                                            yaptıktan ve yamaları uyguladıktan sonra inşayı
                                            sonlandır.
              --setup                     : Yapılandırma adımından sonra inşayı sonlandır.
              --build                     : Derleme adımından sonra inşayı sonlandır.
              --check                     : Test adımından sonra inşayı sonlandır.
              --install                   : Kurulum adımından sonra inşayı sonlandır.
              --package                   : INARY paketi oluştur.

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

        $ inary build
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
        *** 0 hata, 1 uyarı
