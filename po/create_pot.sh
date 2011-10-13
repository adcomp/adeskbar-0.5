#!/bin/sh

rm adeskbar.pot
xgettext -k_ -kN_ -o adeskbar.pot ../adesk/barconf.py --language=Python
