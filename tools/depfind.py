#!/usr/bin/env python
#-*- coding: utf-8 -*-



# Kutuphaneler import ediliyor
from inary.db.filesdb import FilesDB
import re
import sys

# files_db sinifi ornekleniyor
files_db = FilesDB()
dosyalar = files_db.search_file("Config.cmake") + files_db.search_file(".pc")


# kullanilacak listeler tanimlaniyor

deb_liste = []
deb_liste_parcali = []
bagimliliklar = []
arama_list = []
bulunanlar = []
yazdirilacak = []
set_list = []
pspec_listele = []
bulunanlar_pc = []

# kullanilacak kumeler tanimlaniyor



#sozlukler tanimlaniyor

version_hepsi = {}
karsilik_version_isim = {}
inaryde_nedir = {}
sade_sayi_version = {}


# verilen cmakelists.txt ye ulasiliyor

cmake_list = sys.argv[1]


def cmake_ulas(): 
    # bu fonksiyon cmakelists in icerigini ulasilabilir hale getiriyor
    file_list = open(cmake_list , "r")

    parcali = file_list.read().split("find_package")
    file_list.close()
    parcali.pop(0)

    for i in parcali:
        if "#" in i:
            parcali.pop(parcali.index(i))
            parcali.append(i.split("#")[0])

    for i in parcali:

        deb_liste.append(i.split(")")[0].replace("(",""))

    for i in  deb_liste:

        deb_liste_parcali.append(i.strip("").split(" "))


def version_bul():


    file_list = open(cmake_list , "r")

    parcali = file_list.readlines()

    file_list.close()

    for i in parcali:
        if "#" in i:
            parcali.pop(parcali.index(i))
            parcali.append(i.split("#")[0])


    for i in parcali:
        if i.replace(" ","").startswith("set("):
            set_list.append(i.strip().lstrip("set").rstrip(")\n").strip().lstrip("("))

    for i in set_list:
        if len(i.strip().split(" ")) >= 2 and i.strip().split(" ")[1].isdigit() == False :
            version_hepsi[i.split(" ")[0]] = i.split(" ")[len(i.split(" "))-1]


    for i in deb_liste_parcali:
        for j in i:
            if re.match("\n",j):
                i.pop(i.index(j))
            elif j == "":
                i.pop(i.index(j))
        for j in i:
            if re.search(" ",j):
                i.pop(i.index(j))
            elif j == "":
                i.pop(i.index(j))
        for j in i:
            if j == "":
                i.pop(i.index(j))
        if len(i) > 1:
            if re.match("[0-9]",i[1]) or  re.match("\$",i[1]):
                karsilik_version_isim[i[0]] = i[1]

def duzenle():
    #bu fonksiyon istenmeyen karekterlerden kurtuluyor

    for i in deb_liste_parcali:
        for j in i:
            if re.search("\$",j):
                i.pop(i.index(j))
            elif j == "":
                i.pop(i.index(j))
        for j in i:
            if re.search("NO_MODULE",j):
                i.pop(i.index(j))
            elif j == "":
                i.pop(i.index(j))
        for j in i:
            if re.search("EXACT",j):
                i.pop(i.index(j))
            elif j == "":
                i.pop(i.index(j))
        for j in i:
            if re.search("OPTIONAL_COMPONENTS",j):
                i.pop(i.index(j))
            elif j == "":
                i.pop(i.index(j))
        for j in i:
            if re.search("NO_POLICY_SCOPE",j):
                i.pop(i.index(j))
            elif j == "":
                i.pop(i.index(j))
        for j in i:
            if re.search("QUIET",j):
                i.pop(i.index(j))
            elif j == "":
                i.pop(i.index(j))
        for j in i:
            if re.search(".*CONFIG.*",j):
                i.pop(i.index(j))
            elif j == "":
                i.pop(i.index(j))
        for j in i:
            if re.search(".*REQUIRED.*",j):
                i.pop(i.index(j))
            elif j == "":
                i.pop(i.index(j))
        for j in i:
            if re.search(".*COMPONENTS.*",j):
                i.pop(i.index(j))
            elif j == "":
                i.pop(i.index(j))
        for j in i:
            if re.match("\"[0-9]",j):
                sade_sayi_version[i[0]] = i.pop(i.index(j))
            elif j == "":
                i.pop(i.index(j))
        for j in i:
            if re.match("[0-9]",j):
                sade_sayi_version[i[0]] = i.pop(i.index(j))
            elif j == "":
                i.pop(i.index(j))
        for j in i:
            if re.match("\n",j):
                i.pop(i.index(j))
            elif j == "":
                i.pop(i.index(j))
        for j in i:
            if re.search(" ",j):
                i.pop(i.index(j))
            elif j == "":
                i.pop(i.index(j))
        for j in i:
            if j == "":
                i.pop(i.index(j))

        bagimliliklar.append(i)





def bag_list():
    # bu fonksiyon bagimliliklari listeliyor

    # kullanilacak degiskenler tanimlaniyor

    ilk = True

    print "-----Bağımlılıklar listeleniyor----- \n"

    for i in bagimliliklar:
        if ilk == True:
            if i[0] not in arama_list:
                print i[0]
                arama_list.append(i[0])
                ilk = False
        n = 1
        if len(i) == 1:
            ilk = True
        while n < len(i) and len(i) != 1 :
            print i[0].strip("\n") + i[n].strip("\n")
            arama_list.append(i[0].strip("\n") + i[n].strip("\n"))
            ilk = True
            if i[0].strip("\n") in karsilik_version_isim.keys():
                karsilik_version_isim[i[0].strip("\n") + i[n].strip("\n")] = karsilik_version_isim[i[0].strip("\n")]
            n = n +1



def dizin_list():
    # bu fonksiyon bulunan bagimliliklarin dizinlerini listeliyor
    print "-----Bağımlılıkların bulunduğu dizinler listeleniyor----- \n"
    for i in arama_list:
        for j in dosyalar:
            for t in j:
                for k in t:
                    if k.endswith(("/" + i + "Config.cmake")):
                        print i+ "-"*(30 - len(i)) +"> " + j[0] + " <" + "-"*(40 - len(j[0])) + "> "  + k
                        bulunanlar.append(i)
                        inaryde_nedir[i] = j[0]
                        if j[0] not in yazdirilacak:
                            yazdirilacak.append(j[0])
                    elif k.endswith(("/" + i + "-config.cmake")):
                        print i +"-"*(30 - len(i)) +"> " + j[0] + " <" + "-"*(40 - len(j[0])) + "> "  + k
                        bulunanlar.append(i)
                        inaryde_nedir[i] = j[0]
                        if j[0] not in yazdirilacak:
                            yazdirilacak.append(j[0])

def olmayan_list():
    #bu fonksiyon dizinleri bulunamayan bagimliliklari listeliyor
    global bulunmayanlar
    print "-----Bulunamayanlar listeleniyor----- \n"
    bulunmayanlar = set(arama_list) - set(bulunanlar)

    for i in bulunmayanlar:
        print i

def pc_ara():
    global bulunmayanlar
    print "-----Bulunamayanlar .pc olarak aranıyor-----\n"

    bos = True
    for i in bulunmayanlar:
        for j in dosyalar:
            for t in j:
                for k in t:
                    if k.endswith(("/" + i.lower() + ".pc")):
                        print i+ "-"*(30 - len(i)) +"> " + j[0] + " <" + "-"*(40 - len(j[0])) + "> "  + k
                        bulunanlar_pc.append(i)
                        inaryde_nedir[i] = j[0]
                        bos = False
                        if j[0] not in yazdirilacak:
                            yazdirilacak.append(j[0])
    if bos == True:
        print "bulunamadı"
    else:
        bulunmayanlar = bulunmayanlar - set(bulunanlar_pc)



def sirala():

    print "---------pcpec.xml için listeleniyor------ \n"

    for i in arama_list:
        if i not in bulunmayanlar and i in karsilik_version_isim.keys() and len(version_hepsi) != 0:
            if re.match("[0-9]",karsilik_version_isim[i].lstrip("${").rstrip("}")):
                if re.match("\"",karsilik_version_isim[i].lstrip("${").rstrip("}")):
                    a = "             <Dependency versionFrom=%s>%s</Dependency>" % (karsilik_version_isim[i].lstrip("${").rstrip("}"),inaryde_nedir[i])
                    if a not in pspec_listele:
                        pspec_listele.append(a)

                else:
                    a = "             <Dependency versionFrom=\"%s\">%s</Dependency>" % (karsilik_version_isim[i].lstrip("${").rstrip("}"),inaryde_nedir[i])
                    if a not in pspec_listele:
                        pspec_listele.append(a)

            elif karsilik_version_isim[i].lstrip("${").rstrip("}") not in version_hepsi.keys():
                a = "             <Dependency>%s<Dependency>" % inaryde_nedir[i]
                if a not in pspec_listele:
                    pspec_listele.append(a)

            else:
                if re.match("\"",version_hepsi[karsilik_version_isim[i].lstrip("${").rstrip("}")]):
                    a = "             <Dependency versionFrom=%s>%s</Dependency>" % (version_hepsi[karsilik_version_isim[i].lstrip("${").rstrip("}")],inaryde_nedir[i])
                    if a not in pspec_listele:
                        pspec_listele.append(a)

                else:
                    a = "             <Dependency versionFrom=\"%s\">%s</Dependency>" % (version_hepsi[karsilik_version_isim[i].lstrip("${").rstrip("}")],inaryde_nedir[i])
                    if a not in pspec_listele:
                        pspec_listele.append(a)

        elif i not in bulunmayanlar and i in sade_sayi_version.keys():
            if re.match("\"",sade_sayi_version[i]):
                a = "             <Dependency versionFrom=%s>%s</Dependency>" % (sade_sayi_version[i],inaryde_nedir[i])
                if a not in pspec_listele:
                    pspec_listele.append(a)

            else:
                a = "             <Dependency versionFrom=\"%s\">%s</Dependency>" % (sade_sayi_version[i],inaryde_nedir[i])
                if a not in pspec_listele:
                    pspec_listele.append(a)


        elif i not in bulunmayanlar:
            a = "             <Dependency>%s<Dependency>" % inaryde_nedir[i]
            if a not in pspec_listele:
                pspec_listele.append(a)

    pspec_listele.sort()
    for i in pspec_listele:
        print i



def calistir():
    # diger fonksiyonlari sirasi ile calistirir calisma sirasi onemlidir.
    cmake_ulas()
    version_bul()
    duzenle()

    bag_list()
    print ""

    dizin_list()
    print ""

    olmayan_list()
    print ""

    pc_ara()
    print ""

    sirala()


calistir()