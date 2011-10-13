# -*- coding: utf-8 -*-

import gtk
import pango
import gobject
import time

import adesk.plugin as Plg

def_settings = { 
    'line1':'%H:%M', 'line1_color':'#EEEEEE', 'line1_font':'Sans Bold 12',
    'line2':'%d/%m', 'line2_color':'#B5B5B5', 'line2_font':'Sans Bold 8',
    }

class Plugin(Plg.PluginContainer):
    def __init__(self, bar, settings):
        Plg.PluginContainer.__init__(self, bar, settings)
        self.can_zoom = False
        self.can_show_icon = False
        self.settings = settings
        self.bar = bar

        self.locked = False

        ## FIXME!!
        for key in def_settings:
            if not key in self.settings:
                self.settings[key] = def_settings[key]

        self.box = gtk.VBox(False, 0)
        self.box.set_border_width(0)
        self.add(self.box)

        self.set_from_config()
        self.update_time()
        gobject.timeout_add(1000, self.update_time)

    def set_from_config(self):
        self.line1_txt = ''
        self.line2_txt = ''
        self.lb_line1 = gtk.Label()
        self.lb_line1.modify_font(pango.FontDescription(self.settings['line1_font']))
        self.lb_line1.set_use_markup(True)
        self.lb_line1.set_alignment(0.5,0.5)
        self.box.pack_start(self.lb_line1)

        if not self.settings['line2'] == '':
            self.lb_line2 = gtk.Label()
            self.lb_line2.modify_font(pango.FontDescription(self.settings['line2_font']))
            self.lb_line2.set_use_markup(True)
            self.lb_line2.set_alignment(0.5,0.5)
            self.box.pack_start(self.lb_line2)
        else:
            self.lb_line2 = None
        self.box.show_all()

    def update_time(self):
        if self.locked:
            return True
            
        now = time.localtime()
        line1_current = time.strftime('<span color="%s">%s</span>' % 
                                    (self.settings['line1_color'], 
                                     self.settings['line1']), 
                                     now)
        if self.lb_line2 is not None:
            line2_current = time.strftime('<span color="%s">%s</span>' % 
                                        (self.settings['line2_color'], 
                                         self.settings['line2']), 
                                         now)

        if self.line1_txt <> line1_current:
            self.lb_line1.set_markup(line1_current)
        self.line1_txt = line1_current
        
        if self.lb_line2 is not None:
            if self.line2_txt <>line2_current:
                self.lb_line2.set_markup(line2_current)
            self.line2_txt = line2_current
            
        return True

    def resize(self):
        if self.bar.cfg['position']=='top' or self.bar.cfg['position']=='bottom':
            self.set_size_request(-1, self.cfg['icon_size'])
        else:
            self.set_size_request(self.cfg['icon_size'], -1)

    def restart(self):
        self.locked = True
        self.box.remove(self.lb_line1)
        self.lb_line1.destroy()
        if self.lb_line2:
            self.box.remove(self.lb_line2)
            self.lb_line2.destroy()
        self.set_from_config()
        self.locked = False
        self.resize()
        self.update_time()
