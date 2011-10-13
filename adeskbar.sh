#!/bin/sh

mkdir -p ~/.config/adeskbar
/usr/share/adeskbar/main.py $@ > ~/.config/adeskbar/output.log 2>&1
