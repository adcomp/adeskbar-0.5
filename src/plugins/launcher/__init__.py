# -*- coding: utf-8 -*-

import gtk

import adesk.plugin as Plg
import adesk.core as Core
import adesk.ui as UI

class Plugin(Plg.Plugin):
    def __init__(self, bar, settings):
        Plg.Plugin.__init__(self, bar, settings)
        self.can_zoom = True

    def onClick(self, widget, event):
        Core.launch_command(self.settings['cmd'])

    def resize(self):
        self.set_size_request(self.cfg['icon_size'], self.cfg['icon_size'])

    def _enter_notify(self, widget, event):
        self.bar.bar_enter_notify()
