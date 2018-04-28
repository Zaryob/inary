PROJECT (helloworld)

# CMake 2.6 required
CMAKE_MINIMUM_REQUIRED(VERSION 2.6)

# Python is required

FIND_PACKAGE(PkgConfig)

# Application name
SET (APP_NAME "helloworld")
SET (APP_SUFFIX "2")

# Uncomment this for production releases.
SET (VERSION_SUFFIX "")
#SET (FLAGS "-g -O0 -Wcast-align -Wno-uninitialized -Wall -fstrict-aliasing")

SET (FLAGS "-g -O0 -Wno-uninitialized -Wall -fstrict-aliasing")
# Uncomment this for gprof profiling
# SET (FLAGS "-g -O0 -Werror -Wcast-align -Wno-uninitialized -Wall -fstrict-aliasing -fprofile-arcs -ftest-coverage")
SET (CMAKE_C_FLAGS "${FLAGS}")
# Uncomment this for sparse building
# SET (CMAKE_C_COMPILER cgcc)

# Append name suffix, if specified
IF (APP_SUFFIX)
   SET (APP_NAME "${APP_NAME}${APP_SUFFIX}")
ENDIF (APP_SUFFIX)

INCLUDE_DIRECTORIES (include/)
# Define version, config dir, data dir and log file.
SET (SOURCES  src/helloworld.cxx
              src/utility.cxx)


# Compile scom from specified sources
ADD_EXECUTABLE (helloworld ${SOURCES})

# Install scom to /usr/bin/<app-name>
INSTALL (PROGRAMS helloworld
         DESTINATION /usr/bin)
