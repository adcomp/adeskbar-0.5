#!/bin/bash

## Create deb package for ADeskBar
## David [a.k.a] ADcomp < david.madbox@gmail.com >
## http://www.adeskbar.tuxfamily.org/

VERSION=`grep ^VERSION src/adesk/release.py | awk $'{print $3}'`
RC=`grep ^RC src/adesk/release.py | awk $'{print $3}'`
ARCH="all"
DIR_TEMP=".deb"
PWD=$(echo `pwd`)
TMP=$PWD

hello() {
    echo -e "\n ### ADeskBar Deb Tool ###\n"
}
status()
{
    local CHECK=$?
    echo -en "\\033[70G[ "
    if [ $CHECK = 0 ]; then
        echo -en "\\033[1;32mOK"
    else
        echo -en "\\033[1;31mKO"
    fi
    echo -e "\\033[0;39m ]"
}

log_info() {
    echo -en "\t" $1
}

## remove *.pyc
pyc=$(find . -name '*.pyc')
for file in $pyc; do rm $file; done

## if exist , remove directory
log_info "  - remove temp directory if exist .."
rm -rf $DIR_TEMP
status

## create directory
log_info "  - create directory .."
( mkdir $DIR_TEMP ;
mkdir -p $DIR_TEMP/usr/share/adeskbar ;
mkdir -p $DIR_TEMP/usr/bin ;
mkdir -p $DIR_TEMP/usr/share/pixmaps ;
mkdir -p $DIR_TEMP/usr/share/applications ;
mkdir $DIR_TEMP/DEBIAN ; )
status

## config
log_info "  - copy debian config .."
echo "Package: adeskbar" > $DIR_TEMP/DEBIAN/control
echo "Version: $VERSION-$RC" >> $DIR_TEMP/DEBIAN/control
echo "Section: utils" >> $DIR_TEMP/DEBIAN/control
echo "Priority: optional" >> $DIR_TEMP/DEBIAN/control
echo "Architecture: $ARCH" >> $DIR_TEMP/DEBIAN/control
echo "Depends: python (>=2.4), python-gtk2, python-wnck, python-xdg, python-xlib" >> $DIR_TEMP/DEBIAN/control
echo "Recommends: python-vte, python-alsaaudio, python-pyinotify, python-dbus, python-keybinder" >> $DIR_TEMP/DEBIAN/control
echo "Maintainer: David Art (david.madbox@gmail.com)" >> $DIR_TEMP/DEBIAN/control
echo "Description: ADeskBar - application launcher for Openbox" >> $DIR_TEMP/DEBIAN/control
status

## copy application
log_info "  - copy application"
(
cp -a src/* $DIR_TEMP/usr/share/adeskbar/
cp src/images/adeskbar.png $DIR_TEMP/usr/share/pixmaps/
cp adeskbar.desktop $DIR_TEMP/usr/share/applications/
cp adeskbar.sh $DIR_TEMP/usr/bin/adeskbar
)
status

## files should be ROOT ?
chown -R root: $DIR_TEMP

## create package
log_info "  - create package .."
( rm -rf adeskbar.$VERSION.$RC-$ARCH.deb ;
dpkg-deb --build $DIR_TEMP adeskbar.$VERSION.$RC-$ARCH.deb > /dev/null 2>&1 ;
chmod a+rw adeskbar.$VERSION.$RC-$ARCH.deb )
status

## remove temp directory
log_info "  - remove temp directory .."
rm -rf $DIR_TEMP
status

log_info " # Package ready : adeskbar.$VERSION.$RC.deb\n\n"

