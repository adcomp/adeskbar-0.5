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
        self.searchbox = SearchWindow(self, bar)

    def onClick(self, widget, event):
        self.searchbox.toggle()

    def resize(self):
        self.set_size_request(self.cfg['icon_size'], self.cfg['icon_size'])

class SearchWindow(UI.PopupWindow):
    def __init__(self, plugin, bar):
        UI.PopupWindow.__init__(self, bar, plugin)

        box = gtk.HBox(False, 4)
        box.set_border_width(2)
        self.add(box)

        self.entry = gtk.Entry()
        self.entry.x_done = False
        self.entry.set_name("TextBox")
        self.entry.set_width_chars(25)
        self.entry.connect("button-press-event", self.manage_click)
        self.entry.connect("activate", self.go)
        box.pack_start(self.entry, True)

        btn = gtk.Button()
        btn.set_name("EdgeButton")
        btn.connect("clicked", self.go)
        #~ btn.set_label("Search")
        btn.set_relief(gtk.RELIEF_NONE)
        btn.set_border_width(0)
        btn.set_focus_on_click(False)
        btn.set_property('can-focus', False)

        image = gtk.Image()
        pixbuf = Core.pixbuf_from_file('images/plugins/searchbox.png', 24, 24)
        image.set_from_pixbuf(pixbuf)
        btn.add(image)

        box.pack_end(btn, False)
        box.show_all()

    def go(self, widget):
        url = " '" + self.plugin.settings['engine'] + self.entry.get_text() + "'"
        cmd = self.plugin.settings['browser'] + url
        Core.launch_command(cmd)

        self.entry.x_done = True
        self.entry.set_text("")
        self.toggle()

    def manage_click(self, entry, event):
        self.fixFocus()

    def fixFocus(self):
        self.entry.grab_focus()
        #~ self.panel.set_focus(self.entry)
        if self.entry.x_done:
            self.entry.set_text("")
            self.entry.x_done = False

    def toggle(self, widget = 0):
        UI.PopupWindow.toggle(self)
        self.fixFocus()
