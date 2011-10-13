# -*- coding: utf-8 -*-
#
#  ADesk Bar - Check
#
#  by ADcomp <david.madbox@gmail.com>
#  http://www.ad-comp.be/
#
#  This program is distributed under the terms of the GNU General Public License
#  For more info see http://www.gnu.org/licenses/gpl.txt
##

import gtk
import release

check = {
    'WNCK':[True, 'python-wnck'],
    'ALSA':[True, 'python-alsaaudio'],
    'VTE ':[True, 'python-vte'],
    'DBUS':[True, 'python-dbus'],
    'XLIB':[True, 'python-xlib'],
    'KEYBINDER':[True, 'python-keybinder'],
    'GIO':[True, 'python-gio'],
    'PYINOTIFY':[True, 'python-pyinotify'],
    }
    
modules = {
    'python-wnck': ('tasklist','intellihide','showdesktop'),
    'python-alsaaudio': ('volume',),
    'python-vte': ('terminal',),
    'python-dbus': ('** not yet implemented ** :)',),
    'python-xlib': ('systray',),
    'python-keybinder': ('global key bindings for applications',),
    'python-gio': ('interfaces and base classes for I/O and files',),
    'python-pyinotify': ('monitoring filesystems changes',)    
    }

def run():
    # Create window
    window = gtk.Window() #gtk.WINDOW_TOPLEVEL)
    title = 'Check python modules'
    window.set_title("ADeskBar - %s" % title)
    window.set_position(gtk.WIN_POS_CENTER)
    window.connect("destroy", destroy)
    window.set_icon_from_file('images/adeskbar.png')
    window.set_border_width(20)
    
    box = gtk.VBox(False, 15)
    window.add(box)
    check_modules(box)
    
    window.show_all()
    gtk.main()

def destroy(widget):
    widget.destroy()
    gtk.main_quit()

def check_modules(box):
    try:
        import wnck
    except:
        check['WNCK'][0] = False
    try:
        import alsaaudio as alsa
    except:
        check['ALSA'][0] = False
    try:
        import vte
    except:
        check['VTE'][0] = False
    try:
        import dbus
    except:
        check['DBUS'][0] = False
    try:
        import Xlib
    except:
        check['XLIB'][0] = False
    try:
        import keybinder
    except:
        check['KEYBINDER'][0] = False
    try:
        import gio
    except:
        check['GIO'][0] = False
    try:
        import pyinotify
    except:
        check['PYINOTIFY'][0] = False

    ind = 0
    max_ind = len(check)-1
    
    for mod in check:
        
        sub_box = gtk.HBox()

        label = gtk.Label()
        label.set_use_markup(True)
        label.set_markup("<small>checking .. :</small> <b><i>%s</i></b>" % check[mod][1])
        label.set_alignment(0,0.5)
        sub_box.pack_start(label, False, False)

        if not check[mod][0]:
            img = gtk.image_new_from_file('images/check/ko.svg')
        else:
            img = gtk.image_new_from_file('images/check/ok.svg')

        sub_box.pack_end(img, False, False)
        box.pack_start(sub_box, False, False)

        temp = "<small>required for</small> : <i>"
        
        for plugin in modules[check[mod][1]]:
            #~ print plugin,
            temp +=  plugin + ' ,  '
            
        if temp[-4:] == ' ,  ':
            temp = temp[:-4]
            
        temp += "</i>"
        
        label = gtk.Label(temp)
        label.set_use_markup(True)
        label.set_markup(temp)
        label.set_alignment(0,0.5)
        box.pack_start(label, False, False)
        
        if ind < max_ind:
            box.pack_start(gtk.HSeparator(), False, False)
            
        ind += 1
