.. -*- coding: utf-8 -*-

==========
inary help
==========

`inary help` comand gives information about all inary commands and options.

**Using**
---------

.. code-block::

              sh ~$ inary help
              sh ~$ inary ?

**Output**
---------------

.. code-block::

              sh ~$ inary help
              usage: inary [options] <command> [arguments]

              where <command> is one of:

                         add-repo (ar) - Add a repository
                            blame (bl) - Information about the package owner and release
                            build (bi) - Build INARY packages
                                 check - Verify installation
                   config-manager (cm) - Inary Config file manager.
                configure-pending (cp) - Configure pending packages
                     delete-cache (dc) - Delete cache files
                            delta (dt) - Creates delta packages
                     disable-repo (dr) - Disable repository
                           emerge (em) - Build and install INARY source packages from repository
                       emergeup (emup) - Build and upgrade INARY source packages from repository
                      enable-repo (er) - Enable repository
                            fetch (fc) - Fetch a package
                                 graph - Graph package relations
                              help (?) - Prints help for given commands
                          history (hs) - History of inary operations
                            index (ix) - Index INARY files in a given directory
                                  info - Display package information
                          install (it) - Install INARY packages
                   list-available (la) - List available packages in the repositories
                  list-components (lc) - List available components
                   list-installed (li) - Print the list of all installed packages
                      list-newest (ln) - List newest packages in the repositories
                    list-orphaned (lo) - List orphaned packages
                     list-pending (lp) - List pending packages
                        list-repo (lr) - List repositories
                     list-sources (ls) - List available sources
                    list-upgrades (lu) - List packages to be upgraded
                      rebuild-db (rdb) - Rebuild Databases
                           remove (rm) - Remove INARY packages
                  remove-orphaned (ro) - Remove orphaned packages
                      remove-repo (rr) - Remove repositories
                           search (sr) - Search packages
                      search-file (sf) - Search for a file
                      update-repo (ur) - Update repository databases
                          upgrade (up) - Upgrade INARY packages

              Use "inary help <command>" for help on a specific command.


              Options:
               --version                    : show program's version number and exit
               -h [--help]                  : show this help message and exit

               general options:
                -D [--destdir] arg          : Change the system root for INARY commands.
                -y [--yes-all]              : Assume yes in all yes/no queries.
                -u [--username] arg
                -p [--password] arg
                -L [--bandwidth-limit] arg  : Keep bandwidth usage under specified KB's.
                -v [--verbose]              : Detailed output
                -d [--debug]                : Show debugging information.
                -N [--no-color]             : Suppresses all coloring of INARY's output.
