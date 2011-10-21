# -*- coding: utf-8 -*-
#
# ADeskBar - "Show Desktop" plugin
#
##

import adesk.plugin as Plg
import adesk.core as Core

try:
    import wnck
except:
    Core.logINFO('Plugin "showdesktop" need python-wnck')
    Core.logINFO(' -- debian/ubuntu : "sudo apt-get install python-wnck"')

class Plugin(Plg.Plugin):

    def __init__(self, bar, settings):
        Plg.Plugin.__init__(self, bar, settings)

    def onClick(self, widget, event):
        screen = wnck.screen_get_default()
        # showing windows = not showing desktop
        showing_windows = not screen.get_showing_desktop()
        screen.toggle_showing_desktop(showing_windows)

    def resize(self):
        self.set_size_request(self.cfg['icon_size'], self.cfg['icon_size'])
