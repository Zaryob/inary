.. -*- coding: utf-8 -*-

Bu belgelendirme sayfası **pspec.xml** dosyasına ait XML dizin ağacını ve bu dosyanın kullanım inceliklerini içerir.

###################
**SpecFile** nedir?
###################


**SpecFile** olarak tanımlanmış dosyalar paket yöneticilerindeki kaynak paketlerin \
tanımlamalarını içeren dosyalardır. Bu dosyalar kaynak pakete ait kaynak kod adresi \
kaynak kod imza değerleri (md5 veya sha1sum) ve bilimum açıklamaları içerir. \
**SpecFile** dosyalarının dosya türü ve adı paket yöneticisinden paket yöneticisine \
değişiklik gösterebilir.
Paketçiler genellikle paketlere ait bağımlılık ve diğer sistem bilgilerini bazen \
de derleme yöntemlerini **SpecFile** içerisinde belirtirler. Bu da Linux distrolarının \
şeffaflığı ve açık kaynak oluşunu destekler. Gerekli olması durumunda kişiler bu \
**SpecFile** dosyalarını değiştirerek bir kaynak kodu kendi ihtiyaçları doğrultusunda \
derleyebilir, sisteme ait düzenlemeleri yapabilir. Inary paket yönetim sistemi \
**pspec.xml** isminde bi **SpecFile** içerir. Bu **SpecFile** XML formatındadır.


***********************************
**pspec.xml** dosyası ne işe yarar?
***********************************

**pspec.xml** dosyası paket için bir iskelet oluşturmamızı sağlar. Kaynak koda ait \
arşiv adresi, doğrulama kod (sha1sum) kaynak pakete ait önceki sürümlerin geçmiş \
bilgisi, bağımlılıklar ve gerektirdiği kurulum sonrası :term:`betik`'leri hep bu dosya üzerinde \
tanımlanmıştır. Bu tanımlamalar bir kaynak paketi bölerek farklı ikili paketler \
elde eldilmesini, özel derleme bayrakları `BuildFlags`_ tanımlayarak kaynak paketin \
uygun bir şekilde derlenmesini, kaynak paketlerve ikili paketler için yerelleştirme \
yapılabilmesine imkan sağlar.

Basit bir xml dosyası mantığındadır. Aşağıda örnek bir **pspec.xml** dosyası verilmiştir.

.. _target:

:file:`pspec.xml`

.. sourcecode:: xml

    <!DOCTYPE INARY SYSTEM "https://gitlab.com/Zaryob/inary/raw/master/inary-spec.dtd">
    <INARY>
        <Source>
            <Name>nano</Name>
            <Homepage>http://www.nano-editor.org/</Homepage>
            <Packager>
                <Name>Someone</Name>
                <Email>someone@somewhere.someextension</Email>
            </Packager>
            <License>GPLv3</License>
            <IsA>app:console</IsA>
            <Summary>GNU GPL'd Pico clone with more functionality</Summary>
            <Description>Nano is a small, free and friendly editor which aims to replace Pico,
            the default editor included in the non-free Pine package. Rather than just copying
            Pico's look and feel, nano also implements some missing (or disabled by default)
            features in Pico,such as "search and replace" and "go to line number".
            </Description>
            <Archive sha1sum="e0c88a8f029a0f01247de2582e1a1c5b110f7da8" type="tarxz">
                https://www.nano-editor.org/dist/v2.9/nano-2.9.8.tar.xz
            </Archive>
            <BuildDependencies>
                <Dependency>ncurses-devel</Dependency>
                <Dependency>gettext-devel</Dependency>
            </BuildDependencies>
        </Source>
        <Package>
            <Name>nano</Name>
            <RuntimeDependencies>
                <Dependency>ncurses</Dependency>
                <Dependency>file</Dependency>
            </RuntimeDependencies>
            <Files>
                <Path fileType="config">/etc</Path>
                <Path fileType="localedata">/usr/share/locale</Path>
                <Path fileType="doc">/usr/share/doc/nano</Path>
                <Path fileType="man">/usr/share/man</Path>
                <Path fileType="info">/usr/share/info</Path>
                <Path fileType="data">/usr/share/nano</Path>
                <Path fileType="executable">/usr/bin</Path>
                <Path fileType="executable">/bin</Path>
            </Files>
            <Provides>
                <SCOM script="pakhandler.py">System.PackageHandler</SCOM>
            </Provides>

        </Package>
        <History>
            <Update release="1">
                <Date>2019-01-16</Date>
                <Version>2.7.5</Version>
                <Comment>First release</Comment>
                <Name>Someone</Name>
                <Email>someone@somewhere.someextension</Email>
            </Update>
        </History>
    </INARY>


pspec.xml dosyası basit olarak böyle bir XML dizin ağacına sahiptir. Detaylı XML \
etiket ağacı dökümü ise şu şekildedir.

.. sourcecode:: text

    * Inary
        * Source
             * Name
             * Homepage
             * Packager
                 * Name
                 * Email
             * License
             * IsA
             * PartOf
             * Summary [xml:lang]
             * Description [xml:lang]
             * Archive [sha1sum, type, target]
             * BuildDependencies
                 * Dependency [version, release]
             * Patches
                 * Patch [compressionType, level, target]
        * Package
             * Name
             * Summary [xml:lang]
             * Description [xml:lang]
             * BuildType
             * BuildFlags
                 * Flag
             * IsA
             * PartOf
             * RuntimeDependencies
                 * Dependency [version, release]
             * Files
                 * Path [fileType, permanent, replace]
             * Provides
                 * SCOM [script]
             * Replaces
                 * Package [version, release]
             * AdditionalFiles
                 * AdditionalFile [target, permission, owner]


        * History
             * Update [release, type]
                 * Date
                 * Version
                 * Comment
                 * Name
                 * Email

.. seealso:: Daha fazla bilgi için bakınız `inary-spec.dtd`_
.. _inary-spec.dtd: https://gitlab.com/Zaryob/inary/raw/master/inary-spec.dtd

**************************
**"pspec.xml"** Etiketleri
**************************

**pspec.xml** dosyasında 3 ana :term:`etiket` vardır: `Source`_, kaynak paketin detaylı \
bilgilerini içerir; `Package`_, kaynak paketten oluşturulacak ikili paketleri içerir, \
her bir ikili paket için yeni bir `Package`_ :term:`etiket`'i açılır; `History`_, \
kaynak pakete  ait geçmiş bilgisi ve mevcut ikili paketlerin alacağı yayım ve \
sürüm bilgilerini içerir.

======
Source
======
Bu :term:`etiket` kaynak pakete ait bazı özel bilgileri ve tanımlamaları içerir. Bu \
:term:`etiket` her bir **pspec.xml** dosyası için sadece bir kere kullanılabilir. \
Bu :term:`etiket` içerisinde kaynak koda ait bazı bilgiler ve tanımlamalar vardır. \
Bu :term:`etiket` alt :term:`etiket`'ler içerir. Bunlar:


Name
----

Kaynak paketin adını içerir. Kaynak paketin adlandırmasında dikkatli olunması \
gereken paket adında *"ascii_letters"* olarak tanımlanmış karakterleri \
``abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789`` içermelidir. \
Parantez işaretleri ``()[]{}``, bölü ve ters bölü işaretleri ``/\``, özel tanımlı \
işaretler ``&%+*#=|<>~̈́:'!<,`` ve tırnak işaretleri paket adlandırması için kullanılmamalıdır. \
Ek olarak bir paketin isminin sayı olması sıkıntı yaratabildiği için sayı ile \
başlayan paket adlandırmalarından elden geldikçe uzak durulmalıdır.


Homepage
--------

Kaynak paketi geliştiren ekibin veya paketin yayıldığı ana geliştirme adresidir. \
`Archive`_ :term:`etiket`'inden farklı olarak kaynak kodun dağıtıldığı sunucu adresidir. \
Sadece son kullanıcıyı bilgilendirme amaçlıdır.


Packager
--------

Kaynak paketin dosyalarını yazan paketçinin bilgilerini içerir. Bu sayede kimin \
hangi paketlerinin bulunduğunun takibi ve hatalı paketlerin paketçisi paketleri \
hakkında uyarılabilir, iş bölümü kolaylıkla sağlanabilir. Bu :term:`etiket` altındaki \
iki :term:`etiket` paketçinin bilgilerini içerir:

    * **Name**: Paketçinin adı
    * **Email**: Paketçinin e-posta adresi


License
-------

Kaynak paketin lisans bilgisini içerir.

.. seealso:: Daha fazla bilgi için bakınız #Fixme:


IsA
---

Kaynak / ikili paketin paket tipini içerir. Hem `Source`_ hem de `Package`_ içinde \
kullanılabilir. Bu da bir kaynak paketten üretilen farklı paket tipindeki ikili \
paketleri belirtmemizi sağlar. En basit ifadesiyle bir kaynak paket derlendiği \
zaman :term:`ikili çalıştırılabilir dosyalar`, kütüphaneler, C/C++ gibi diller için \
:term:`başlık dosyaları` ve :term:`manual sayfaları` ile belgelendirme dosyalarını \
içeren geniş bir katalogda dosyalar oluşabilir. Bu :term:`etiket` farklı kullanıcılara \
hitap edebilecek paketleri ayırmamızı kolaylaştırır.

.. seealso:: Paket tipleri hakkında daha fazla bilgi için bakınız. #Fixme:


PartOf
------

Kaynak paketin dahil olduğu **component** bilgisidir. Bu da bir paketten üretilen \
farklı ikili paketlerin ayrılmasını sağlar. Mesela bir kaynak kod derlenince oluşan \
çalıştırılabilir dosyaları  bir paket içerir, başlık dosyalarını ise başka bir paket \
içerebilir. Başlık dosyalarını içeren ikili paketin **component** bilgisi farklı iken \
diğerlerininki farklı olur. Bu da bizim belirli **component** paketlerini tek komutla \
yüklememizi kolaylaştırır.

.. seealso: **Component** hakkında daha fazla bilgi için bakınız. #Fixme:


Summary
-------

Kaynak pakete ait kısa bir tanımlama metnidir. Öntanımlı dil İngilizce'dir. \
Bu :term:`etiket` bir adet :term:`belirteç` içerir.

    * xml:lang tanımlama metninin hangi dilde yazıldığını belirtir.

Description
------------

Kaynak pakete detaylı bir açıklama metnidir. Öntanımlı dil İngilizce'dir. \
Bu :term:`etiket` bir adet :term:`belirteç` içerir.

    * xml:lang açıklama metninin hangi dilde yazıldığını belirtir.

BuildDependencies
-----------------

Kaynak paketin derlemesi sırasında gerekli olan bağımlılıklardır. Bu bağımlılıklar \
kaynak kodun derleme yöntemine uygun olarak bir dosya içerisinde (Makefile, \
CMakeLists.txt, requirements.txt, etc.) tutulur. Her bir bağımlılık için bu :term:`etiket` \
altında **Dependency** isminde bir :term:`etiket` açılarak her birisi tek tek girilir. \
**Dependency** :term:`etiket`'leri aşağıdaki :term:`belirteç` verilerini içerir. \
Bu :term:`belirteç` verilerinin kullanılmasının sebebi şudur. Eğer bir kaynak kod \
gereksinimi olan bir bağımlılığın sadece belirli bir sürümü veya belirli bir sürümünün \
yukarısındaki ya da aşağısındaki sürümü ile derlenebiliyorsa bu detay bilgi girilerek \
paketlerin uygun şekilde derlenmesi sağlanır. Aynı mantıkla yayım numarası da girilebilir.


    * version: Özel bir sürümü belirtir.
    * versionTo: Belirli bir sürümden kadar olan sürümleri belirtir.
    * versionFrom: Belirli bir sürümden yukarısını belirtir.
    * release: Özel bir yayımı belirtir.
    * releaseTo: Belirli bir yayıma kadar olanı belirtir.
    * releaseFrom: Belirli bir yayımdan yukarısını belirtir.


Archive
-------

Kaynak paketin, derlenmemiş dosyaların, kaynak kodunun bilgilerini içeren :term:`etiket`'dir. \
`Archive`_ :term:`etiket`'i içerisine kaynak kodun uzak sunucu adresi girilirken :term:`belirteç` \
olarak bazı bilgiler verilir. Bir kaynak paketin birden fazla `Archive`_ :term:`etiket`'i bulunabilir.

    * sha1sum: Kaynak paketin doğrulama kodunu içerir. Sha1sum verisi paket doğrulaması için kullanılır.
    * type: Kaynak paketin sıkıştırıldığı dosya tipini içerir. Bakınız: paket sıkıştırma tipleri.
    * target (Kullanılması zorunlu değildir): Kaynak paketin açılacağı dizin bilgisidir.


Patches
-------

Kaynak paketin son sürümülerinde bazen yama dosyaları yayınlanır. Kaynak paket yeniden \
derlenip yeniden yayımlanacak iken bu yamalar yapılmalıdır. Şeffaflık açısından bu \
yamalar  **files/** klasörü içerisine atılır ve **pspec.xml** içerisine girilir. \
Her bir yama için **Patch** isminde bir alt :term:`etiket` açılır, **files/** klasörünün \
içindeki konumu bu :term:`etiket`'e bilgi olarak girilir. Bu :term:`etiket` 3 adet \
:term:`belirteç` içerir:

    * compressionType (Kullanılması zorunlu değildir): Eğer yama dosyası sıkıştırılmış  ise (kernel yamaları gibi) buraya sıkıştırılma tipi girilir. Öntanımlı olarak sıkıştırma tipi yoktur. Bakınız: paket sıkıştırma tipleri
    * level: Her yama belirli bir seviyede uygulanır. Öntanımlı seviye 0'dır.
    * target(Kullanılması zorunlu değildir): Yamanın uygulanacağı sadece bir alt dizin varsa o dizin buraya girilir.


AdditionalFiles
---------------

Kaynak kodun açılması sonrasında kaynak kodun açıldığı klasör'e kopyalanacak dosyalar \
başta **files/** dizini içerisine atılır. Sonrasında **pspec.xml** dosyasına girilir. \
Bu sayede kaynak koda hangi ek dosyaları nereye eklemiş olduğumuzu rahatlıkla görebiliriz \
Bu pakette şeffaflık sağlar ayrıca isteyen geliştiricinin ek dosyalardan birisini rahatlıkla \
işleme tabi tutmasını sağlar.

.. note:: Kaynak kodun açıldığı yer `/var/inary/<paket_adı>-<paket_sürümü>-<paket-yayımı>/work/` klasörüdür

`AdditionalFiles`_ **AdditionalFile** isminde bir alt :term:`etiket` içerir. Her bir dosya yeni bir \
**AdditionalFile** :term:`etiket`'i açılmak suretiyle **pspec.xml** dosyasına eklenir. **AdditionalFile** \
3 adet :term:`belirteç` içerir.

    * target: dosyanın kopyalanacağı konum.
    * permission: dosyanın okuma yazma izni.
    * owner: dosyanın sahipliği.

=======
Package
=======

Bu :term:`etiket` derleme sonunda oluşacak ikili paketler için kullanılır. Bir kaynaktan \
bir ikili paket oluşturulabileceği gibi derleme sonucunda oluşanlar farklı paketlere \
dağıtılabilir. Gerekli olduğu durumda bir paketten farklı bir derleme methodu ile farklı \
paketler de oluşturulabileceği için bu tanımlamalar burada yer alır. Bu :term:`etiket` \
bazı alt :term:`etiket`'ler içerir:

Name
----

`Source`_ :term:`etiket`'i altındaki Name aynı özelliklere sahiptir. Ama bir kaynak koddan \
oluşan farklı isimde bir paket oluşabileceği için girilmesi zorunludur.


Summary
-------

Kaynak pakete veya ikili pakete ait kısa bir tanımlama metnidir. Eğer `Package`_ \
:term:`etiket`'i içerisinde girilmedi ise ikili paket `Source`_ içindeki Summary kullanılır. \
Öntanımlı dil İngilizce'dir. Bu :term:`etiket` bir adet :term:`belirteç` içerir.

    * xml:lang tanımlama metninin hangi dilde yazıldığını belirtir.


Description
------------

Kaynak pakete veya ikili pakete ait detaylı bir açıklama metnidir. Eğer `Package`_ \
:term:`etiket`'i içerisinde girilmedi ise ikili paket `Source`_ içindeki Description \
kullanılır. Öntanımlı dil İngilizce'dir. Bu :term:`etiket` bir adet :term:`belirteç` içerir.

    * xml:lang açıklama metninin hangi dilde yazıldığını belirtir.


BuildType
---------

Derleme tipini içerir. Bu bilgiyi kullanarak farklı derleme tipleri için farklı \
derleme fonksiyonları kullanılabilir.


BuildFlags
----------

Bir derleme tipi için öntanımlı bir derleme bayrağı eklenebilir.


IsA
---

`Source`_ içerisindeki ile işlevi aynıdır. Eğer `Package`_ :term:`etiket`'i içerisinde \
girilmedi ise ikili paket `Source`_ içindeki IsA bilgisini kullanır.


PartOf
------

`Source`_ içerisindeki ile işlevi aynıdır. Eğer `Package`_ :term:`etiket`'i içerisinde \
girilmedi ise ikili paket `Source`_ içindeki PartOf bilgisini kullanır.


RuntimeDependencies
-------------------

İkili dosyaların çalışması için gerekli olan bağımlılıklardır. Bu bağımlılıklar ``ldd`` \
çıktıları veya :term:`script based diller` için moduller veya başka şeyler olabilir. Her bir \
bağımlılık için bu :term:`etiket` altında **Dependency** isminde bir :term:`etiket` açılarak \
her birisi tek tek girilir. **Dependency** :term:`etiket`'leri aşağıdaki :term:`belirteç` \
verilerini içerir. Bu :term:`belirteç` verilerinin kullanılmasının sebebi şudur. Eğer \
bir ikili dosya gereksinimi olan bir bağımlılığın sadece belirli bir sürümü veya belirli \
bir sürümünün yukarısındaki ya da aşağısındaki sürümü ile çalıştırılabiliyorsa bu detay \
bilgi girilerek paketlerin çalışmasında sıkıntı yaşanmaması sağlanır, son kullanıcı madur \
olmaz. Aynı mantıkla yayım numarası da girilebilir.

    * version: Özel bir sürümü belirtir.
    * versionTo: Belirli bir sürümden kadar olan sürümleri belirtir.
    * versionFrom: Belirli bir sürümden yukarısını belirtir.
    * release: Özel bir yayımı belirtir.
    * releaseTo: Belirli bir yayıma kadar olanı belirtir.
    * releaseFrom: Belirli bir yayımdan yukarısını belirtir.


Files
-----

Inary ile kaynak koddan paket oluştururken oluşan dosyaları parçayabileceğimizi söylemiştik. \
İşte bu tanımlamalar **Files** :term:`etiket`'i altında yapılır. Her bir klasör **Path** \
:term:`etiket`'i altına yazılır. **Path** :term:`etiket`'i 1 adet :term:`belirteç` içerir.

    * fileType: Paket içerisine alınan klasörün hangi veri tipinden dosyalar içerdiğini tanımlar. Öntanımlı dosya tipleri:
        * executable: :term:`ikili çalıştırılabilir dosyalar` veya :term:`betik`'ler
        * library: :term:`kütüphane dosyaları`
        * data: Bazı ek dosyalar
        * config: Programa ait config dosyaları.
        * doc: Belgelendirmeler
        * man: :term:`manual sayfaları`
        * info: Kaynak koda ait bilgi dosyaları
        * localedata: Yerelleştirme dosyaları.
        * header: Geliştirme kütüphanelerinin :term:`başlık dosyaları`


Conflicts
---------

Derlenmiş paketin çakıştığı diğer paketlerdir. Her bir çakışma için bu :term:`etiket` altında \
`Package`_ isminde bir :term:`etiket` açılarak her birisi tek tek girilir. `Package`_ \
:term:`etiket` ları aşağıdaki :term:`belirteç` verilerini içerir. Bu :term:`belirteç` \
verilerinin kullanılmasının sebebi şudur. Eğer çakışmalar bir paketin sadece belirli \
bir sürümü veya belirli bir sürümünün yukarısındaki ya da aşağısındaki sürümü ile \
yaşanıyorsa bu detay bilgi girilerek paketlerin çalışmasında sıkıntı yaşanmaması sağlanır, \
son kullanıcı madur olmaz. Aynı mantıkla yayım numarası da girilebilir.

    * version: Özel bir sürümü belirtir.
    * versionTo: Belirli bir sürümden kadar olan sürümleri belirtir.
    * versionFrom: Belirli bir sürümden yukarısını belirtir.
    * release: Özel bir yayımı belirtir.
    * releaseTo: Belirli bir yayıma kadar olanı belirtir.
    * releaseFrom: Belirli bir yayımdan yukarısını belirtir.


Replaces
--------

Bir kaynak paketten oluşan ikili paketin sonraki sürümlerinde ismi değiştirildiği \
zaman bu :term:`etiket` kullanarak eski isimdeki paket bu isimdeki paket ile yer \
değiştirilmesi sağlanır. Her bir değişme için bu :term:`etiket` altında `Package`_ \
isminde bir :term:`etiket` açılarak her birisi tek tek girilir. \
`Package`_ :term:`etiket`'leri aşağıdaki :term:`belirteç` verilerini içerir. \
Bu :term:`belirteç` verilerinin kullanılmasının sebebi şudur. Eğer değişim bir \
paketin sadece belirli bir sürümü veya belirli bir sürümünün yukarısındaki ya da \
aşağısındaki sürümü ile yapılacaksa bu detay bilgi girilerek paketlerin çalışmasında \
sıkıntı yaşanmaması sağlanır, son kullanıcı madur olmaz. Aynı mantıkla yayım \
numarası da girilebilir.

    * version: Özel bir sürümü belirtir.
    * versionTo: Belirli bir sürümden kadar olan sürümleri belirtir.
    * versionFrom: Belirli bir sürümden yukarısını belirtir.
    * release: Özel bir yayımı belirtir.
    * releaseTo: Belirli bir yayıma kadar olanı belirtir.
    * releaseFrom: Belirli bir yayımdan yukarısını belirtir.


Provides
--------

Bir paketin kurulum sonrası :term:`betik`'leri bu :term:`etiket` altında belirlenir. Bu :term:`etiket` \
altında **SCOM** isminde bir :term:`etiket` açılır. **SCOM** :term:`etiket`'i içerisine :term:`betik`'in \
SCOM tipi yazılır. Bu :term:`etiket` 1 adet :term:`belirteç` içerir.

    * script: :term:`betik`'lerin '``scom/`` klasörü içerisindeki konumudur.

.. seealso: Daha fazla bilgi için bakınız(SCOM :term:`betik` tipleri). #Fixme:

AdditionalFiles
---------------

İnşaa edilen kodun paketleme dizinine kurulması sonrasında eklenecek ".desktop" dosyaları gibi elle \
yazılması gereken dosyaları eklememiz için kullanılır. Kullanım mantığı `Source`_ içindeki \
ile aynıdır. Paketleme dizininee kopyalanacak dosyalar başta **files/** dizini içerisine \
atılır. Sonrasında **pspec.xml** dosyasına girilir. \
Bu sayede kurulum dizinine hangi ek dosyaları nereye eklemiş olduğumuzu rahatlıkla görebiliriz \
Bu pakette şeffaflık sağlar ayrıca isteyen geliştiricinin ek dosyalardan birisini rahatlıkla \
işleme tabi tutmasını sağlar.

.. note:: İnşaa edilen kodun kurulduğu klasör `/var/inary/<paket_adı>-<paket_sürümü>-<paket-yayımı>/install/` klasörüdür

`AdditionalFiles`_ **AdditionalFile** isminde bir alt :term:`etiket` içerir. Her bir dosya yeni bir \
**AdditionalFile** :term:`etiket`'i açılmak suretiyle **pspec.xml** dosyasına eklenir. **AdditionalFile** \
3 adet :term:`belirteç` içerir.

    * target: dosyanın kopyalanacağı tam konumdur.
    * permission: dosyanın okuma yazma izni.
    * owner: dosyanın sahipliği.

.. note:: Bir ikili dosyanın bu :term:`etiket` içerisindeki bir dosya ile değiştirilmesi tehlikeli ve yasaktır.
.. note:: Bir target :term:`belirteç`'i içerinde girilen dosyanın atılacağı konumda aynı isimli başka bir dosya bulunması hataya sebebiyet verir.

=======
History
=======

Pakete ait geçmiş bilgisini içerir. Bir adet alt :term:`etiket`'e sahiptir. Bir kaynak paket \
için yeni bir güncelleme gireleceği zaman bu :term:`etiket`'le \
aynı isimde ama yayım :term:`belirteç`'i bir fazla olan yeni bir dizin eklenir.
Örneğin 3. yayımına ulaşmış bir paketin History dizini şöyle olabilir:

.. sourcecode:: xml

    <History>
        <Update release="3">
            <Date>2019-03-16</Date>
            <Version>1.3</Version>
            <Comment>Rebuilded last version</Comment>
            <Name>Someone</Name>
            <Email>someone@somewhere.someextension</Email>
        </Update>
        <Update release="2">
            <Date>2019-02-16</Date>
            <Version>1.3</Version>
            <Comment>Updated new version.</Comment>
            <Name>Someone</Name>
            <Email>someone@somewhere.someextension</Email>
        </Update>
        <Update release="1">
            <Date>2019-01-16</Date>
            <Version>1.2</Version>
            <Comment>First release</Comment>
            <Name>Someone</Name>
            <Email>someone@somewhere.someextension</Email>
        </Update>
    </History>

Update
------

Pakete ait son güncel yayım ve sürüm bilgisini içeren :term:`etiket`'dir. İki adet \
:term:`belirteç` ve bazı alt :term:`etiket`'ler içerir.

    * release: Pakete ait güncelleştirmenin yayım numarasıdır.
    * type: Paketin o güncelleştirmesi eğer güvenlik("security") güncellemesi veya önemli bir güncelleme ("critical") ise burada belirtilir.

Date
^^^^

En son güncellemenin girildiği tarihtir.

.. note:: Inary paket geliştiricilerine GG/AA/YYYY formatında tarih girilmesi önemle rica olunur

Version
^^^^^^^

Pakete ait sürüm bilgisidir.

.. seealso:: Inary paket geliştiricilerinin sürüm bilgileri hakkında detaylı bilgiyi versionning.rst dosyasından incelemesi ve sürüm bilgilerini ona göre düzenlemesi önemle rica olunur.

Comment
^^^^^^^

Paket güncelleştirmesine ait güncelleştirme mesajıdır. Paketin yeni yayımında neler yapıldığını aktarır.

Name
^^^^

Yeni yayına yükselten paketçinin adı.

Email
^^^^^

Yeni yayıma yükselten paketçinin e-posta adresi.

Action
^^^^^^

Paketin kurulmasının ardın yapılması gereken bazı ayarlamalar olabilir. Sistem yeniden \
başlatılmalı, revdep güncellemesi yapılması gerekebilir. Bu işlem bu :term:`etiket` altına yazılır. \

Bir adet :term:`belirteç` alır.

    * package: Bu işlemi farklı bir paket için yapması gerekiyorsa burada belirtilir.

.. seealso: Daha fazla işlem için bakınız paket sonrası işlemler.
