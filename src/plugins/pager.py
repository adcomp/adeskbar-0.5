#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2010, Philip Busch <vzxwco@gmail.com>
See License.txt for details.
__appname__ = 'neap'
__author__ = ['Philip Busch <philip@0xe3.com>', 'Clément Lavoillotte']
__version__ = '0.6.3'
__license__ = 'BSD'
__website__ = 'http://code.google.com/p/neap/'
"""

import sys
import os
import re
import math
import ConfigParser
from datetime import datetime
from optparse import OptionParser

import gtk
import gobject
from Xlib import X, display, error, Xatom, Xutil
import Xlib.protocol.event

import adesk.plugin as Plg
import adesk.core as Core
import adesk.ui as UI


class Pager:
    '''Dummy pager, not intended to be used directly'''
    
    def __init__(self, display, screen, root):
        '''Initialization.'''
        
        self.display = display
        self.screen = screen
        self.root = root

    def get_desktop_tasks(self, num):
        '''Returns a list of tasks for desktop num.'''

        return self.root.get_full_property(self.display.get_atom('_NET_CLIENT_LIST'), Xatom.WINDOW).value

    def get_current_desktop(self):
        '''Returns the index of the currently active desktop.'''
        
        return 0

    def get_desktop_layout(self):
        '''Returns a tupel containing the number of rows and cols, from the window manager.'''
        
        return (1,1)

    def get_desktop_count(self):
        '''Returns the current number of desktops.'''

        return 1

    def get_desktop_names(self):
        '''Returns a list containing desktop names.'''

        return ['Desktop']

    def switch_desktop(self, num):
        '''Sets the active desktop to num.'''

        pass

    def send_event(self, win, ctype, data, mask=None):
        '''Sends a ClientMessage event to the root window.'''

        data = (data + [0] * (5 - len(data)))[:5]
        ev = Xlib.protocol.event.ClientMessage(window=win,
                client_type=ctype, data=(32, data))

        if not mask:
            mask = X.SubstructureRedirectMask | X.SubstructureNotifyMask
        self.root.send_event(ev, event_mask=mask)


class VirtualDesktopPager(Pager):
    '''Virtual desktop / workspace -based pager. Should be used with most freedesktop-compliant window managers.'''
    
    def get_current_desktop(self):
        '''Returns the index of the currently active desktop.'''

        return self.root.get_full_property(self.display.get_atom('_NET_CURRENT_DESKTOP'), 0).value[0]

    def get_desktop_layout(self):
        '''Returns a tupel containing the number of rows and cols, from the window manager.'''

        grid = self.root.get_full_property(self.display.get_atom('_NET_DESKTOP_LAYOUT'), 0)

        rows = 0
        cols = 0

        if grid != None and grid.value[2] > 1 and grid.value[1] > 1:
            # if _NET_DESKTOP_LAYOUT has sane values, use them:
            rows = grid.value[2]
            cols = grid.value[1]
        else:
            # else compute nice defaults:
            count = self.get_desktop_count()
            rows = round(math.sqrt(count))
            cols = math.ceil(math.sqrt(count))

        return (int(rows), int(cols))

    def get_desktop_count(self):
        '''Returns the current number of desktops.'''

        return self.root.get_full_property(self.display.get_atom('_NET_NUMBER_OF_DESKTOPS'), 0).value[0]

    def get_desktop_names(self):
        '''Returns a list containing desktop names.'''

        count = self.get_desktop_count()
        names = self.root.get_full_property(self.display.get_atom('_NET_DESKTOP_NAMES'), 0)

        if hasattr(names, 'value'):
            count = self.get_desktop_count()
            names = names.value.strip('\x00').split('\x00')[:count]
        else:
            names = []
            for i in range(count):
                names.append(str(i))

        if len(names) < count:
            for i in range(len(names), count):
                names.append(str(i))

        return names

    def switch_desktop(self, num):
        '''Sets the active desktop to num.'''

        win = self.root
        ctype = self.display.get_atom('_NET_CURRENT_DESKTOP')
        data = [num]

        self.send_event(win, ctype, data)
        self.display.flush()


class ViewportPager(Pager):
    '''Viewport-based pager. To be used with compiz and other viewport-based window managers.'''

    def get_sreen_resolution(self):
        '''Returns a tupel containing screen resolution in pixels as (width, height).'''
        
        return (self.screen.width_in_pixels, self.screen.height_in_pixels)

    def get_current_desktop(self):
        '''Returns the index of the currently active desktop.'''

        w,h = self.get_sreen_resolution()
        rows,cols = self.get_desktop_layout()
        vp = self.root.get_full_property(self.display.get_atom("_NET_DESKTOP_VIEWPORT"), 0).value
        return round(vp[1]/h)*cols + round(vp[0]/w);

    #TODO: optimize (cache ?)
    def get_desktop_layout(self):
        '''Returns a tupel containing the number of rows and cols, from the window manager.'''

        w,h = self.get_sreen_resolution()
        size = self.root.get_full_property(self.display.get_atom("_NET_DESKTOP_GEOMETRY"), 0)

        #default values
        rows = 1
        cols = 1

        if size != None:
            rows = round(size.value[1] / h)
            cols = round(size.value[0] / w)
        
        return (int(rows), int(cols))

    def get_desktop_count(self):
        '''Returns the current number of desktops.'''

        rows,cols = self.get_desktop_layout()
        return rows * cols

    def get_desktop_names(self):
        '''Returns a list containing desktop names.'''

        count = self.get_desktop_count()
        names = []
        for i in range(count):
            names.append('Workspace {0}'.format(i+1))

        return names

    def switch_desktop(self, num):
        '''Sets the active desktop to num.'''

        w,h = self.get_sreen_resolution()
        rows,cols = self.get_desktop_layout()
        x = int(num % cols)
        y = int(round((num-x)/cols))
        data = [x*w, y*h]
        
        win = self.root
        ctype = self.display.get_atom("_NET_DESKTOP_VIEWPORT")

        self.send_event(win, ctype, data)
        self.display.flush()


def pager_auto_detect(display, screen, root):
    '''Auto-detects pager to use.'''
    pager = None
    
    grid = root.get_full_property(display.get_atom('_NET_DESKTOP_LAYOUT'), 0)
    size = root.get_full_property(display.get_atom("_NET_DESKTOP_GEOMETRY"), 0)
    
    if (grid != None and grid.value[2] > 1 and grid.value[1] > 1):
        return VirtualDesktopPager(display, screen, root)
    elif (hasattr(size, 'value') and (size.value[1]>screen.height_in_pixels or size.value[0]>screen.width_in_pixels)):
        return ViewportPager(display, screen, root)
    else:
        # defaults to VirtualDesktop
        return VirtualDesktopPager(display, screen, root)


PAGERS = {'virtual': VirtualDesktopPager, 'viewport':ViewportPager, 'auto':pager_auto_detect}


class NeapConfig(object):

    def __init__(self):
        '''Initialization.'''

        # default config
        self.conf = {}
        self.conf['padding'] = 2
        self.conf['spacing'] = 2
        self.conf['color_active'] = '#7F7F7F'
        self.conf['color_inactive'] = '#44494C'
        self.conf['color_background'] = '#2357bd'
        self.conf['rows'] = 0
        self.conf['columns'] = 0
        self.conf['pager'] = 'auto'

    def __setitem__(self, key, val):
        '''Sets config variable key to val.'''

        self.set(key, val)

    def __getitem__(self, key):
        '''Returns the value of config variable key.'''

        return self.conf[key]

    def set(self, key, val):
        '''Sets config variable key to val, including sanity-check.'''

        # discard empty values
        if val == None:
            return False

        if key == 'pager':
            return (key in PAGERS)

        # is val a number, a hex color or the string "transparent"?
        if not (val == "transparent" or
                re.match("#[a-fA-F0-9]{6}", val) != None or
                val.isdigit()):
            return False

        try:
            val = int(val)
        except ValueError:
            pass

        if val == 'transparent':
            val = '#2357bd'

        if key not in self.conf.keys():
            return False

        self.conf[key] = val

        return True

class Neap(object):

    def __init__(self, config, plugin, bar):
        '''Initialization.'''

        self.plugin = plugin
        self.bar = bar
        
        # default config
        self.conf = config
        self.grid = []

        # X stuff
        self.display = display.Display()
        self.screen = self.display.screen()
        self.root = self.screen.root

        # select pager
        self.pager = PAGERS[self.conf['pager']](self.display, self.screen, self.root)

        # notify about and handle workspace switches
        screen = gtk.gdk.screen_get_default()
        root = screen.get_root_window()
        root.set_events(gtk.gdk.SUBSTRUCTURE_MASK)
        root.add_filter(self.event_filter)

        # initialize data
        self.old_active = -2
        self.count = -2
        self.layout = (-2, -2)

        self.icon = gtk.Image()
        self.plugin.add(self.icon)
        
        self.init_size()

    def init_size(self):
        icon_size = self.bar.cfg['icon_size']
        self.colormap = gtk.gdk.Colormap(gtk.gdk.visual_get_best(), False)
        self.color_active = self.colormap.alloc_color(self.conf['color_active'])
        self.color_inactive = self.colormap.alloc_color(self.conf['color_inactive'])
        self.color_background = self.colormap.alloc_color(self.conf['color_background'])
        self.pixmap = gtk.gdk.Pixmap(None, icon_size, icon_size, 32)
        self.gc = self.pixmap.new_gc()
        self.pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, icon_size, icon_size)
        self.pixbuf.fill(0xffffffff)
        self.pixbuf = self.pixbuf.add_alpha(True, 0xFF, 0xFF, 0xFF)
        
        self.icon.set_size_request(icon_size, icon_size)
        #~ self.update_grid()
        self.update_pixbuf()
        
    def event_filter(self, event, user_data=None):
        '''Handles incoming gtk.gdk.Events.'''

        # we only registered for SUBSTRUCTURE_MASK events, so
        # we just update the pixbuf
        self.update_pixbuf(self.pager.get_current_desktop())
        return gtk.gdk.FILTER_CONTINUE

    def get_icon_desktop_layout(self):
        '''Returns a tupel containing the number of rows and cols, for the pager icon.'''

        if self.conf['rows'] > 0 and self.conf['columns'] > 0:
            # if .neaprc config variables are set, enforce them:
            rows = self.conf['rows']
            cols = self.conf['columns']
            return (rows, cols)
        else:
            # else icon layout = window manager's desktop layout
            return self.pager.get_desktop_layout()

    def update_grid(self):
        '''Updates internal grid structure. Returns False if the grid did not need to be updated.'''

        (rows, cols) = self.get_icon_desktop_layout()
        count = self.pager.get_desktop_count()
        #~ if ((rows, cols) == self.layout and count == self.count):
            #~ return False
        self.layout = (rows, cols)
        self.count = count
        
        (w, h) = (self.bar.cfg['icon_size'], self.bar.cfg['icon_size'])
        padding = self.conf['padding']
        spacing = self.conf['spacing']

        n = max(rows, cols)
        c = (w - 2 * padding - (n - 1) * spacing) / cols

        grid_width = cols * c + (cols - 1) * spacing
        grid_height = rows * c + (rows - 1) * spacing

        off_x = (w - 2 * padding - grid_width) / 2
        off_y = (h - 2 * padding - grid_height) / 2

        grid = []
        for i in range(rows):
            for j in range(cols):
                x = off_x + padding + j * (c + spacing)
                y = off_y + padding + i * (c + spacing)

                if i * cols + j < count:
                    grid.append((x, y, c, c))

        self.grid = grid
        return True

    def update_pixbuf(self, active=-1):
        '''Updates internal icon pixbuf.'''

        if (self.update_grid() is False and self.old_active == active):
            return

        self.old_active = active

        (w, h) = (self.bar.cfg['icon_size'], self.bar.cfg['icon_size'])
        
        # ---ACTUAL DRAWING CODE---
        self.gc.set_foreground(self.color_background)
        self.pixmap.draw_rectangle(self.gc, True, 0, 0, w, h)

        self.gc.set_foreground(self.color_inactive)

        i = 0
        for cell in self.grid:
            if i == active:
                self.gc.set_foreground(self.color_active)
            else:
                self.gc.set_foreground(self.color_inactive)

            i = i + 1

            (x, y, size_x, size_y) = cell
            self.pixmap.draw_rectangle(self.gc, True, x, y, size_x, size_y)
        # -------------------------

        self.pixbuf.get_from_drawable(self.pixmap, self.colormap, 0, 0, 0, 0, w, h)
        self.pixbuf = self.pixbuf.add_alpha(True, chr(0x23), chr(0x57), chr(0xbd))
        self.icon.set_from_pixbuf(self.pixbuf)

    def scroll(self, widget, event):
        '''Callback for scroll wheel actions.'''

        if event.direction == gtk.gdk.SCROLL_UP:
            target = self.pager.get_current_desktop() - 1
        elif event.direction == gtk.gdk.SCROLL_DOWN:
            target = self.pager.get_current_desktop() + 1
        else:
            return

        self.pager.switch_desktop(target % self.pager.get_desktop_count())


    def __setitem__(self, key, val):
        '''Sets config variable key to val.'''

        self.conf[key] = val

    def __getitem__(self, key):
        '''Returns the value of config variable key.'''

        return self.conf[key]

    def set(self, key, val):
        '''Sets config variable key to val.'''

        self.conf[key] = val

    def main(self):
        '''Starts the main GTK loop.'''
        num = self.pager.get_current_desktop()
        self.update_pixbuf(num)

class Plugin(Plg.PluginContainer):
    def __init__(self, bar, settings):
        Plg.PluginContainer.__init__(self, bar, settings)
        self.can_zoom = False
        self.can_show_icon = False
        self.settings = settings
        self.bar = bar

        config = NeapConfig()
        self.pager = Neap(config, self, bar)
        self.pager.main()
        self.connect('scroll-event', self.pager.scroll)

    def resize(self):
        self.set_size_request(self.cfg['icon_size'], self.cfg['icon_size'])
        self.pager.init_size()

    def _enter_notify(self, widget, event):
        self.bar.bar_enter_notify()
