#!/bin/bash

for PO in *.po; do
    DIR=${PO/.po/}
    echo $DIR
    mkdir -p ../locale/$DIR/LC_MESSAGES
    #~ echo "msgfmt --output-file=../locale/$DIR/LC_MESSAGES/adeskbar.mo $PO"
    msgfmt --output-file=../locale/$DIR/LC_MESSAGES/adeskbar.mo $PO
done
