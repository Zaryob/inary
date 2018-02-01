### Importing 
----------------------------------------

`from inary.system_literals import $module_name`


## Module 'strutils'
----------------------------------------
# string/list/functional utility functions

* any (pred,seq)

* concat (l):
  Concatenate a list of lists.

* every (pred,seq)

* human_readable_rate (size)

* human_readable_size (size)

* multisplit (str,chars):
  Split str with any of the chars.

* prefix (a,b):
  Check if sequence a is a prefix of sequence b.

* remove_prefix (a,b):
  Remove prefix a from sequence b.

* same (l):
  Check if all elements of a sequence are equal.

* strlist (l):
  Concatenate string reps of l's elements.

* unzip (seq)



## Module 'dirutils'
----------------------------------------
# dirutils module provides basic directory functions.

* dir_size (dir)
  Calculate the size of files under a directory.

* remove_dir (path)
  Remove all content of a directory.



## Module 'sysutils'
----------------------------------------
# sysutils module provides basic system utilities.

* FileLock class:
  Create a file lock for operations

* find_executable (exec_name)

* find the given executable in PATH

* getKernelOption (option):
  Get a dictionary of args for the given kernel command line option

* touch (filename):
  Update file modification date, create file if necessary

* capture ()
  Capture output of the command without running a shell

* run ()
  Run a command without running a shell, only output errors

* run_full ()
  Run a command without running a shell, with full output

* run_quiet ()
  Run the command without running a shell and no output


## Module 'csapi'
----------------------------------------
# csapi module provides basic system configuration utility function.

* atoi():
  Convert a string into an integer.

* settimeofday():
  Set system date.

* changeroute():
  Change the route table.



## Module 'iniutils'
----------------------------------------
# initutils module provides ini style configuration file utils.


## Module 'diskutils'
----------------------------------------
# diskutils module provides EDD class to query device boot order and device information utilities.



## Module 'localedata'
----------------------------------------
# localedata module provides locale information.



## Module 'localedata'
----------------------------------------
# network utility functions
