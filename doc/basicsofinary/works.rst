.. -*- coding: utf-8 -*-

=============================
How inary transactions works?
=============================

Inary generates own database for package installation, uninstall and all other package operations. \
The database of inary is generated with using `index.xml` file, metadata's of installed packages and package \
content list of the installed packages. Inary database is based on 3 main foundations.

    * installdb: Consists of all installed packages and their datas.
    * packagedb: Consists of all packages in remote or local repositories.
    * repodb: Consists of repository uri and details.

These database files are created and edited by inary. These database files are created automatically \
when a break or corruption is detected. Database files only contain some ways to secure installation. \
So you can sit back and sip your coffee without fear of databases.

When any install operation is triggered, inary first checks the installdb to see if the package is \
installed, if it is not installed, it finds the repository containing the most package from the repodb. \
When all the process is done, the package is added to the installdb.

Removal is simpler. The reverse dependencies of the package are added to the deletion queue, the list of \
files is removed, the packages are removed from the system and the packages are removed from the installdb.

Summing up these procedures may seem intimidating to you, but the purpose of summarizing this is to brag \
about making these processes very fast and 100% lossless :smile:

Package managers usually consist of two parts. such as dpkg and apt coexistence or yum and rpm. However, \
inary supports all users from the end user to the developer through the same library and the same cli. We \
also force any user into some cases to prevent unnecessary errors and problems. For example, even the \
freedom to blow up your system is gived by inary (only with "--ignore-safety" parameter)

However, we will go into a little more details, if you are afraid of the details, you can continue with \
how to set up the program for the shiftlesses.

**XML and Why I used?**
-----------------------

It has a metadata management style that uses XML files. Extensible Markup Language (XML) is a markup language. \
Isn't it pretty descriptive? That is, a structural-language created for you to easily create the tree directory \
structure using markups.
Although it seems difficult to read and write by hand (which we can do), it has a structure that can be manipulated \
quickly and at 100% stability using appropriate libraries. Indeed, the similarity to the HTML language (even the use \
of the same syntax) facilitates our work on the web side.
It also works as well as a plain text file when compressed. And it saves us the trouble of
analyzing packet data with complex commands like sed grep awk and other regexes.

Package building process is the festivity of the houses. it consists of two package files, `pspec.xml` and `actions.py`. \
I will explain them in more detail is just preliminary information. Using them, the packages are compiled independently \
from the outside world by providing python shell isolation. In this way, the packages can sleep in their packs without \
being affected by the absurd environment variables.

We said that everything is created by inary except pspec.xml for packages. It certainly is. Metadata and files data of \
the packages are derived from this.
Analyzing all the packages and writing the warehouse index is also done with a command of inary. Opensuse must have \
been suffering to do this :smile:.

Another point is that while doing this, no hand intervention actually permits. So this is good news when there are tons \
of packages that are wasted as a result of each packer's own style. At the very least, the new packager does not have \
to examine the codes that are broken from someone else's fantasy world.

**Well, What about XML files slowly read?**
-------------------------------------------

This is actually caused by armament xml parsers that are printed to developers. we have created a C-based parser to \
overcome this. After all, I stated that we are about 950% faster to the git repository.

**How to ensure stability?**
----------------------------

The rest comes when it meets certain standards for the steps to be taken outside the package specifications.

**Auxiliary Operations**
------------------------

If you are just a standard user who installs and updates packages, install remove and upgrade is sufficient for you. \
But not everyone's needs are the same. Some of them have fetishes on package management. Since we know this, there are \
many commands that can be used to clean the packages (including runtime deps) from your files, to clean up the stray \
packages. It might be nice to tamper with the `inary help` command.

**Okay, other punches?**
------------------------

There are many features to use the git repository as a repository (but pushing the packages is a bit annoying), \
from encrypting repositories, even packages with the gpg key. I will continue to call these as the place for each command.