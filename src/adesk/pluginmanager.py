# -*- coding: utf-8 -*-

# extra modules
import gtk
import traceback
import gobject

# adeskbar modules
import core

DEBUG = 0

class PluginManager:
    """ Class AppManager - load/resize plugins for main bar """
    
    def __init__( self, bar ):
        """ configure container for plugins """

        self.bar = bar
        self.index = []
        self.plugins = {}

        if bar.cfg['position'] == "top" or bar.cfg['position'] == "bottom":
            self.box = gtk.HBox(False, bar.cfg['icon_space'])
        else:
            self.box = gtk.VBox(False, bar.cfg['icon_space'])

        self.spacer_left_top = gtk.EventBox()
        self.spacer_left_bottom = gtk.EventBox()
        self.spacer_right = gtk.EventBox()
        
        if not DEBUG:
            self.spacer_left_top.set_visible_window(False)
            self.spacer_left_bottom.set_visible_window(False)
            self.spacer_right.set_visible_window(False)

        self.table = gtk.Table(3, 3, False)
        self.table.set_row_spacings(0)
        self.table.set_col_spacings(0)

        self.table.attach(self.spacer_left_top, 0, 1, 0, 1, xoptions=gtk.SHRINK, yoptions=gtk.SHRINK)
        self.table.attach(self.spacer_left_bottom, 0, 1, 2, 3, xoptions=gtk.SHRINK, yoptions=gtk.SHRINK)
        self.table.attach(self.spacer_right, 2, 3, 0, 1, xoptions=gtk.SHRINK, yoptions=gtk.SHRINK)
        
        if self.bar.cfg['fixed_mode']:
            self.table.attach(self.box, 1, 2, 1, 2, xoptions=gtk.EXPAND|gtk.FILL, yoptions=gtk.EXPAND|gtk.FILL)
        else:
            self.table.attach(self.box, 1, 2, 1, 2, xoptions=gtk.SHRINK, yoptions=gtk.SHRINK)

        bar.win.add(self.table)
        self.resize_spacer()
        self.table.show_all()

        self.box_alloc = self.box.get_allocation()


    def on_init(self):
        for index in self.plugins:
            self.plugins[index].on_init()

    def run(self):
        #~ if not self.bar.cfg['fixed_mode']:
        self.box.connect('size-allocate', self.box_size_allocate)

    def load_plugin(self, launcher, is_plugin = False):
        """ load plugin as widget """
        
        try:
            
            if is_plugin:
                exec("import plugins.%s as plugin" % launcher['cmd'][1:])
            else:
                exec("import plugins.launcher as plugin")
                
            widget = plugin.Plugin(self.bar, launcher)
            
        except Exception as e:
            traceback.print_exc()
            return None

        return widget

    def append(self, index, launcher):
        """ append plugin (widget) to main bar """

        is_plugin = False
        is_separator = False

        if len(launcher['cmd']) > 1 and launcher['cmd'][0] == '@':
            is_plugin = True

            if launcher['cmd'][1:] == 'separator':
                is_separator = True

            elif launcher['cmd'][1:] == 'drawer' and index in self.bar.drawer:
                    launcher['launcher'] = self.bar.drawer[index]

        widget = self.load_plugin(launcher, is_plugin)

        if widget: # load OK
            widget.tooltip = launcher['name']
            widget.index = index

            if widget.can_show_icon:
                widget.set_icon(launcher['icon'], is_separator)

            widget.resize()
            widget.connect("button-release-event", self.bar.widget_released)
            widget.connect("button-press-event", self.bar.widget_press)
            widget.connect("enter-notify-event", self.bar.widget_enter_notify)
            widget.connect("leave-notify-event", self.bar.launcher_leave_notify)

            widget.show()

            #~ if launcher['cmd'][1:] == 'tasklist' or launcher['cmd'][1:] == 'expander':

            if launcher['cmd'][1:] == 'expander' or (launcher['cmd'][1:] == 'tasklist' and int(launcher['expand'])):
                self.box.pack_start(widget, True, True)
            else:
                self.box.pack_start(widget, False, False)

            self.index.append(index)
            self.plugins[index] = widget
            return widget
        else:
            return None        

    def remove(self, index):
        self.index.remove(index)
        self.plugins[index].hide()
        self.plugins[index].destroy()
        self.plugins.pop(index)
        self.bar.reposition()

    def reorder(self, index, position):
        self.box.reorder_child(self.plugins[index], position)
        self.index.remove(index)
        self.index.insert(position, index)

    def box_size_allocate(self, widget, allocation):
        """ resize to minimum size and reposition """
        if not self.box_alloc == allocation:
            self.box.set_size_request(-1, -1)
            self.bar.win.resize(1, 1)
            gobject.idle_add(self.bar.reposition)

        self.box_alloc = allocation

    def resize_spacer(self):
        """ configure main bar aspect from config """
        cfg = self.bar.cfg
        
        padding = cfg['padding']
        size, zoom_f, space = cfg['icon_size'], cfg['zoom_factor'], cfg['icon_space']
        offset_top = max( padding, int(size * zoom_f - size) )
        offset_side = 2*padding

        if cfg['position']=='bottom':
            self.spacer_left_top.set_size_request(offset_side, offset_top)
            self.spacer_left_bottom.set_size_request(offset_side, padding)
            self.spacer_right.set_size_request(offset_side, padding)

        elif cfg['position']=='top':
            self.spacer_left_top.set_size_request(offset_side, padding)
            self.spacer_left_bottom.set_size_request(offset_side, offset_top)
            self.spacer_right.set_size_request(offset_side, padding)

        elif cfg['position']=='left':
            self.spacer_left_top.set_size_request(padding, offset_side)
            self.spacer_left_bottom.set_size_request(padding, offset_side)
            self.spacer_right.set_size_request(offset_top, offset_side)

        elif cfg['position']=='right':
            self.spacer_left_top.set_size_request(offset_top, offset_side)
            self.spacer_left_bottom.set_size_request(offset_top, offset_side)
            self.spacer_right.set_size_request(padding, offset_side)

    def set_orientation(self):
        if self.bar.cfg['position'] == "top" or self.bar.cfg['position'] == "bottom":
            self.box.set_orientation(gtk.ORIENTATION_HORIZONTAL)
        else:
            self.box.set_orientation(gtk.ORIENTATION_VERTICAL)

    def set_panel_mode(self):
        self.table.remove(self.box)
        if self.bar.cfg['fixed_mode']:
            self.table.attach(self.box, 1, 2, 1, 2, xoptions=gtk.EXPAND|gtk.FILL, yoptions=gtk.EXPAND|gtk.FILL)
        else:
            self.table.attach(self.box, 1, 2, 1, 2, xoptions=gtk.SHRINK, yoptions=gtk.SHRINK)
