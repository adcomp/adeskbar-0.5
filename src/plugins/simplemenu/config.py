# -*- coding: utf-8 -*-

import gtk

settings = {'terminal':'x-terminal-emulator'}

class config():

    def __init__(self, box, conf, ind):

        self.conf = conf
        self.ind = ind

        for key in settings:
            if not key in conf.launcher[ind]:
                conf.launcher[ind][key] = settings[key]

        self.settings = conf.launcher[ind]


        label = gtk.Label("Terminal :")
        label.set_alignment(0, 0.5)
        self.terminal = gtk.Entry()
        self.terminal.set_width_chars(20)
        self.terminal.set_text(conf.launcher[ind]['terminal'])

        box.pack_start(label, False, False)
        box.pack_start(self.terminal, False, False)

    def save_change(self):
        self.conf.launcher[self.ind]['terminal'] = self.terminal.get_text()
        self.conf.plg_mgr.plugins[self.ind].restart()
        
