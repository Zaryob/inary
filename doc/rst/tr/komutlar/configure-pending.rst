.. -*- coding: utf-8 -*-

=======================
inary configure-pending
=======================




`inary configure-pending` sisteme kurulmuş ama kurulum sonrası betikleri işlememiş
paketlerin kurulum sonrası betiklerini tamamlamak için kullanılır.


**Yardım Çıktısı**
------------------
.. code-block:: shell

        $ inary configure-pending --help
        Kullanım: Kalan paketleri yapılandır

        Eğer kurulum sırasında bazı paketlerin SCOM yapılandırması
        atlandıysa, o paketler yapılandırılmayı bekleyen paketler
        listesine eklenir. Bu komut o paketleri yapılandırır.


        Seçenekler:
         --version                    : programın sürüm numarasını göster ve çık
         -h [--help]                  : bu yardım iletisini göster ve çık

         configure-pending seçenekleri:
          --ignore-dependency         : Bağımlılık bilgilerini dikkate alma.
          --ignore-safety             : Emniyet mandalını yoksay.
          --ignore-scom               : Bypass scom configuration agent
          -n [--dry-run]              : Hiçbir eylem gerçekleştirme, sadece neler
                                        yapılacağını göster.

         genel seçenekler:
          -D [--destdir] arg          : INARY komutları için sistem kökünü değiştir.
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

        $ sudo inary configure-pending acl bash unzip gcc binutils tar
        "acl" yapılandırılıyor.
        "acl" paketi yapılandırılıyor.
        "acl" yapılandırıldı.
        "bash" yapılandırılıyor.
        "bash" paketi yapılandırılıyor.
        "bash" yapılandırıldı.
        "unzip" yapılandırılıyor.
        "unzip" paketi yapılandırılıyor.
        "unzip" yapılandırıldı.
        "tar" yapılandırılıyor.
        "tar" paketi yapılandırılıyor.
        "tar" yapılandırıldı.
