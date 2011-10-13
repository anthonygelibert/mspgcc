#!/bin/sh
# Author: Anthony Gelibert <anthony.gelibert@lcis.grenoble-inp.fr>

[ "root" = "`whoami`" ] && echo "Being root in all the build process isn't a good idea" && exit 1

num_cpus() {
	local tmp;

    case $(uname -s) in
        Darwin)
            tmp="`sysctl -n hw.availcpu 2> /dev/null`";;
		FreeBSD)
            tmp="`sysctl -n hw.ncpu 2> /dev/null`";;
		Linux|CYGWIN_NT*)
			tmp="`grep ^processor /proc/cpuinfo 2>/dev/null| wc -l`";;
		*)	tmp=1;;
	esac
	[ $tmp = 0 ] && tmp=1;
    echo "${tmp}";
}


clear

BINUTILS_VERSION="`ls | grep binutils | tail -1 | cut -f3 -d-`"
echo "version : $BINUTILS_VERSION"
BINUTILS="binutils-$BINUTILS_VERSION"
echo "filename : $BINUTILS"
BINUTILS_PATCH="`ls | grep $BINUTILS `"
echo "patch files : $BINUTILS_PATCH"

BUILDDATE="`date '+%Y%m%d'`"
BUILDDIR="$PWD/build"

GCC_VERSION="`ls | grep gcc | tail -1 | cut -f3 -d-`"
TARGETDIR="/opt/msp430-gcc-$GCC_VERSION"
echo "target Directory : $TARGETDIR"

MIRROR_BINUTILS="ftp://sources.redhat.com/pub/binutils/releases"

NUM_CPU=$(num_cpus);

TAR_GZIP=xzf
TAR_BZIP=xjf

echo "/----------------------------+"
echo "|  build and install script |"
echo "+----------------------------/\n"

echo "I will compile:"
echo "  - Binutils:    $BINUTILS_VERSION"

echo "Build settings:"
echo "  - Build dir:  $BUILDDIR"
echo "  - Target dir: $TARGETDIR"
echo "  - Binutils:   $MIRROR_BINUTILS/$BINUTILS"

echo "Build order: binutils, gcc, gdb, mcu, libc\n"

mkdir $BUILDDIR 2> /dev/null

cd $BUILDDIR
echo "###############################################################################"
echo "##  msp430-binutils ($BINUTILS_VERSION)"
echo "###############################################################################"
echo "## Clean"
sudo rm -rf $BINUTILS
sudo rm -rf $BINUTILS-build
echo "## Download"
if [ ! -e $BINUTILS.tar.gz ]; then
    wget $MIRROR_BINUTILS/$BINUTILS.tar.gz
    if [ $? -ne 0 ]; then
        echo "I can't download Binutils $BINUTILS_VERSION from $MIRROR_BINUTILS/$BINUTILS.tar.gz";
        exit 1;
    fi
fi
echo "## Unpacking"
tar $TAR_GZIP $BINUTILS.tar.gz


for file in $BINUTILS_PATCH 
do 
  (echo "## Patch with : $file "; cd $BINUTILS; patch -p1 < ../../$file)
done

mkdir -p "$BINUTILS-build"
cd "$BINUTILS-build"
pwd

echo "## Configure"
../$BINUTILS/configure --target=msp430 --disable-werror --disable-nls --prefix="$TARGETDIR"
echo "## Build for $NUM_CPU"
make -j$NUM_CPU
echo "## Install"
echo "Note: I will request your root password to install in the target directory"
sudo make -j$NUM_CPU install


