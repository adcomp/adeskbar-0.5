# -*- coding: utf-8 -*-
#
# ADeskBar - "Menu" plugin
#
##

import gtk
import os

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

def_settings = {'terminal':'x-terminal-emulator', 'show_label':1, 'run':1}

MENU_WIDTH = 400
DEBUG = 0

PATH = os.environ['PATH'].split(':')

def exists_in_list(list,item):
	for i in list:
		if i == item:
			return True
	return False

# look for executable files
class FileListing:
	
	l = []	

	def __init__(self,path):
		self.PATH = path
		for dir in self.PATH:
			self.append_files_from(dir)

	def get_file_set(self):
		return set(self.l)

	def append_files_from(self,dir):
		dirname = os.path.abspath(dir)
		files = [ f for f in os.listdir(dir) if f[0] <> '.' ]
		files.sort()

		for file in files:
			self.l.append(file)	



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
        self.timer = gobject.timeout_add(4000, self.on_timeout_notify)

    def on_timeout_notify(self):
        self.timer = None
        print('Reload menu ( change in /usr/share/applications )')
        self.menu_ui.restart()
        return False

class Plugin(Plg.Plugin):
    
    def __init__(self, bar, settings):
        Plg.Plugin.__init__(self, bar, settings)

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

    nbook = None
    catbox = None
    entry = None

    def __init__(self, plugin, bar):
        UI.PopupWindow.__init__(self, bar, plugin)
        
        self.connect ("key-press-event", self.on_key_press_event)
        self.set_size_request(MENU_WIDTH,-1)
        
        self.settings = plugin.settings

        ## FIXME!!
        for key in def_settings:
            if not key in self.settings:
                self.settings[key] = def_settings[key]
        
        box = gtk.VBox()
        
        self.mainbox = gtk.HBox()
        self.mainbox.show()
        self.mainbox.set_spacing(2)
        self.mainbox.set_border_width(2)

        self.entrybox = gtk.HBox()
        self.entrybox.set_spacing(2)
        self.entrybox.set_border_width(2)
        
        box.pack_start(self.mainbox, False, False)
        box.pack_end(self.entrybox, False, False)
        
        self.add(box)
        self.restart()

        box.show_all()
        
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

        if self.entry:
            for child in self.entrybox.get_children():
                child.destroy()
            self.entry = None
            
        if self.settings['run']:
            self.fl = FileListing(PATH)
            self.entry = gtk.Entry()
            self.entry.show()
            #~ self.entry.set_max_length(150)
            self.entry.set_width_chars(45)

            completion = gtk.EntryCompletion()
            self.entry.set_completion(completion)
            completion_model = self.create_completion_model()
            completion.set_model(completion_model)
            completion.set_text_column(0)

            self.entry.connect("activate", self.enter_callback)

            btn = Core.image_button(None, 'images/plugins/run.png', 24)
            btn.connect("clicked", self.enter_callback)
            btn.set_focus_on_click(False)

            self.entrybox.pack_start(self.entry, True, True)
            self.entrybox.pack_start(btn, False, False)

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
                        if app.Comment == '' or app.Comment == ' ':
                            comment = '--'
                        elif len(app.Comment) > 50:
                            comment == app.Comment[:50] + '..'
                        else:
                            comment = app.Comment
                        txt_label += '\n<small>' + comment + '</small>'

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

    # Quit when Escape key is pressed
    def on_key_press_event(self, widget, event):
        if event.hardware_keycode == 9: # Escape 
            self.entry.x_done = True
            self.entry.set_text("")
            self.toggle()

    def create_completion_model(self):
		store = gtk.ListStore(str)
		f = self.fl.get_file_set()
		for file in f:
			iter = store.append()
			store.set(iter,0,file)
		return store

    def enter_callback(self, widget):
        Core.launch_command(self.entry.get_text())
        self.entry.x_done = True
        self.entry.set_text("")
        self.toggle()
