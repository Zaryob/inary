                INARY PACKAGE MANAGER
                ---------------------

Pisi çatalı: Copyright (C) 2005 - 2011, Tubitak/UEKAE
          GNU/Genel Kamu Lisansı sürüm 2 ile lisanslanmıştır.

Inary çatalı ve geliştirmeleri: Copyright (C) 2016 - 2020 Suleyman POYRAZ (Zaryob)
          Lisansı GNU/Genel Kamu Lisansı sürüm 3'e yükseltilmiştir.

Inary geliştirmeleri :  Copyright (C) 2018 - 2020 Ali Rıza KESKİN (Sulincix)



https://github.com/Pardus-Linux/pisi adresinden çatallanmıştır

Inary paket yönetim sistemi mevcut pisi paket yöneticisinin eksiklerini,
hatalarını onarmak, python3 ile yeniden ele alınıp açık kaynak dünyasındaki
son gelişmeleri yakalamak amacıyla 21-12-2016 tarihinde pisi çatalı üzerinde
çalışılarak başlamış; ilerleyen başlangıç niteliğinde olan pisi çatalından
kodlama yöntemi ve kullanılan ek modüller bakımından ayrılmış ve kendine
özgü bir hale dönüşmüş, ayrıca pisi adının lisanslı olması sebebyle yeniden
adlandırılarak geliştirilmeye devam edilmiştir.

Yazılım inary adını aldığı zaman gitlab sitesi üzerinden kamuya yayılmıştır.

Diğer paket yönetim sistemlerinden ayrılan yanları:
 - Dinamik dosya veritabanına sahiptir. Kurulu dosyalarda değişme olup olmadığı
   ile ilgili takipler kolayca yapılabilir.
 - Python ile kodlanmış diğer paket yöneticilerine göre oldukça hızlı ve seri
   iş yapar.
 - Tüm kurulum betiği python scriptlerinden oluştuğu için betikleri anlaması
   kolaydır, pakete ait diğer veriler xml dosyalarında depo edildiği için paket
   yapım arayüzü ile terminal ekranına gerek kalmadan paket oluşturma işi
   yapılabilir.

Diğer özellikleri:
 - Sağlam ve python içinde gömülü bir veritabanı ile çalıştığı için hızlıdır.
 - LZMA ve XZ sıkıştırma yöntemleri kullandığı için daha küçük paketlere sahiptir.
 - Basit düzey ve üst düzey tüm işlemleri aynı kararlılıkla yerine getirir
 - Forend uygulamaları tasarlanmasına elverişli bir yapıdadır.
 - Terminal arayüzü oldukça anlaşılır ve kullanıcı dostudur.


Kurulum bağımlılıkları:
python3-pycurl | python3-requests | requests | wget
intltool

