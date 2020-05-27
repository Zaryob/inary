for managing CFLAGS, CXXFLAGS and LDFLAGS you can use inarytools
for CFLAGGS -> inarytools.cflags
for LDFLAGGS -> inarytools.ldflags
for CXXFLAGGS -> inarytools.cxxflags
for both CFLAGGS and CXXFLAGS -> inarytools.flags

available operations:

add("param1", "param2", ..., "paramN")
e.g.
inarytools.cxxflags.add("-fpermisive")
-> shelltools.export("CXXFLAGS", "{} -fpermisive".format(get.CXXFLAGS()))
inarytools.flags.add("-fno-strict-aliasing", "-fPIC")
-> shelltools.export("CFLAGS", "{} -fno-strict-aliasing -fPIC".format(get.CFLAGS()))
-> shelltools.export("CXXFLAGS", "{} -ffno-strict-aliasing -fPIC".format(get.CXXFLAGS()))

remove("param1", "param2", ..., "paramN")
e.g.
inarytools.cflags.remove("-fno-strict-aliasing")
-> shelltools.export("CFLAGS", get.CFLAGS().replace("-fno-strict-aliasing", ""))

replace("old value", "new value")
e.g.
inarytools.cflags.replace("-O2", "-O3")
-> shelltools.export("CFLAGS", get.CFLAGS().replace("-O2", "-O3"))

sub(pattern, repl, count, flags)
works like re.sub(pattern, repl, string, count, flags) for specified flags
e.g.
inarytools.cflags.replace(r"-O\d", "-Os")
-> import re
-> shelltools.export("CFLAGS", re.sub(r"-O\d", "-Os", get.CFLAGS()))
