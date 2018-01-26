2018-01-22 Suleyman POYRAZ <nipalensisaquila@gmail.com>
    * itembyrepo patladı --- STATUS: NOT FIXED; FLAG: CRITICAL ---:
    itemby repo ile paketlerin getirilmesi sirasinda ters giden
    biseyler var. Mevcut binary depodaki hicbir sey listelenmiyor
    Ya index alinirken bir sikinti oldugu icin ya da ciddi ciddi 
    itembyrepo patladi gitti. Uff cok sinir bozucu bisey.

```ADDONS
#~ sudo inary-cli it libtool --no-color
Warning: Safety switch: The component system.base cannot be found.
Error: System error. Program terminated.
Error: Repo item libtool not found
Please use 'inary help' for general help.
Use --debug to see a traceback.


#~ sudo inary-cli it libtool --no-color --debug
DEBUG: HistoryDB initialized in 0.00017023086547851562.
DEBUG: ComponentDB initialized in 0.00010442733764648438.
DEBUG: RepoDB initialized in 6.246566772460938e-05.
Warning: Safety switch: The component system.base cannot be found.
DEBUG: PackageDB initialized in 9.870529174804688e-05.
Error: System error. Program terminated.
Error: <class 'Exception'>: Repo item libtool not found
Please use 'inary help' for general help.

Traceback:
  File "/usr/local/bin/inary-cli", line 82, in <module>
    cli.run_command()
  File "/usr/local/lib/python3.5/dist-packages/inary/cli/inarycli.py", line 145, in run_command
    self.command.run()
  File "/usr/local/lib/python3.5/dist-packages/inary/cli/install.py", line 105, in run
    Reactor.install(packages, ctx.get_option('reinstall') or reinstall)
  File "/usr/local/lib/python3.5/dist-packages/inary/reactor.py", line 49, in wrapper
    ret = func(*__args,**__kw)
  File "/usr/local/lib/python3.5/dist-packages/inary/reactor.py", line 389, in install
    return inary.operations.install.install_pkg_names(packages, reinstall)
  File "/usr/local/lib/python3.5/dist-packages/inary/operations/install.py", line 59, in install_pkg_names
    G_f, order = plan_install_pkg_names(A)
  File "/usr/local/lib/python3.5/dist-packages/inary/operations/install.py", line 281, in plan_install_pkg_names
    G_f.add_package(x)
  File "/usr/local/lib/python3.5/dist-packages/inary/data/pgraph.py", line 176, in add_package
    pkg1 = self.packagedb.get_package(pkg)
  File "/usr/local/lib/python3.5/dist-packages/inary/db/packagedb.py", line 87, in get_package
    pkg, repo = self.get_package_repo(name, repo)
  File "/usr/local/lib/python3.5/dist-packages/inary/db/packagedb.py", line 160, in get_package_repo
    pkg, repo = self.pdb.get_item_repo(name, repo)
  File "/usr/local/lib/python3.5/dist-packages/inary/db/itembyrepo.py", line 50, in get_item_repo
    raise Exception(_("Repo item {} not found").format(str(item)))
Error: System error. Program terminated.
Error: <class 'Exception'>: Repo item libtool not found
Please use 'inary help' for general help.

#~ sudo inary-cli info libtool --debug
Installed package:
Name                : libtool, version: 2.4.6, release: 1
Summary             : Program geliştiriciler için ortak kütüphane aracı
Description         : Libtool, program geliştiriciler için bir paylaşımlı
                      kütüphane aracıdır.
Licenses            : GPLv2
Component           : system.devel
Provides            : 
Dependencies        : gnuconfig 
Distribution        : Sulin, Dist. Release: 2018
Architecture        : x86_64, Installed Size: 3.58 MB, install.tar.xz sha1sum:
                      cb0149d7681ea4df32e8e043b48ce4a8f811a8cf
Reverse Dependencies: 

libtool package is not found in binary repositories
libtool package is not found in source repositories
```

2018-01-14 Suleyman POYRAZ <nipalensisaquila@gmail.com>
    * inary/atomicoperations.py --- STATUS: NOT FIXED ---
    In removing not asking "Do you want remove conflicted files "
    Now remove all package files and conflicted files

