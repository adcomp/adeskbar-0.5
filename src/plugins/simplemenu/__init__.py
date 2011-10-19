# -*- coding: utf-8 -*-

import gtk

try:
    import pyinotify
    NOTIFY = True
except:
    NOTIFY = False
    
import adesk.plugin as Plg
import adesk.ui as UI
import adesk.core as Core

import gobject
gobject.threads_init()

class EventHandler(pyinotify.ProcessEvent):
    
    def __init__(self, menu_ui):
        self.menu_ui = menu_ui
        self.timer = None
        
    def process_IN_CREATE(self, event):
        #~ print 'process_IN_CREATE'
        self.set_timer()
        
    def process_IN_DELETE(self, event):
        #~ print 'process_IN_DELETE'
        self.set_timer()
            
    def set_timer(self):
        if not self.timer == None:
            gobject.source_remove(self.timer)
        self.timer = gobject.timeout_add(5000, self.on_timeout_notify)

    def on_timeout_notify(self):
        self.timer = None
        print('Reload menu ( change in /usr/share/applications )')
        self.menu_ui.restart()
        return False
        
class Plugin(Plg.Plugin):
    def __init__(self, bar, settings):
        Plg.Plugin.__init__(self, bar, settings)
        self.settings = settings
        self.bar = bar
        self.can_zoom = True
        self.menu = UI.Menu(self.launch_app)
        self.menu.menu.connect('deactivate', self.menu_deactivate)

        if NOTIFY:
            wm = pyinotify.WatchManager()  # Watch Manager
            mask = pyinotify.IN_DELETE | pyinotify.IN_CREATE  # watched events
            handler = EventHandler(self)
            self.notifier = pyinotify.ThreadedNotifier(wm, handler)
            wdd = wm.add_watch('/usr/share/applications', mask, rec=True)
            self.notifier.start()

    def restart(self):
        self.menu.menu.destroy()
        self.menu = UI.Menu(self.launch_app)
        self.menu.menu.connect('deactivate', self.menu_deactivate)

    def stop(self):
        if NOTIFY:
            self.notifier.stop()
            
    def onClick(self, widget, event):

        def get_position(menu):
            plugin_x, plugin_y, plugin_w, plugin_h = self.get_allocation()
            screen_width, screen_height =  gtk.gdk.screen_width(), gtk.gdk.screen_height()
            menu_size = self.menu.menu.size_request()

            padding = 0
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
        self.menu.menu.popup(None, None, get_position, 0, 0)
        self.is_visible = True

    def resize(self):
        self.set_size_request(self.cfg['icon_size'], self.cfg['icon_size'])

    def launch_app(self, widget, app):
        # Strip last part of path if it contains %<a-Z>
        command = app.Exec.split('%')[0]
        if app.Terminal:
            command = '%s -e %s' % (self.settings['terminal'], command)
        Core.launch_command(command)

    def menu_deactivate(self, widget):
        self.is_visible = False
        self.call_bar_update()
