# -*- coding: utf-8 -*-

import gtk

import adesk.plugin as Plg
import adesk.core as Core
import adesk.ui as UI

class Plugin(Plg.Plugin):
    def __init__(self, bar, settings):
        Plg.Plugin.__init__(self, bar, settings)
        self.settings = settings
        self.can_zoom = True
        self.hello = Hello(self, bar)

    def onClick(self, widget, event):
        self.hello.toggle()

    def resize(self):
        self.set_size_request(self.cfg['icon_size'], self.cfg['icon_size'])

class Hello(UI.PopupWindow):
    def __init__(self, plugin, bar):
        UI.PopupWindow.__init__(self, bar, plugin)

        btn = gtk.Button('Hello')
        btn.show()
        btn.set_relief(gtk.RELIEF_NONE)
        btn.set_border_width(0)
        btn.set_focus_on_click(False)
        btn.set_property('can-focus', False)

        self.add(btn)
