# -*- coding: utf-8 -*-

import gtk

settings = { 
    'size':4,
    }

class config():
    def __init__(self, box, conf, ind):

        self.conf = conf
        self.ind = ind
        
        self.settings = conf.launcher[ind]

        for key in settings:
            if not self.settings.has_key(key):
                self.settings[key] = settings[key]

        label = gtk.Label('Size')
        label.set_alignment(0.9, 0.5)
        
        adjustment = gtk.Adjustment(value=self.settings['size'], lower=1, upper=128, step_incr=1, page_incr=8, page_size=0)
        self.size = gtk.SpinButton(adjustment=adjustment, climb_rate=0.0, digits=0)
        self.size.set_tooltip_text('size in pixel')

        box.pack_start(label, False, False)
        box.pack_start(self.size, False, False)

    def save_change(self):
        self.settings['size'] = int(self.size.get_value())
        self.conf.plg_mgr.plugins[self.ind].restart()

