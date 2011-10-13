# -*- coding: utf-8 -*-

import gtk
import vte
import os

import adesk.plugin as Plg
import adesk.core as Core
import adesk.ui as UI

try:
    import vte
except:
    Core.logINFO('Plugin "terminal" need python-vte')
    Core.logINFO(' -- debian/ubuntu : "sudo apt-get install python-vte"')

class Plugin(Plg.Plugin):
    def __init__(self, bar, settings):
        Plg.Plugin.__init__(self, bar, settings)
        self.can_zoom = True
        self.settings = settings
        self.terminal = Terminal(self, bar)

    def onClick(self, widget, event):
        self.terminal.toggle()

    def resize(self):
        self.set_size_request(self.cfg['icon_size'], self.cfg['icon_size'])

    def restart(self):
        self.terminal.restart()

class Terminal(UI.PopupWindow):
    def __init__(self, plugin, bar):
        UI.PopupWindow.__init__(self, bar, plugin)
        self.plugin = plugin
        
        self.box = gtk.HBox()
        self.add(self.box)
        self.box.show()
        
        self.init_terminal()
        self.set_from_config()

        self.is_fullscreen = False

    def restart(self):
        self.box.remove(self._vte)
        self.box.remove(self.scrollbar)
        self.resize(1, 1)
        self.set_from_config()

    def set_from_config(self):
        self.box.set_size_request(int(self.plugin.settings['width']), int(self.plugin.settings['height']))
        self.init_terminal()
        
        self._vte.set_font_from_string(self.plugin.settings['font'])

        if self.is_composited():
            self._vte.set_opacity(65535 * int(self.plugin.settings['opacity']) // 100)
        else:
            self._vte.set_background_transparent(True)

        ## exec cmd
        if not self.plugin.settings['exec_cmd'] == '':
            self._vte.feed_child('%s\n' % self.plugin.settings['exec_cmd'])

        self.scrollbar = gtk.VScrollbar()
        self.scrollbar.show()
        self.scrollbar.set_adjustment(self._vte.get_adjustment())
        
        self.box.pack_start(self._vte)
        self.box.pack_end(self.scrollbar)
        
    def init_terminal(self):
        self._vte = vte.Terminal()
        #~ self.connect("focus-in-event", self.fixFocus)
        
        self._vte.connect("child-exited", self.__cb_exited)
        self._vte.connect("key-press-event", self.on_key_press)
        
        self._vte.set_emulation("xterm")
        self._vte.set_allow_bold(True)
        self._vte.set_scrollback_lines(1024)
        self._vte.set_size(80,24)
        self.start_terminal()
        self._vte.show()

    def start_terminal(self):
        os.chdir(os.getenv('HOME'))
        self._vte.fork_command()
        realpath = os.path.dirname(os.path.realpath( __file__ ))
        os.chdir(realpath + '/..')
        
    def __cb_exited(self, terminal):
        self.start_terminal()
        self.toggle()

    def on_key_press(self, widget, event):
        if event.keyval == gtk.keysyms.F11:
            self.set_fullscreen()

    def set_fullscreen(self):
            if self.is_fullscreen:
                self.unfullscreen()
            else:
                self.fullscreen()
            self.is_fullscreen = not self.is_fullscreen
