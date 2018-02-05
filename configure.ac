# autoconf base script to create configuration file
# for raspbian_devfs
#
# raspbain_devfs is intended to be run under linux
#    ubuntu, (it uses apt-get, so it assumes the availability of this command 
#             to do the lifting)
#    for the raspian system and then download and install packages
#    locally under chroot.  
#
#    normally one would use this technique to build a rootfs for a network
#    booted system but in this case we will use this technique install libraries.
#    and development header files into this rootfs, so we can reference them 
#    from a cross environment.
#
#  if we wish to do this without the apt-get in ubuntu then it will get more compicated
#  as we need to make scripts to unpack the data and create the package graph
#  and then perform the downloads and unpacking of the files to set things up..
#
# 
AC_INIT(raspbian_devfs, version-0.1)
AC_MSG_NOTICE([Hello, world.])

# apt get does not appear to have a redirect method...
AC_CHECK_PROG(APT_GET_CHECK,python3,yes)
if test x"$APT_GET_CHECK" != x"yes" ; then
    AC_MSG_ERROR([apt-get is required to make this program work.])
fi

#AC_CHECK_PROG(APT_GET_CHEC7,apt-get,yes)
#if test x"$APT_GET_CHECK" != x"yes" ; then
#    AC_MSG_ERROR([apt-get is required to make this program work.])
#fi



AC_PREFIX_DEFAULT(["`pwd`/build"])


AC_CONFIG_FILES([
 Make.rules
])

AC_OUTPUT

    
