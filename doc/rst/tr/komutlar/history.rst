.. -*- coding: utf-8 -*-

=============
inary history
=============



`inary history` komutu geçmişteki yapılan komutları listelememizi, belirli bir \
zamandan sonra yapılan değişimleri geri almamızı, sistem geri yükleme noktası \
oluşturmamızı sağlar.


**Yardım Çıktısı**
------------------

.. code-block:: shell

            $ inary history --help
            kullanım: INARY işlemlerinin günlüğü

            Kullanım: history

            Önceki işlemleri listeler.

            Seçenekler:
             --version                    : programın sürüm numarasını göster ve çık
             -h [--help]                  : bu yardım iletisini göster ve çık

             history seçenekleri:
              -l [--last] arg             : Sadece son 'n' adet operasyonu göster.
              -s [--snapshot]             : Güncel sistemin görüntüsünü al.
              -t [--takeback] arg         : Verilen operasyon tamamlandıktan sonraki duruma
                                            geri dön.

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

            $ inary history
            İşlem #4: depo güncellemesi:
            Tarih: 2019-08-20 19:19
                * core deposu güncellendi.

            İşlem #3: kur:
            Tarih: 2019-08-20 21:41
                * gperftools-devel 2.7-1-s19-x86_64 kuruldu.
                * yasm 1.3.0-1-s19-x86_64 kuruldu.
                * yasm-devel 1.3.0-1-s19-x86_64 kuruldu.

            İşlem #2: kur:
            Tarih: 2019-08-20 21:38
                * libgcc 8.2.0-1-s19-x86_64 kuruldu.
                * libffi 3.2.1-1-s19-x86_64 kuruldu.
                * ncurses 6.1-1-s19-x86_64 kuruldu.

            İşlem #1: depo güncellemesi:
            Tarih: 2019-08-20 21:37
                * core deposu güncellendi.
