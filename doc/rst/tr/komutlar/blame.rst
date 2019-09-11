.. -*- coding: utf-8 -*-

===========
inary blame
===========

`inary blame` komutu bir pakete air paket bakıcısı, paket sürüm bilgisini \
ve güncelleme mesajını getirmek için kullanılır.

**Yardım Çıktısı**
------------------

.. code-block:: shell

            $ inary blame --help
            blame (bl): Paket sahibi ve yayım bilgisi

            Kullanım: blame <paket> ... <paket>


            Seçenekler:
             --version                    : programın sürüm numarasını göster ve çık
             -h [--help]                  : bu yardım iletisini göster ve çık

             blame seçenekleri:
              -r [--release] arg          : Verilen sürüm için paket bakıcısı
              -a [--all]                  : Tüm sürümler için paket bakıcısı

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

            $ inary blame expat
            İsim: expat, sürüm: 2.2.6, yayım: 1
            Paket Bakıcısı: Süleyman POYRAZ <zaryob.dev@gmail.com>
            Yayım Güncelleyen: Süleyman POYRAZ <zaryob.dev@gmail.com>
            Güncelleme Tarihi: 2018-12-23

            First release

