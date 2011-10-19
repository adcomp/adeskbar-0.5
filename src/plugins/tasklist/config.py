# -*- coding: utf-8 -*-

import gtk

settings = { 
    'desktop_color':'#EEEEEE', 'desktop_font':'Sans Bold 12',
    'show_desk_pos':1, 'show_desk_name':0, 'show_all_win':1,
    'active_color':'#7F7F7F', 'padding':10, 'opacity':14100,
    'expand': 1, 
    }

class config():
    def __init__(self, box, conf, ind):

        self.conf = conf
        self.ind = ind
        
        self.settings = conf.launcher[ind]

        for key in settings:
            if not key in self.settings:
                self.settings[key] = settings[key]


        ### Active color - Padding
        hhbox = gtk.HBox(False, 0)
        hhbox.set_spacing(10)


        hbox = gtk.HBox(False, 0)
        hbox.set_spacing(10)
        label = gtk.Label('Active window color')
        map = label.get_colormap()
        
        colour = map.alloc_color(self.settings['active_color'])
        self.active_color = gtk.ColorButton(colour)
        self.active_color.set_use_alpha(True)
        self.active_color.set_alpha(self.settings['opacity'])
        hbox.pack_start(label, False)
        hbox.pack_start(self.active_color, False)
        hhbox.pack_start(hbox, False)

        hbox = gtk.HBox(False, 0)
        hbox.set_spacing(10)
        label = gtk.Label('Padding')
        adjustment = gtk.Adjustment(value=self.settings['padding'], lower=1, upper=25, step_incr=1, page_incr=10, page_size=0)
        self.padding = gtk.SpinButton(adjustment=adjustment, climb_rate=0.0, digits=0)
        hbox.pack_start(label, False)
        hbox.pack_start(self.padding, False)
        hhbox.pack_start(hbox, False)
        
        box.pack_start(hhbox, False)


        ### Show all windows - desktop position/name
        self.show_all_win_checkbox = gtk.CheckButton('Show all windows')
        self.show_all_win_checkbox.set_active(int(self.settings['show_all_win']))

        box.pack_start(self.show_all_win_checkbox, False)
        
        
        ### Show desktop position/name
        showdesktopbox = gtk.HBox()
        
        self.show_desk_pos_checkbox = gtk.CheckButton('Show desktop position')
        self.show_desk_pos_checkbox.set_active(int(self.settings['show_desk_pos']))
        showdesktopbox.pack_start(self.show_desk_pos_checkbox, True)

        self.show_desk_name_checkbox = gtk.CheckButton('Show desktop name')
        self.show_desk_name_checkbox.set_active(int(self.settings['show_desk_name']))

        colour = map.alloc_color(self.settings['desktop_color'])
        self.desk_color = gtk.ColorButton(colour)
        self.desk_font = gtk.FontButton(self.settings['desktop_font'])
        showdesktopbox.pack_start(self.desk_font, True)
        showdesktopbox.pack_start(self.desk_color, False)

        box.pack_start(showdesktopbox, False)

        showdesknamebox = gtk.HBox(False, 0)
        showdesknamebox.set_border_width(0)
        showdesknamebox.set_spacing(10)
        label = gtk.Label('     ')
        showdesknamebox.pack_start(label, False)
        showdesknamebox.pack_start(self.show_desk_name_checkbox, False)
        
        box.pack_start(showdesknamebox, False)

        ### expand
        self.expand_checkbox = gtk.CheckButton('Fills space on the bar in fixed mode')
        self.expand_checkbox.set_active(int(self.settings['expand']))
        box.pack_start(self.expand_checkbox, False)

    def save_change(self):
        self.settings['opacity'] = self.active_color.get_alpha()
        self.settings['active_color'] = gtk.color_selection_palette_to_string([self.active_color.get_color()])
        self.settings['padding'] = int(self.padding.get_value())
        self.settings['desktop_color'] = gtk.color_selection_palette_to_string([self.desk_color.get_color()])
        self.settings['desktop_font'] = self.desk_font.get_font_name()
        self.settings['show_desk_pos'] = int(self.show_desk_pos_checkbox.get_active())
        self.settings['show_desk_name'] = int(self.show_desk_name_checkbox.get_active())
        self.settings['show_all_win'] = int(self.show_all_win_checkbox.get_active())
        self.settings['expand'] = int(self.expand_checkbox.get_active())
        self.conf.plg_mgr.plugins[self.ind].restart()
