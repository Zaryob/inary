#!/usr/bin/python 
import sys
import os
data = ""
inaryfile=str(sys.argv[1])
sys.argv.append("")
kontrol=str(sys.argv[2])
#make workspace
os.system("rm -rf /tmp/uninary/")
os.system("mkdir /tmp/uninary/")
os.system("unzip " + inaryfile + " -d /tmp/uninary/")
#manipule xml file
os.system('sed -i "s/<\//:/" /tmp/uninary/metadata.xml')
os.system('sed -i "s/<//" /tmp/uninary/metadata.xml')
os.system('sed -i "s/>/:/" /tmp/uninary/metadata.xml')
os.system('sed -i "s/> //" /tmp/uninary/metadata.xml')
os.system('echo "--dosya-sonu--" >> /tmp/uninary/metadata.xml')
metadata = open("/tmp/uninary/metadata.xml")
os.system("rm -f /tmp/uninary/control")
os.system("touch /tmp/uninary/control")
def bul(aranacak,yazilacak ,i=1,value=1):
  durum = "devam"
  while durum == "devam":
    data = metadata.readline()
    if aranacak in data:
      durum = "dur"
      data=data.split(":")
      if value == 1:
	data=data[i]
	if data == "x86_64":
	  data = "amd64" 
	data = yazilacak + data
	kod= 'echo "'+ data + '" >> /tmp/uninary/control'
	print kod
	os.system(kod)
    if "--dosya-sonu--" in data:
      durum = "dur"
      

#write control
bul("Package:","x",1,0)
sayi=metadata.tell()
bul("Name:","Package: ")
metadata.seek(sayi)
bul("PartOf:","Priority: ")
os.system('echo "Section: inarylinux" >> /tmp/uninary/control')
metadata.seek(sayi)
bul("InstalledSize","Installed-Size: ")
metadata.seek(sayi)
bul("Update","x",1,0)
bul("Name:","Maintainer: ")
metadata.seek(sayi)
bul("Architecture:","Architecture: ")
metadata.seek(sayi)
bul("Update","x",1,0)
bul("Version","Version: ")
metadata.seek(sayi)
bul("Dependency release","Depends: ")
metadata.seek(sayi)
bul("Summary xml","Description: ",2)
metadata.seek(sayi)
bul("Description xml"," ",2)
#remove metadata.xml
os.system("rm -f /tmp/uninary/metadata.xml")
#remove files.xml
os.system("rm -f /tmp/uninary/files.xml")
#make debian dir
os.system("mkdir /tmp/uninary/DEBIAN/")
#move control
os.system("mv -f /tmp/uninary/control /tmp/uninary/DEBIAN/")
print "control Dosyasi olusturuldu. Simdi gerekli betikleri olusturunuz."
if kontrol == "x":
    print "kontrol edildigi kabul edildi."
else:
    bekleme=input()
os.system("cd /tmp/uninary/ ; tar -xf /tmp/uninary/*.tar.*")
os.system("rm -f /tmp/uninary/install.tar.*")
print "Paketlemeden onceki son kontrollerinizi yapiniz."
if kontrol == "x":
    print "kontrol edildigi kabul edildi."
else:
    bekleme=input()
os.system("dpkg -b /tmp/uninary/")
inaryfile=inaryfile.split("/")
debfile = inaryfile[len(inaryfile) - 1]
os.system("mv /tmp/uninary.deb ./"+ inaryfile[len(inaryfile) - 1] + ".deb")
