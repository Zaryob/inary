.. -*- coding: utf-8 -*-

================
inary rebuild-db
================

`inary rebuild-db` komutu inary paket sistemine ait veritabanı \
dosyalarının düzenlenip yeniden oluşturulmasını sağlar


**Yardım Çıktısı**
------------------

.. code-block:: shell

            $ inary rebuild-db --help
            kullanım: Veritabanlarını Yeniden İnşa Et

            Kullanım: rebuild-db [ <paket1> <paket2> ... <paketn> ]

            INARY veritabanlarını yeniden inşa eder

            Eğer paket belirtimleri verilirse, /var/lib/inary altındaki
            dizinlerin adları olmalıdir.


            Seçenekler:
             --version                    : programın sürüm numarasını göster ve çık
             -h [--help]                  : bu yardım iletisini göster ve çık

             rebuild-db seçenekleri:
              -f [--files]                : Dosya veritabanını yeniden inşa et

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
            inary rebuild-db
            INARY veritabanı yeniden inşa edilsin mi? (evet/hayır):  yes
            Dosya veritabanını yeniden inşa ediliyor...
             -> "libobjc" veritabanına ekleniyor...
            Dosyalar veritabanına eklendi...
