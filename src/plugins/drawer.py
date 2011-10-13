# adesk "Drawer" plugin

import gtk
import os

import adesk.plugin as Plg
import adesk.core as Core
import adesk.ui as UI

class Plugin(Plg.Plugin):
    def __init__(self, bar, settings):
        Plg.Plugin.__init__(self, bar, settings)

        self.can_zoom = True
        self.drawer = Drawer(self, bar)

    def onClick(self, widget, event):
        self.drawer.toggle()

    def resize(self):
        self.set_size_request(self.cfg['icon_size'], self.cfg['icon_size'])

    def restart(self):
        self.drawer.restart()

class Drawer(UI.PopupWindow):
    def __init__(self, plugin, bar):
        UI.PopupWindow.__init__(self, bar, plugin)
        
        self.box = gtk.VBox(False, 0)
        self.box.set_border_width(0)
        self.add(self.box)
        
        self.buttons = []
        self.create_drawer_button()

    def create_drawer_button(self):
        
        for launcher in self.plugin.settings['launcher']:
            (cmd, icon, name) = launcher
            image = gtk.Image()
            Core.set_icon(icon, image, size=24)
            button = Core.image_button(name, image, 24)
            button.connect("button-release-event", self.onClicked, cmd)
            self.box.pack_start(button)
            self.buttons.append(button)

        self.set_size_request(200,-1)
        self.box.show_all()

    def onClicked(self, widget, event, cmd):

        Core.launch_command(cmd)
        self.toggle(self)

    def restart(self):

        for button in self.buttons:
            self.box.remove(button)
            button.destroy()

        self.buttons = []
        self.resize(1, 1)
        self.box.set_size_request(-1, -1)
        self.create_drawer_button()
