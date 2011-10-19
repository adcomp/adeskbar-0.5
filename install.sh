#!/bin/sh

##
#  Install ADeskBar
## David [a.k.a] ADcomp < david.madbox@gmail.com >
## http://www.adeskbar.tuxfamily.org/
##

## remove *.pyc
pyc=$(find . -name '*.pyc')
for file in $pyc; do rm $file; done

## copy files
rm -rf /usr/share/adeskbar
mkdir /usr/share/adeskbar
cp -a src/*  /usr/share/adeskbar
chown -R root: /usr/share/adeskbar
cp src/images/adeskbar.png /usr/share/pixmaps
cp adeskbar.desktop /usr/share/applications
cp src/main.py /usr/bin/adeskbar
