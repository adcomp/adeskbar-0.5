#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    ADesk Bar - application launcher for openbox
#       
#    Copyright 2009-2011 ADcomp <david.madbox@gmail.com>
#
#    http://adeskbar.tuxfamily.org
#       
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#       
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#       
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#    MA 02110-1301, USA.
#       

import os
import os.path
import sys

DEFAULT_INSTALL_PATH = '/usr/share/adeskbar'
sys.path.append(DEFAULT_INSTALL_PATH)

def gtkrc_changed (monitor, file, data, event, bar_mgr):
    bar_mgr.resize_and_seticon()
    
realpath = os.path.dirname(os.path.realpath( __file__ ))
os.chdir(realpath)

if os.path.exists('adesk') and os.path.isdir('adesk'):
    # do nothing .. 
    pass
else:
    os.chdir(DEFAULT_INSTALL_PATH)

## parse argument
if len(sys.argv) == 1:
    cfg_file = 'default'
elif len(sys.argv) == 2:
    cfg_file = sys.argv[1]
else:
    cfg_file = '-h'

## show usage .. 
if cfg_file == '--help' or cfg_file == '-h':
    import adesk.release as release

    print('ADeskBar v%s.%s' % (release.VERSION, release.RC))
    print 
    print('Usage : adeskbar [config_name]')
    print
    sys.exit(0)

## let's go ..
import adesk.bar
bar_mgr = adesk.bar.BarManager(cfg_file)

### !! if I move this in BarManager.init , no callback .. why ?
try:
    import gio
    home = os.environ['HOME']
    file = gio.File( home + '/.gtkrc-2.0')
    monitor = file.monitor_file()
    monitor.connect ("changed", gtkrc_changed, bar_mgr)
except:
    pass
    # no update if gtk theme change ..
    
bar_mgr.run()
