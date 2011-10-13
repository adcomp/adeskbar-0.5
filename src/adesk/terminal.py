# -*- coding: utf-8 -*-

import gtk
import vte
import os

import ui

class Terminal(ui.EmbeddedWindow):
    def __init__(self, bar):
        ui.EmbeddedWindow.__init__(self, bar)

        self.bar = bar
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
        self.maximize()
        window_w, window_h = self.bar.win.get_size()
        screen_width, screen_height = gtk.gdk.screen_width(), gtk.gdk.screen_height()
        print 'window_w = ' + str(window_w)
        self.box.set_size_request(screen_width, screen_height/2)
        self.init_terminal()
        
        #~ self._vte.set_font_from_string(self.plugin.settings['font'])

        #~ if self.is_composited():
            #~ self._vte.set_opacity(65535 * int(self.plugin.settings['opacity']) // 100)
        #~ else:
            #~ self._vte.set_background_transparent(True)

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
        #~ self._vte.set_size(80,24)
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
            print 'set fullscreen'
            self.set_fullscreen()
            return True

    def set_fullscreen(self):
            if self.is_fullscreen:
                print '-- unfullscreen'
                self.unfullscreen()
            else:
                print '-- fullscreen '
                self.fullscreen()
            self.is_fullscreen = not self.is_fullscreen
