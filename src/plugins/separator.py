# -*- coding: utf-8 -*-

import gtk
import adesk.plugin as Plg

class Plugin(Plg.Plugin):
    def __init__(self, bar, settings):
        Plg.Plugin.__init__(self, bar, settings)
        self.has_tooltip = False
        self.can_zoom = False

    def resize(self):
        if self.cfg['position'] == "bottom" or self.cfg['position'] == "top":
            self.set_size_request(self.cfg['icon_size']//4 , self.cfg['icon_size'])
        else:
            self.set_size_request(self.cfg['icon_size'], self.cfg['icon_size']//4)
