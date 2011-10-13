import gtk
import gobject
import os
import re

import adesk.core as Core
import adesk.barconf as BarConf
import adesk.ui as ui

# position in list
ID_ICON  = 0
ID_NAME = 1
ID_CMD = 2
ID_IMG = 3

settings = {'launcher':[]}

class config():
    def __init__(self, box, conf, ind):

        self.conf = conf
        self.ind = ind

        BoxListControls = gtk.VBox(False,0)

        # ListStore
        self.view = View()
        self.app_menu = ui.Menu(self.new_item_menu)

        if ind in self.conf.drawer:
            self.view.add_list(self.conf.drawer[ind])

        self.view.connect("row-activated", self.edit_item)

        scrolled = gtk.ScrolledWindow()
        scrolled.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolled.add(self.view)

        frame = gtk.Frame()
        frame.add(scrolled)

        #~ # Add from menu
        button = Core.image_button(BarConf._('add from menu'), 'images/conf/add_app.png', 24)
        button.connect("clicked", self.popup_menu)
        BoxListControls.pack_start(button, False, False)

        ## Control buttons for list
        # Add Launcher
        button = Core.image_button(BarConf._('add custom launcher'), 'images/conf/add_custom.png', 24)
        button.connect("clicked", self.new_item_custom)
        BoxListControls.pack_start(button, False, False)

        # Remove
        button = Core.image_button(BarConf._('remove'), 'images/conf/remove.png', 24)
        button.connect("clicked", self.remove_item)
        BoxListControls.pack_end(button, False, False)

        hbox = gtk.HBox()
        hbox.pack_start(BoxListControls, False, False)
        hbox.pack_start(frame, True)

        box.pack_start(hbox, True)

    def popup_menu(self, widget):
        
        def get_position(menu):
            x, y, w, h = widget.get_allocation()
            win_x, win_y = widget.window.get_position()
            return (win_x + x, win_y + y + h + 10, False)
        
        self.app_menu.menu.popup(None, None, get_position, 0, 0)

    def remove_item(self, widget):
        self.view.remove_item()

    def edit_item(self, view, path=None, view_column=None):
        selection = view.get_cursor()[0][0]
        if (selection is not None):
            model   = view.get_model()
            BarConf.Edit_Item(self.conf, model, selection, True)

    def new_item_custom(self, widget):
        app = Core.App()
        app.Name = 'Custom'
        app.Icon = 'system-run'
        self.new_item_menu(widget, app)
        #~ self.edit_item(self.view)

    def new_item_menu(self, widget, app):
        self.view.new_entry()
        selection = self.view.get_cursor()[0][0]
        
        if (selection is not None):
            model   = self.view.get_model()
            item    = model.get_iter(selection)
            
            model.set_value(item, ID_NAME, app.Name)

            command = app.Exec.split('%')[0]
            if app.Terminal:
                command = 'x-terminal-emulator -e %s' % command
            model.set_value(item, ID_CMD, command)

            icon = app.Icon
            BarConf.set_icon(icon, model, item)

            if len(icon) > 1 and not icon[0] == '/' and re.match(".*\.(png|xpm|svg)$", icon) is not None:
                    icon = icon[:-4]

            model.set_value(item, ID_IMG, icon)

    def save_change(self):
        
        # XXX! FixMe !! why 2 tab ? need to modify this buggy code :(
        self.conf.drawer[self.ind] = []
        self.conf.plg_mgr.plugins[self.ind].settings['launcher'] = []
        
        model = self.view.get_model()
        iter = model.get_iter_root()

        while (iter):
            name = model.get_value(iter, ID_NAME)
            icon = model.get_value(iter, ID_IMG)
            cmd = model.get_value(iter, ID_CMD)
            
            self.conf.drawer[self.ind].append((cmd, icon, name))
            self.conf.plg_mgr.plugins[self.ind].settings['launcher'].append((cmd, icon, name))

            iter = model.iter_next(iter)

        # restart plugin with new conf ..
        self.conf.plg_mgr.plugins[self.ind].restart()

class View(gtk.TreeView):

    def __init__(self):
        gtk.TreeView.__init__(self)
        self.set_headers_visible(False)
        self.set_reorderable(True)
        self.get_selection().set_mode(gtk.SELECTION_SINGLE)

        self.model = gtk.ListStore(
            gtk.gdk.Pixbuf,         # icon pixbuf
            gobject.TYPE_STRING,    # name
            gobject.TYPE_STRING,    # cmd
            gobject.TYPE_STRING,    # icon path
            )

        self.filtremodele = self.model.filter_new()
        self.set_model(self.model)

        cell = gtk.CellRendererPixbuf()
        col = gtk.TreeViewColumn(None, cell, pixbuf=ID_ICON)
        self.append_column(col)

        cell = gtk.CellRendererText()
        col = gtk.TreeViewColumn(None, cell, text=ID_NAME)
        self.append_column(col)

        cell = gtk.CellRendererText()
        col = gtk.TreeViewColumn(None, cell, text=ID_CMD)
        col.set_visible(False)
        self.append_column(col)

        cell = gtk.CellRendererText()
        col = gtk.TreeViewColumn(None, cell, text=ID_IMG)
        col.set_visible(False)
        self.append_column(col)

    def remove_item(self):
        # remove item from configuration
        try:
            #self.view.grab_focus()
            pos = self.get_cursor()[0][0]
            if pos == None: # no selection
                return

            model = self.get_model()
            #~ self.view.set_cursor(pos-1)
            #~ self.view.grab_focus()
            model.remove(model.get_iter(pos))

            if pos < 0:
                pos = 0
            # Set the focus and cursor correctly
            self.set_cursor(pos);
            self.grab_focus()
        except TypeError:
            print( "> nothing to delete !?" )

    def add_list(self, list):
        model = self.get_model()
        for my_item in list:
            item = model.append(None)
            cmd , icon , name = my_item
            #~ Core.set_icon(icon_path, model, item, 32)
            BarConf.set_icon(icon, model, item)
            model.set_value(item, ID_NAME, str(name))
            model.set_value(item, ID_CMD, str(cmd))
            model.set_value(item, ID_IMG, str(icon))

    # Add new treeview object, position=-1 inserts  into cursor's position
    def new_entry(self, position=-1, insertAfter=True):
        self.grab_focus()
        model = self.get_model()
        try:
            position = self.get_cursor()[0][0]
            try:
                iter = model.get_iter(position)
            except ValueError:
                print("> Empty list ?")
                iter = model.get_iter()

            if (insertAfter == True):
                item = model.insert_after(iter)
            else:
                item = model.insert_before(iter)
        except TypeError:
            print "typeError _ treeview"
            item = model.append(None)
            self.grab_focus()

        icon_path = ''
        icon = ''
        model.set_value(item, ID_NAME, '')
        model.set_value(item, ID_CMD, '')
        model.set_value(item, ID_IMG, icon_path)
        model.set_value(item, ID_ICON, Core.pixbuf_from_file(icon,32,32))
        ## Set focus to new entry and edit
        path = model.get_path(model.get_iter(position+1))
        self.set_cursor(path)
