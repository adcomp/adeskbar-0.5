# -*- coding: utf-8 -*-

import os
import os.path
import gtk
import re
import gio
import glib
import xdg.Menu
import xdg.BaseDirectory
from subprocess import Popen

# Only for debugging : False / True
DEBUG = 0

ICON_THEME = gtk.icon_theme_get_default()

# FIXME! quick hack
ID_ICON  = 1

def logINFO(msg, from_mod=""):
    if DEBUG:
        mod = ''
        if from_mod:
            mod = "(" + from_mod + ") -- "
        print ("[adeskbar] %s%s" % (mod, msg))

def launch_command(cmd):
    if cmd != ' ' and cmd != None and len(cmd)!=0:
        os.chdir(os.environ['HOME'])
        logINFO("Exec. | %s |" % cmd, 'core')
        
        try:
            Popen(cmd, shell=True)
        except OSError:
            logINFO("   -- error :  %s" % cmd, 'core')

        realpath = os.path.dirname(os.path.realpath( __file__ ))
        os.chdir(realpath + '/..')

def hex2rgb(color_hex):
    ## convert Hex color to RGB
    hexcolor = color_hex.strip()
    hexcolor = hexcolor[1:]
    if len(hexcolor) != 6:
        logINFO('Invalid hex color, use #RRGGBB format.', 'core')
        return (0.0, 0.0, 0.0)
    r, g, b = hexcolor[:2], hexcolor[2:4], hexcolor[4:]
    r, g, b = [int(n, 16) for n in (r, g, b)]
    return (float(r)/256, float(g)/256, float(b)/256)

def pixbuf_from_file(file, width=None, height=None):
    pixbuf = None

    if file != None or file == '':
        if os.path.isfile(file):
            try:
                
                if not width and not height:
                    pixbuf = gtk.gdk.pixbuf_new_from_file(file)
                else:
                    if width and not height:
                        height = width
                    width, height = int(width), int(height)
                    pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(file, width, height)
            except:
                logINFO("is a image ? => %s" % file, 'core')
                pixbuf = None
        else:
            logINFO("is a image ? => %s" % file, 'core')

    return pixbuf

def ask_question(msg='Ok .. ?'):
    """  """
    message = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_INFO, gtk.BUTTONS_YES_NO, msg)
    resp = message.run()
    message.destroy()

    if resp == gtk.RESPONSE_YES:
        return True
    else:
        return False

def show_msg(msg=' .. '):
    """  """
    message = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_INFO, gtk.BUTTONS_OK, msg)
    resp = message.run()
    message.destroy()

def show_error_dlg(error_string):
	"""This Function is used to show an error dialog when an error occurs.
	error_string - The error string that will be displayed 	on the dialog."""
    
	error_dlg = gtk.MessageDialog(type=gtk.MESSAGE_ERROR,
				                  message_format=error_string,
				                  buttons=gtk.BUTTONS_OK)
	error_dlg.run()
	error_dlg.destroy()

def image_button(label, image, size):
    bt = gtk.Button()
    bt.set_relief(gtk.RELIEF_NONE)
    bt.set_border_width(0)
    bt.set_focus_on_click(False)
    bt.set_property('can-focus', False)

    box = gtk.HBox(False, 6)
    box.set_border_width(2)
    box.show()

    if image == None:
        bt_image = gtk.Image()
        pixbuf = pixbuf_from_file('images/def_icon.png', size, size)
        bt_image.set_from_pixbuf(pixbuf)
        
    elif type(image) == gtk.Image:
        bt_image = image
        
    elif type(image) == gtk.gdk.Pixbuf:
        bt_image = gtk.Image()
        bt_image.set_from_pixbuf(image)
        
    else:
        bt_image = gtk.Image()
        try:
            pixbuf = get_pixbuf_icon(image, size)
            bt_image.set_from_pixbuf(pixbuf)
        except:
            pass

    bt_image.show()
    bt_image.set_size_request(size, size)
    box.pack_start(bt_image, False, False)
    
    if label is not None:
        bt_label = gtk.Label()
        bt_label.set_use_markup(True)
        if '&' in label:
            label = label.replace('&', '&amp;')
                 
        bt_label.set_markup(label)
        bt_label.set_alignment(0.2, 1)
        align = gtk.Alignment(1, 0, 0.5, 0.5)
        align.show()
        align.add(bt_label)
        box.pack_start(align, False, False)

    bt.add(box)
    bt.show_all()
    return bt

def set_icon(icon, dst, item=None, size=None):
    
    # update icon for gtk.Image
    if type(dst) == gtk.Image:
        
        if not size:
            size = 64
        
        if os.path.isfile(icon) and '.' in icon:
            try:
                dst.set_from_pixbuf(pixbuf_from_file(icon, size, size))
            except:
                dst.set_from_stock(gtk.STOCK_MISSING_IMAGE, gtk.ICON_SIZE_DIALOG)
                
        elif ICON_THEME.has_icon(icon):
            pixbuf = ICON_THEME.load_icon(icon, size, gtk.ICON_LOOKUP_USE_BUILTIN)
            dst.set_from_pixbuf(pixbuf)
        else:
            dst.set_from_stock(gtk.STOCK_MISSING_IMAGE, gtk.ICON_SIZE_DIALOG)
            
    # update icon for "view"
    else:

        # Update icon
        try:
            if os.path.exists(icon) and '.' in icon:
                dst.set_value(item, ID_ICON, pixbuf_from_file(icon, 32, 32) )
            elif ICON_THEME.has_icon(icon):
                pixbuf = ICON_THEME.load_icon(icon, 32, gtk.ICON_LOOKUP_USE_BUILTIN)
                dst.set_value(item, ID_ICON, pixbuf)
            else:
                dst.set_value(item, ID_ICON, pixbuf_from_file('images/def_icon.png', 32, 32) )
                
        except:
            print '* Listview Error while adding pixbuf  .. !'


def get_pixbuf_icon(icon_value, size=24):
    if not icon_value:
        return None

    #~ if os.path.isabs(icon_value):
    if os.path.isfile(icon_value) and not os.path.isdir(icon_value):
        try:
            return gtk.gdk.pixbuf_new_from_file_at_size(icon_value, size, size)
        except glib.GError:
            print 'core.get_pixbuf_icon : gtk.gdk.pixbuf_new_from_file_at_size >> glib.GError'
            return None
                
        icon_name = os.path.basename(icon_value)
    else:
        icon_name = icon_value

    if re.match(".*\.(png|xpm|svg)$", icon_name) is not None:
        icon_name = icon_name[:-4]
    try:
        return ICON_THEME.load_icon(icon_name, size, gtk.ICON_LOOKUP_FORCE_SIZE)
    except:
        for dir in BaseDirectory.xdg_data_dirs:
            for i in ("pixmaps", "icons"):
                path = os.path.join(dir, i, icon_value)
                if os.path.isfile(path):
                    return gtk.gdk.pixbuf_new_from_file_at_size(path, size, size)

class App:
    
    Name = ''
    Icon = ''
    Exec = ''
    Terminal = False
    Comment = ''

class XdgMenu():
    
    def __init__(self, select_menu='applications'):
        
        self.applications = {}
        self.category = None

        if os.path.isfile('/etc/xdg/menus/%s.menu' % select_menu):
            xdgmenu = xdg.Menu.parse('/etc/xdg/menus/%s.menu' % select_menu)
            self.process_menu(xdgmenu)
        else:
            print ('Menu -', '/etc/xdg/menus/%s.menu' % select_menu)
            print ('-- not found')

    def getMenu(self):
        return self.applications

    def process_menu(self, menu):

        for entry in menu.getEntries():
            if isinstance(entry, xdg.Menu.Menu):
                name = entry.getName()
                icon = entry.getIcon()
                self.applications[name] = (icon,[])
                self.category = name
                self.process_menu(entry)

            elif isinstance(entry, xdg.Menu.MenuEntry):
                app = App()
                de = entry.DesktopEntry
                app.Name = de.getName()
                app.Icon = de.getIcon()
                app.Comment = de.getComment()
                app.Exec = de.getExec()
                app.Terminal = de.getTerminal()
                self.applications[self.category][1].append(app)
