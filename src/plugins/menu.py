# -*- coding: utf-8 -*-

import gtk

try:
    NOTIFY = True
    import pyinotify
except:
    NOTIFY = False
    
import adesk.plugin as Plg
import adesk.ui as UI
import adesk.core as Core

import gobject
gobject.threads_init()

MENU_WIDTH = 400
DEBUG = 0

class EventHandler(pyinotify.ProcessEvent):
    
    def __init__(self, menu_ui):
        self.menu_ui = menu_ui
        self.timer = None
        
    def process_IN_CREATE(self, event):
        self.set_timer()
        
    def process_IN_DELETE(self, event):
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
        self.bar = bar
        self.settings = settings
        self.can_zoom = True
        self.menu = Menu_UI(self, bar)

    def onClick(self, widget, event):
        self.menu.toggle(self.menu)

    def resize(self):
        self.set_size_request(self.cfg['icon_size'], self.cfg['icon_size'])
        
    def restart(self):
        self.menu.restart()
        
    def stop(self):
        self.menu.stop()

class Menu_UI(UI.PopupWindow):
    def __init__(self, plugin, bar):
        UI.PopupWindow.__init__(self, bar, plugin)
        self.set_size_request(MENU_WIDTH,-1)
        
        self.settings = plugin.settings
        if not 'show_label' in self.settings:
            self.settings['show_label'] = 1
        
        self.nbook = None
        self.catbox = None
        
        self.mainbox = gtk.HBox()
        self.mainbox.show()
        self.mainbox.set_spacing(1)
        self.mainbox.set_border_width(1)
        self.add(self.mainbox)
        self.restart()
        
        if NOTIFY:
            wm = pyinotify.WatchManager()
            mask = pyinotify.IN_DELETE | pyinotify.IN_CREATE
            handler = EventHandler(self)
            self.notifier = pyinotify.ThreadedNotifier(wm, handler)
            wdd = wm.add_watch('/usr/share/applications', mask, rec=True)
            self.notifier.start()

    def restart(self):
        if self.nbook is not None:
            self.nbook.destroy()
            self.catbox.destroy()
            
        self.nbook = gtk.Notebook()
        self.nbook.set_show_tabs(False)
        self.nbook.set_border_width(0)
        self.nbook.show()

        self.catbox = gtk.VBox()
        self.catbox.show()
        self.catbox.set_spacing(1)
        self.catbox.set_border_width(1)
        self.catbox.show()
        
        self.mainbox.pack_start(self.catbox, False, False)
        self.mainbox.pack_start(self.nbook, False, False)

        self.create_menu()
        
        self.catbox.get_children()[0].set_relief(gtk.RELIEF_HALF)

    def stop(self):
        if NOTIFY:
            self.notifier.stop()
            
    def executeAction(self, widget, event, app):
        if event.button == 1: # left click
            command = app.Exec.split('%')[0]
            if app.Terminal:
                command = '%s -e %s' % (self.settings['terminal'], command)
            Core.launch_command(command)
            self.toggle()

    def create_menu(self):
        xdgmenu = Core.XdgMenu()
        self.applications = xdgmenu.getMenu()
        self.add_to_nbook()

    def add_to_nbook(self):
        app_sort = []
        for category in self.applications:
            app_sort.append(category)
        app_sort.sort()
        
        for category in app_sort:
            box = self.make_tab_box(category, self.applications[category][0])
            for app in self.applications[category][1]:

                    if DEBUG:
                        txt_label = app.Name + '\n' + app.Exec
                    else:
                        txt_label = app.Name 
                        txt_label += '\n<small>' + app.Comment + '</small>'

                    button = Core.image_button(txt_label, app.Icon, 24)
                    button.connect("button-release-event", self.executeAction, app)
                    box.pack_start(button, False, False)
                                  
    def make_tab_box(self, label, icon):
        box = gtk.VBox()
        box.show()
        box.set_spacing(1)
        box.set_border_width(1)

        scrolled = gtk.ScrolledWindow()
        scrolled.show()
        scrolled.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scrolled.add_with_viewport(box)
        
        ind = self.nbook.append_page(scrolled, None)

        if self.plugin.settings['show_label'] in ('False','false','0', 0):
            button = Core.image_button(None, icon, 24)
        else:
            button = Core.image_button(label, icon, 24)
        
        button.connect("button-release-event", self.mouse_over, ind)
        button.connect("enter-notify-event", self.mouse_over, ind)
        self.catbox.pack_start(button, False, False)

        return box

    def mouse_over(self, widget, event, data):
        self.nbook.set_current_page(data)
        for button in self.catbox.get_children():
            button.set_relief(gtk.RELIEF_NONE)
        widget.set_relief(gtk.RELIEF_HALF)
            
