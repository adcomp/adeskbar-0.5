import gtk
import gobject
import sys
import os

import ui
import core

PATH = os.environ['PATH'].split(':')
#~ print "-- PATH:",PATH

def exists_in_list(list,item):
	for i in list:
		if i == item:
			return True
	return False

# look for executable files
class FileListing:
	
	l = []	

	def get_file_set(self):
		return set(self.l)

	def append_files_from(self,dir):
		dirname = os.path.abspath(dir)
		files = [ f for f in os.listdir(dir) if f[0] <> '.' ]
		files.sort()

		for file in files:
			self.l.append(file)			

	def __init__(self,path):
		self.PATH = path
		for dir in self.PATH:
			self.append_files_from(dir)

class RunDialog(ui.EmbeddedWindow):

    fl = FileListing(PATH)

    def __init__(self, bar):
        ui.EmbeddedWindow.__init__(self, bar)
        self.connect ("key-press-event", self.on_key_press_event)
        # def text entry
        self.entry = gtk.Entry()
        #~ self.entry.set_max_length(150)
        self.entry.set_width_chars(45)

        completion = gtk.EntryCompletion()
        self.entry.set_completion(completion)
        completion_model = self.create_completion_model()
        completion.set_model(completion_model)
        completion.set_text_column(0)

        self.entry.connect("activate", self.enter_callback)

        self.add(self.entry)

        # draw widgets
        self.entry.show()

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
        core.launch_command(self.entry.get_text())
        self.entry.x_done = True
        self.entry.set_text("")
        self.toggle()













