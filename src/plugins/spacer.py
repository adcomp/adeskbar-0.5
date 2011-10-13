# -*- coding: utf-8 -*-

import adesk.plugin as Plg

class Plugin(Plg.Plugin):
    def __init__(self, bar, settings):
        Plg.Plugin.__init__(self, bar, settings)
        self.settings = settings
        self.has_tooltip = False
        self.can_zoom = False
        self.can_show_icon = False
        
        if not 'size' in self.settings:
            self.settings['size'] = 4
        else:
            self.settings['size'] = int(self.settings['size'])

    def resize(self):
        if self.cfg['position'] == "bottom" or self.cfg['position'] == "top":
            self.set_size_request(self.settings['size'], self.cfg['icon_size'])
        else:
            self.set_size_request(self.cfg['icon_size'], self.settings['size'])

    def restart(self):
        self.resize()
