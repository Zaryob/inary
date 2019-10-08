.. -*- coding: utf-8 -*-

%%%%%%%%%%%%%%%%%%%%%
Installation of Inary
%%%%%%%%%%%%%%%%%%%%%

Installation under another distro
`````````````````````````````````

If you're using another distribution, inary can be used in two ways

* to completely switch to sulin: with inary it's easy to switch to sulin without downloading and reinstalling iso
* to install programs in your userspace: Like brew package manager


Use to switch to Sulin from another distro
------------------------------------------

.. code-block:: shell

    sh ~# git clone https://github.com/SulinOS/inary.git
    sh ~# cd inary
    sh ~# python3 setup.py install
    sh ~# cd ..
    sh ~# git clone https://github.com/SulinOS/switch-sulin.git
    sh ~# cd switch-sulin
    sh ~# ./switch-sulin --interactive
    sh ~# inary rdb
    sh ~# inary cp
    sh ~# shutdown -r now

Brew-Like using
---------------

.. code-block:: shell

    sh ~$ mkdir ~/.inary
    sh ~$ git clone https://github.com/SulinOS/inary.git
    sh ~$ python3 setup.py build
    sh ~$ python3 setup.py install --root=~/.inary
    sh ~$ python3 scripts/inary-profile select brew-like
    sh ~$ inary rdb

Installation on SulinOS
```````````````````````
In the distribution of Sulin, Inary comes  preloaded.

.. note:: you can install inary fallowing steps to installing any other distro, but this could break the preloaded inary package.


Upgrade inary
`````````````
Inary allows self-updating...

.. code-block:: shell

    sh ~$ inary ur
    sh ~$ inary up inary

...or you can also upgrade it from exist cloned repository

.. code-block:: shell

    sh ~# cd inary
    sh ~# git pull
    sh ~# python3 setup.py install


Package Post install Processes
``````````````````````````````
For inary package management system, Comar has been forked and developed  and scom \
is a former inary dependency and contains pisi package configuration scripts.

Unless otherwise specified (scom script running can be ignored with using `--ignore-scom` parameter), \
scom scripts will be executed after package installation.

However, unlike in the past, existing inary allows packet processing without using scom. \
In this case, the configuration after the installation of the packages is left entirely \
to the users hand.
