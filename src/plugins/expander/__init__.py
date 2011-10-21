# -*- coding: utf-8 -*-
#
# ADeskBar - "Expander" plugin
#
##

import adesk.plugin as Plg

class Plugin(Plg.Plugin):
    def __init__(self, bar, settings):
        Plg.Plugin.__init__(self, bar, settings)

        self.has_tooltip = False
        self.can_zoom = False
        self.can_show_icon = False
        
