# -*- coding: utf-8 -*-

import gtk
import wnck
import time

import adesk.plugin as Plg

class Plugin(Plg.Plugin):
    def __init__(self, bar, settings):
        Plg.Plugin.__init__(self, bar, settings)
        self.settings = settings
        self.bar = bar
        self.can_zoom = True

        # Wnck 
        self.wnck = Wnck()

        # menu
        self.popupMenu = None
        
    def onClick(self, widget, event):

        def get_position(menu):
            plugin_x, plugin_y, plugin_w, plugin_h = self.get_allocation()
            screen_width, screen_height =  gtk.gdk.screen_width(), gtk.gdk.screen_height()
            menu_size = self.popupMenu.size_request()

            padding = 4
            orientation = self.bar.cfg['position']
            
            if orientation == "bottom":
                icon_y = self.bar.bar_pos_y  - menu_size[1] - padding
                icon_x = self.bar.bar_pos_x + plugin_x
            elif orientation == "top":
                icon_y = self.bar.bar_pos_y + self.bar.draw_height + padding
                icon_x = self.bar.bar_pos_x + plugin_x
            elif orientation == "right":
                icon_x = self.bar.bar_pos_x - menu_size[0] - padding
                icon_y = self.bar.bar_pos_y + plugin_y
            elif orientation == "left":
                icon_x = self.bar.bar_pos_x + self.bar.draw_width + padding
                icon_y = self.bar.bar_pos_y + plugin_y

            # Make sure the bottom of the menu doesn't get below the bottom of the screen
            icon_y = min(icon_y, screen_height - menu_size[1])

            return (icon_x, icon_y, False)
            
        self.create_menu()
        self.popupMenu.popup(None, None, get_position, 0, 0)


    def resize(self):
        self.set_size_request(self.cfg['icon_size'], self.cfg['icon_size'])

    def create_menu(self):
        if self.popupMenu:
            self.popupMenu.destroy()
        
        windows = self.wnck.screen.get_windows()
        
        workspaces = []
        ws_windows = {}
        
        ws_count = self.wnck.screen.get_workspace_count()
        active_ws = self.wnck.screen.get_active_workspace()

        for i in range(0, ws_count):
            ws = self.wnck.screen.get_workspace(i)
            workspaces.append(ws)
            ws_windows[ws] = []

        for window in windows:
            if not window.is_skip_pager():
                ws = window.get_workspace()
                ws_windows[ws].append(window)

        self.popupMenu = gtk.Menu()
        
        ind_ws = 0
        for ws in workspaces:
            ind_ws += 1
            label = "Desktop %s" % ind_ws
            if active_ws == ws:
                label += ' *'
            menu_desktop = gtk.ImageMenuItem(label)
            self.popupMenu.add(menu_desktop)
            menu_desktop.show()
            
            empty = True
            for window in ws_windows[ws]:
                menuPopup = gtk.ImageMenuItem(window.get_name())
                menuPopup.connect("activate", self.activate_window, window)
                image = gtk.Image()
                pbuf = self.window_get_icon(window)
                image.set_from_pixbuf(pbuf)
                menuPopup.set_image(image)
                self.popupMenu.add(menuPopup)
                menuPopup.show()
                empty = False

            if empty and not (active_ws == ws):
                menu_desktop.connect("activate", self.activate_workspace, ws)
            else:
                menu_desktop.set_sensitive(False)
                
            if not ind_ws == ws_count:
                separator = gtk.SeparatorMenuItem()
                self.popupMenu.add(separator)
                separator.show()

        #~ self.popupMenu.show_all()

    def activate_window(self, data, window):
        timestamp = int(time.time())
        
        ws = window.get_workspace()
        active_ws = self.wnck.screen.get_active_workspace()

        if not ws == active_ws:
            if ws:
                ws.activate(timestamp)
        
        window.activate(timestamp)

    def activate_workspace(self, data, workspace):
        timestamp = int(time.time())
        workspace.activate(timestamp)

    def window_get_icon(self, window):
        size = 24
        return window.get_icon().scale_simple(size, size, gtk.gdk.INTERP_BILINEAR)


class Wnck:
    def __init__(self):

        # silently ignore x errors
        gtk.gdk.error_trap_push()

        # init screen and hook into WnckSceen's events
        self.screen = wnck.screen_get_default()
        self.screen.force_update()
        self.screen.connect("window_opened", self.window_opened)

    def window_opened(self, screen, window):
        return
        
        timestamp = int(time.time())

        wsp = window.get_workspace()
        active_wsp = self.screen.get_active_workspace()
        
        if not wsp == active_wsp:
            if wsp:
                wsp.activate(timestamp)
        window.activate(timestamp)
