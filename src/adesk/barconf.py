# -*- coding: utf-8 -*-

##
#   ADesk Bar - UI config
##

## python modules
import os
import sys
import gtk
import gobject
import string
import locale
import gettext
import traceback
import time
import re

# adeskbar modules
import core
import plugin
import config
import ui
import release

## Test
#~ import check

## Translation
locale.setlocale(locale.LC_ALL, '')
#~ gettext.install('adeskbar', './locale', unicode=1)
gettext.bindtextdomain('adeskbar', './locale')
gettext.bind_textdomain_codeset('adeskbar','UTF-8') 
gettext.textdomain('adeskbar')
_ = gettext.gettext

# position in list
ID_ICON  = 0
ID_NAME = 1
ID_IND = 2
ID_CMD = 2
ID_IMG = 3


ABOUT_TXT = """
application launcher for Openbox.
By David Art [a.k.a] ADcomp
Email : david.madbox@gmail.com
Web : http://adeskbar.tuxfamily.org/
"""

def set_icon(icon, dst, item=None, size=None):
    
    # update icon for gtk.Image
    if type(dst) == gtk.Image:
        
        if not size:
            size = 64
        
        if os.path.isfile(icon) and '.' in icon:
            # Update property image:
            try:
                dst.set_from_pixbuf(core.pixbuf_from_file(icon, size, size))
            except:
                dst.set_from_stock(gtk.STOCK_MISSING_IMAGE, gtk.ICON_SIZE_DIALOG)
                
        elif core.ICON_THEME.has_icon(icon):
            pixbuf = core.ICON_THEME.load_icon(icon, size, gtk.ICON_LOOKUP_USE_BUILTIN)
            dst.set_from_pixbuf(pixbuf)
        else:
            dst.set_from_stock(gtk.STOCK_MISSING_IMAGE, gtk.ICON_SIZE_DIALOG)
            
    # update icon for "view"
    else:
        pixbuf = core.get_pixbuf_icon(icon, 32)
        # Update icon
        if pixbuf is None:
            pixbuf = core.get_pixbuf_icon('images/def_icon.png', 32)
        try:
            dst.set_value(item, ID_ICON, pixbuf)
        except:
            print '* Listview Error while adding pixbuf  .. !'
        
class Conf():

    def __init__(self, bar):

        ## tab for (position,align) on screen
        self.pos_align = [(1,0),(1,1),(1,2),
                          (3,0),(3,1),(3,2),
                          (0,0),(0,1),(0,2),
                          (2,0),(2,1),(2,2)]

        self.pos_tab = ['bottom','top','left','right']
        self.align_tab = ['start','center','end']

        self.bar = bar
        self.cfg_file = bar.cfg_file
        self.config = bar.cfg
        self.plg_mgr = bar.plg_mgr
        self.launcher = bar.launcher
        self.drawer = bar.drawer

        ## Gtk Stuff
        self.ui_Main()

    def ui_Main(self):
        # Create window
        self.window = gtk.Window() #gtk.WINDOW_TOPLEVEL)
        self.window.set_title("ADeskBar %s - %s" % (_('Settings'), self.bar.cfg_file))
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.connect("destroy", self.destroy)
        self.window.set_icon_from_file('images/adeskbar.png')
        self.screen_pixbuf = core.pixbuf_from_file('images/conf/display.png')

        self.nbook = gtk.Notebook()
        self.nbook.set_show_tabs(False)
        self.nbook.set_border_width(0)
        self.current_page = 0

        # IconView
        self.frame_iconView = gtk.Frame()
        store = gtk.ListStore(str, gtk.gdk.Pixbuf)
            
        ## preferences
        pixbuf = core.pixbuf_from_file('images/conf/preferences.png')
        store.append([_('preferences'), pixbuf])

        ## position
        pixbuf = core.pixbuf_from_file('images/conf/position.png')
        store.append([_('position'), pixbuf])

        ## launchers
        pixbuf = core.pixbuf_from_file('images/conf/launchers.png')
        store.append([_('launchers'), pixbuf])

        ## advanced
        pixbuf = core.pixbuf_from_file('images/conf/advanced.png')
        store.append([_('advanced'), pixbuf])

        iconView = gtk.IconView(store)
        iconView.set_text_column(0)
        iconView.set_pixbuf_column(1)
        iconView.set_spacing(0)
        iconView.set_margin(0)
        iconView.set_column_spacing(0)
        iconView.set_row_spacing(0)
        iconView.connect("selection-changed", self.iconView_activated)
        iconView.select_path(0)
        self.frame_iconView.add(iconView)
        
        # Containers
        BoxControls = gtk.HBox()
        BoxControls.set_spacing(4)

        ## Main Controls
        
        # test
        #~ button_refresh = gtk.Button(stock=gtk.STOCK_PROPERTIES)
        #~ button_refresh.connect("clicked", self.my_test)
        #~ BoxControls.pack_end(button_refresh, False, False)
        
        # About
        self.bt_about = gtk.Button(stock=gtk.STOCK_ABOUT)
        self.bt_about.connect("clicked", self.switch_about)
        BoxControls.pack_start(self.bt_about, False, False)
        
        # Exit
        button = gtk.Button(stock=gtk.STOCK_CLOSE)
        button.connect("clicked", self.close_and_save)
        BoxControls.pack_end(button, False, False)

        self.ui_Preferences()
        self.ui_Position()
        self.ui_Launcher()
        self.ui_Advanced()
        self.ui_About()

        BoxBase = gtk.VBox()
        BoxBase.set_spacing(4)
        BoxBase.set_border_width(12)
        BoxBase.pack_start(self.frame_iconView, False)
        BoxBase.pack_start(self.nbook, True)
        BoxBase.pack_start(gtk.HSeparator(), False)
        BoxBase.pack_end(BoxControls, False)

        self.window.add(BoxBase)
        self.window.resize(450, 400)
        self.window.show_all()

    def my_test(self, widget=None):
        for ind in self.bar.configuration.l_ind:
            print 'a) ', self.bar.configuration.launcher[ind]
            print 'b) ', self.launcher[ind]
            print 

    def switch_page(self, flag_edit=False):
        if self.nbook.get_current_page() == 2 or flag_edit:
            self.frame_iconView.hide()
            self.bt_about.hide()
            self.nbook.set_current_page(-1)
        else:
            self.frame_iconView.show()
            self.bt_about.show()
            self.nbook.set_current_page(2)

    def switch_about(self, widget=None):
        if not self.nbook.get_current_page() == 4:
            self.frame_iconView.hide()
            self.nbook.set_current_page(4)
        else:
            self.frame_iconView.show()
            self.nbook.set_current_page(self.current_page)

    def iconView_activated(self, widget):
        cursor = widget.get_cursor()
        if cursor:
            self.nbook.set_current_page(cursor[0][0])
            self.current_page = cursor[0][0]

    def ui_Preferences(self):
        bBox = gtk.VBox()
        bBox.set_spacing(10)
        bBox.set_border_width(10)

        label_icon_size = gtk.Label(_('Size'))

        ## Size
        adjustment = gtk.Adjustment(value=self.config['icon_size'], lower=24, upper=256, step_incr=8, page_incr=16, page_size=0)
        self.icon_size = gtk.SpinButton(adjustment=adjustment, climb_rate=0.0, digits=0)
        self.icon_size.connect("value-changed", self.set_icon_size)
        self.icon_size.set_tooltip_text('Size in pixel')

        box = gtk.HBox()
        box.set_spacing(10)
        box.pack_start(label_icon_size, False, False)
        box.pack_end(self.icon_size, False, False)
        bBox.pack_start(box, False, True)

        ## Style
        self.bar_style = gtk.combo_box_new_text()
        self.bar_style.connect("changed", self.set_bar_style)
        self.bar_style.append_text(_('Edgy'))
        self.bar_style.append_text(_('Floaty'))
        if self.bar.is_composited:
            self.bar_style.append_text(_('3d'))
        self.bar_style.set_active(self.config['bar_style'])

        box = gtk.HBox()
        box.set_spacing(10)
        box.pack_start(gtk.Label(_('Style')), False, False)
        box.pack_end(self.bar_style, False, False)
        bBox.pack_start(box, False, True)

        ## Icons effects
        self.icons_effects = gtk.combo_box_new_text()
        self.icons_effects.connect("changed", self.set_icons_effects)
        self.icons_effects.append_text('None')
        self.icons_effects.append_text('Glow')
        self.icons_effects.append_text('Simple')
        self.icons_effects.append_text('Zoom')
        self.icons_effects.set_active(self.config['icons_effects'])

        box = gtk.HBox()
        box.set_spacing(10)
        box.pack_start(gtk.Label(_('Icons effects')), False, False)
        box.pack_end(self.icons_effects, False, False)
        bBox.pack_start(box, False, True)

        ## Behavior (hide mode)
        self.auto_hide = gtk.combo_box_new_text()
        self.auto_hide.connect("changed", self.set_auto_hide)
        self.auto_hide.append_text(_('Always visible'))
        self.auto_hide.append_text(_('Autohide'))

        if self.bar.wnck:
            self.auto_hide.append_text(_('Intellihide'))
        self.auto_hide.set_active(self.config['auto_hide'])

        box = gtk.HBox()
        box.set_spacing(10)
        box.pack_start(gtk.Label(_('Behavior')), False, False)
        box.pack_end(self.auto_hide, False, False)
        bBox.pack_start(box, False, True)

        ## Fixed mode
        adjustment = gtk.Adjustment(value=self.config['fixed_size'], lower=1, upper=100, step_incr=0.5, page_incr=0, page_size=0)
        self.fixed_size = gtk.SpinButton(adjustment=adjustment, climb_rate=0.0, digits=1)
        self.fixed_size.set_tooltip_text('"panel" size in %')
        self.fixed_size.connect("value-changed", self.set_fixed_size)

        self.fixed_mode_checkbox = gtk.CheckButton(_('fixed mode ( aka "panel" )'))
        self.fixed_mode_checkbox.set_active(self.config['fixed_mode'])
        self.fixed_mode_checkbox.connect("toggled", self.set_fixed_mode)

        box = gtk.HBox()
        box.set_spacing(10)
        box.pack_start(self.fixed_mode_checkbox, False, False)
        box.pack_end(self.fixed_size, False, False)
        bBox.pack_start(box, False, True)

        ## reserve space at screen edge
        self.reserve_space_checkbox = gtk.CheckButton(_('reserve space at screen edge'))
        self.reserve_space_checkbox.set_active(self.config['reserve_space'])
        self.reserve_space_checkbox.connect("toggled", self.set_reserve_space)

        box = gtk.HBox()
        box.set_spacing(10)
        box.pack_start(gtk.Label('    '), False, False)
        box.pack_start(self.reserve_space_checkbox, False, False)
        bBox.pack_start(box, False, True)

        ## Separator
        bBox.pack_start(gtk.HSeparator(), False, False)

        # Auto-raise
        self.autoraise_checkbox = gtk.CheckButton(_('Show on mouse over'))
        self.autoraise_checkbox.set_active(self.config['auto_raise'])
        self.autoraise_checkbox.connect("toggled", self.set_auto_raise)
        
        bBox.pack_start(self.autoraise_checkbox, False, True)

        # keep_below other window
        self.keep_below_checkbox = gtk.CheckButton(_('Keep below other windows'))
        self.keep_below_checkbox.set_active(self.config['keep_below'])
        self.keep_below_checkbox.connect("toggled", self.set_keep_below)
        
        bBox.pack_start(self.keep_below_checkbox, False, True)

        # Show tooltips
        self.tooltips_checkbox = gtk.CheckButton(_('Show launchers tooltips'))
        self.tooltips_checkbox.set_active(self.config['tooltips'])
        self.tooltips_checkbox.connect("toggled", self.set_tooltips)
        
        bBox.pack_start(self.tooltips_checkbox, False, True)

        label = gtk.Label('Preferences')
        self.nbook.append_page(bBox, label)

    def ui_About(self):

        mainbox = gtk.VBox()
        mainbox.set_border_width(0)
        mainbox.set_spacing(0)

        about_box = gtk.HBox()
        about_box.set_border_width(0)
        about_box.set_spacing(0)

        img = gtk.Image()
        img.set_from_file('images/adeskbar.png')
        about_box.pack_start(img, 0, 0)

        r_box = gtk.VBox()
        r_box.set_border_width(10)
        r_box.set_spacing(2) 
        
        about_box.pack_start(r_box, 0, 0)

        label = gtk.Label()
        label.set_use_markup(True)
        label.set_markup("<b>ADesk Bar - <small>v%s.%s</small></b>" % (release.VERSION, release.RC))
        label.set_alignment(0,0.5)
        r_box.pack_start(label, 0)

        label = gtk.Label()
        label.set_use_markup(True)
        label.set_markup(ABOUT_TXT)
        label.set_alignment(0,0.5)
        r_box.pack_start(label, 0)

        #~ mod_box = gtk.VBox(False, 10)
        #~ mod_box.set_border_width(10)
        #~ check.check_modules(mod_box)
        #~ scrolled = gtk.ScrolledWindow()
        #~ scrolled.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        #~ scrolled.add_with_viewport(mod_box)

        mainbox.pack_start(about_box, 0)
        #~ mainbox.pack_start(scrolled)
        

        label = gtk.Label('About')
        self.nbook.append_page(mainbox, label)

    def ui_Position(self):
        bBox = gtk.VBox()
        bBox.set_border_width(10)
        bBox.set_spacing(10)
        bBox.pack_start(gtk.Label(_("Select position on screen")), False, False)

        align = gtk.Alignment(0.5,0.5,0,0)
        bBox.pack_start(align)

        table = gtk.Table(5, 5, False)

        self.area = gtk.DrawingArea()
        self.area.set_size_request(160, 116)
        self.area.connect("expose-event", self.area_expose)
        self.pangolayout = self.area.create_pango_layout("")

        button_pos = []
        for i in range(12):
            but = gtk.Button()
            if i in (3,4,5,9,10,11):
                but.set_size_request(20, 38)
            else:
                but.set_size_request(50, 20)
            #~ but.set_relief(gtk.RELIEF_NONE)
            but.set_border_width(0)
            but.set_focus_on_click(False)
            but.set_property('can-focus', False)
            but.connect("clicked", self.area_update_pos, i)
            button_pos.append(but)

        table.attach(button_pos[0], 1, 2, 0, 1)
        table.attach(button_pos[1], 2, 3, 0, 1)
        table.attach(button_pos[2], 3, 4, 0, 1)

        table.attach(button_pos[3], 4, 5, 1, 2)
        table.attach(button_pos[4], 4, 5, 2, 3)
        table.attach(button_pos[5], 4, 5, 3, 4)

        table.attach(button_pos[6], 1, 2, 4, 5)
        table.attach(button_pos[7], 2, 3, 4, 5)
        table.attach(button_pos[8], 3, 4, 4, 5)

        table.attach(button_pos[9], 0, 1, 1, 2)
        table.attach(button_pos[10], 0, 1, 2, 3)
        table.attach(button_pos[11], 0, 1, 3, 4)

        table.attach(self.area, 1, 4, 1, 4)
        align.add(table)


        self.position = self.pos_tab.index(self.config['position'])
        self.align = self.align_tab.index(self.config['align'])


        ## OFFSET POSITION
        adjustment = gtk.Adjustment(value=self.config['offset_pos'], lower=0, upper=1000, step_incr=1, page_incr=10, page_size=0)
        self.spin_offset_pos = gtk.SpinButton(adjustment=adjustment, climb_rate=0.0, digits=0)
        self.spin_offset_pos.connect("value-changed", self.set_offset_pos)
        label = gtk.Label(_("Offset - position"))

        box = gtk.HBox()
        box.set_spacing(10)
        box.pack_start(label, False, False)
        box.pack_end(gtk.Label('px'), False, False)
        box.pack_end(self.spin_offset_pos, False, False)
        bBox.pack_start(box, False, True)

        ## OFFSET ALIGN
        adjustment = gtk.Adjustment(value=self.config['offset_align'], lower=0, upper=1000, step_incr=1, page_incr=10, page_size=0)
        self.spin_offset_align = gtk.SpinButton(adjustment=adjustment, climb_rate=0.0, digits=0)
        self.spin_offset_align.connect("value-changed", self.set_offset_align)
        label = gtk.Label(_("Offset - align"))

        box = gtk.HBox()
        box.set_spacing(10)
        box.pack_start(label, False, False)
        box.pack_end(gtk.Label('px'), False, False)
        box.pack_end(self.spin_offset_align, False, False)
        bBox.pack_start(box, False, True)

        label = gtk.Label('Position')
        self.nbook.append_page(bBox, label)

    def ui_Launcher(self):
        
        self.app_menu = ui.Menu(self.new_item_menu)
        self.plugin_menu = PluginMenu(self.new_item_plugin)

        bBox = gtk.HBox(False,0)
        bBox.set_spacing(10)
        bBox.set_border_width(4)

        BoxListControls = gtk.VBox(False,0)

        # ListStore
        self.view = View(self)
        self.view.connect("row-activated", self.edit_item)
        
        for index in self.plg_mgr.index:
            name = self.plg_mgr.plugins[index].settings['name']
            icon = self.plg_mgr.plugins[index].settings['icon']
            self.view.add_launcher(name, icon, index)

        self.view.model.connect("row-deleted", self.view.row_deleted)

        scrolled = gtk.ScrolledWindow()
        scrolled.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolled.add(self.view)
        frame = gtk.Frame()
        frame.add(scrolled)

        # Add from menu
        button = core.image_button(_('add from menu'), 
                                'images/conf/add_app.png', 24)
        button.connect("clicked", self.popup_menu)
        BoxListControls.pack_start(button, False, False)

        # Add Plugin
        button = core.image_button(_('add plugin'), 
                                'images/conf/add_plugin.png', 24)
        button.connect("clicked", self.popup_plugin)
        BoxListControls.pack_start(button, False, False)

        # Add custom
        button = core.image_button(_('add custom launcher'), 
                                'images/conf/add_custom.png', 24)
        button.connect("clicked", self.new_item_custom)
        BoxListControls.pack_start(button, False, False)

        # Remove
        button = core.image_button(_('remove'), 
                                'images/conf/remove.png', 24)
        button.connect("clicked", self.remove_item)
        BoxListControls.pack_end(button, False, False)

        bBox.pack_start(BoxListControls, False, False)
        bBox.pack_start(frame, True)

        label = gtk.Label('Launcher')
        self.nbook.append_page(bBox, label)

    def ui_Advanced(self):
        bBox = gtk.VBox()
        bBox.set_spacing(10)
        bBox.set_border_width(10)


        ## Label is no Composite
        if not self.bar.is_composited:
            label = gtk.Label()
            label.set_use_markup(True)
            label.set_markup("<b>No X Composite</b> : some options are disabled")
            label.set_alignment(0, 0.5)
            bBox.pack_start(label, False, True)

        ## Separator
        bBox.pack_start(gtk.HSeparator(), False, False)

        ## Opacity (composite)
        adjustment = gtk.Adjustment(value=self.config['opacity'], lower=0, upper=100, step_incr=5, page_incr=10, page_size=0)
        self.opacity = gtk.SpinButton(adjustment=adjustment, climb_rate=0.0, digits=0)
        self.opacity.connect("value-changed", self.set_opacity)

        if not self.bar.is_composited:
            self.opacity.set_sensitive(False)

        box = gtk.HBox()
        box.set_spacing(10)
        box.pack_start(gtk.Label(_('Opacity')), False, False)
        #~ box.pack_end(gtk.Label('%'), False, False)
        box.pack_end(self.opacity, False, False)
        bBox.pack_start(box, False, True)

        ## Separator
        bBox.pack_start(gtk.HSeparator(), False, False)

        ## bar size factor
        adjustment = gtk.Adjustment(value=self.config['bar_size'], lower=5, upper=100, step_incr=5, page_incr=10, page_size=0)
        self.bar_size = gtk.SpinButton(adjustment=adjustment, climb_rate=0.0, digits=0)
        self.bar_size.connect("value-changed", self.set_bar_size)
        
        if not self.bar.is_composited:
            self.bar_size.set_sensitive(False)

        box = gtk.HBox()
        box.set_spacing(10)
        box.pack_start(gtk.Label(_('Bar size')), False, False)
        #~ box.pack_end(gtk.Label('%'), False, False)
        box.pack_end(self.bar_size, False, False)
        bBox.pack_start(box, False, True)

        ## rounded corner
        adjustment = gtk.Adjustment(value=self.config['rounded_corner'], lower=0, upper=100, step_incr=5, page_incr=10, page_size=0)
        self.rounded_corner = gtk.SpinButton(adjustment=adjustment, climb_rate=0.0, digits=0)
        self.rounded_corner.connect("value-changed", self.set_rounded_corner)

        box = gtk.HBox()
        box.set_spacing(10)
        box.pack_start(gtk.Label(_('Rounded')), False, False)
        #~ box.pack_end(gtk.Label('%'), False, False)
        box.pack_end(self.rounded_corner, False, False)
        bBox.pack_start(box, False, True)

        ## Separator
        bBox.pack_start(gtk.HSeparator(), False, False)

        ## Space beetwen Launcher
        adjustment = gtk.Adjustment(value=self.config['icon_space'], lower=1, upper=32, step_incr=1, page_incr=2, page_size=0)
        self.icon_space = gtk.SpinButton(adjustment=adjustment, climb_rate=0.0, digits=0)
        self.icon_space.connect("value-changed", self.set_icon_space)

        box = gtk.HBox()
        box.set_spacing(10)
        box.pack_start(gtk.Label(_('Space between icon')), False, False)
        #~ box.pack_end(gtk.Label('px'), False, False)
        box.pack_end(self.icon_space, False, False)
        bBox.pack_start(box, False, True)

        ## Icon padding
        adjustment = gtk.Adjustment(value=self.config['padding'], lower=1, upper=32, step_incr=1, page_incr=2, page_size=0)
        self.padding = gtk.SpinButton(adjustment=adjustment, climb_rate=0.0, digits=0)
        self.padding.connect("value-changed", self.set_padding)

        box = gtk.HBox()
        box.set_spacing(10)
        box.pack_start(gtk.Label(_('Icon padding')), False, False)
        #~ box.pack_end(gtk.Label('px'), False, False)
        box.pack_end(self.padding, False, False)
        bBox.pack_start(box, False, True)

        ## Zoom factor
        adjustment = gtk.Adjustment(value=self.config['zoom_factor'], lower=1.0, upper=1.3, step_incr=0.05, page_incr=0.1, page_size=0)
        self.zoom_factor = gtk.SpinButton(adjustment=adjustment, climb_rate=0.0, digits=2)
        self.zoom_factor.connect("value-changed", self.set_zoom_factor)

        box = gtk.HBox()
        box.set_spacing(10)
        box.pack_start(gtk.Label(_('Zoom Factor')), False, False)
        box.pack_end(self.zoom_factor, False, False)
        bBox.pack_start(box, False, True)

        ## Separator
        bBox.pack_start(gtk.HSeparator(), False, False)

        ## Backgroung color
        map = self.window.get_colormap()
        colour = map.alloc_color(self.config['bg_color'])

        self.bt_bg_color  = gtk.ColorButton(colour)
        self.bt_bg_color.connect('color-set', self.set_bg_color)

        box = gtk.HBox()
        box.pack_start(gtk.Label(_('Background color [ Bar ]')), False, False)
        box.pack_end(self.bt_bg_color, False, False)
        bBox.pack_start(box, False, True)

        # bg_gradient
        colour = map.alloc_color(self.config['bg_gradient_color'])
        self.bt_bg_gradient_color = gtk.ColorButton(colour)
        self.bt_bg_gradient_color.set_use_alpha(True)
        self.bt_bg_gradient_color.set_alpha(self.config['bg_gradient_alpha'])
        self.bt_bg_gradient_color.connect('color-set', self.set_bg_gradient_color)



        self.bg_gradient_checkbox = gtk.CheckButton(_('add some gradients'))
        self.bg_gradient_checkbox.set_active(self.config['bg_gradient'])
        self.bg_gradient_checkbox.connect("toggled", self.set_bg_gradient)
       
        box = gtk.HBox()
        box.set_spacing(10)
        box.pack_start(self.bg_gradient_checkbox, False, False)
        box.pack_end(self.bt_bg_gradient_color, False, False)
        bBox.pack_start(box, False, True) 

        # Show border checkbox / color
        self.showborder_checkbox = gtk.CheckButton(_('Show border'))
        self.showborder_checkbox.set_active(self.config['show_border'])
        self.showborder_checkbox.connect("toggled", self.set_border)

        colour = map.alloc_color(self.config['border_color'])
        self.bt_border_color = gtk.ColorButton(colour)
        self.bt_border_color.connect('color-set', self.set_border_color)

        box = gtk.HBox()
        box.set_spacing(10)
        box.pack_start(self.showborder_checkbox, False, False)
        box.pack_end(self.bt_border_color, False, False)
        bBox.pack_start(box, False, True)

        ## Separator
        bBox.pack_start(gtk.HSeparator(), False, True)

        ## Color Tooltips/Plugins
        colour = map.alloc_color(self.config['bg_color_sub'])
        self.bt_bg_color_sub  = gtk.ColorButton(colour)
        self.bt_bg_color_sub.connect('color-set', self.set_color_sub)

        box = gtk.HBox()
        box.pack_start(gtk.Label(_('Background color [ Tooltips / Plugins ]')), False, False)
        box.pack_end(self.bt_bg_color_sub, False, False)
        bBox.pack_start(box, False, True)

        colour = map.alloc_color(self.config['border_color_sub'])
        self.bt_border_color_sub  = gtk.ColorButton(colour)
        self.bt_border_color_sub.connect('color-set', self.set_border_color_sub)

        box = gtk.HBox()
        box.pack_start(gtk.Label(_('Border color')), False, False)
        box.pack_end(self.bt_border_color_sub, False, False)
        bBox.pack_start(box, False, True)

        ## Separator
        bBox.pack_start(gtk.HSeparator(), False, True)

        ## Size when Hidden
        adjustment = gtk.Adjustment(value=self.config['hidden_size'], lower=1, upper=100, step_incr=1, page_incr=0, page_size=0)
        self.hidden_size = gtk.SpinButton(adjustment=adjustment, climb_rate=0.0, digits=0)
        self.hidden_size.connect("value-changed", self.set_hidden_size)
        self.hidden_size.set_tooltip_text('hidden size in pixel')

        box = gtk.HBox()
        box.set_spacing(10)
        box.pack_start(gtk.Label(_('Hidden size')), False, False)
        box.pack_end(self.hidden_size, False, False)
        bBox.pack_start(box, False, True)

        ## tempo Hidden
        adjustment = gtk.Adjustment(value=self.config['timer'], lower=0, upper=100, step_incr=1, page_incr=2, page_size=0)
        self.timer = gtk.SpinButton(adjustment=adjustment, climb_rate=0.0, digits=0)
        self.timer.connect("value-changed", self.set_timer)
        self.timer.set_tooltip_text('time in second')

        box = gtk.HBox()
        box.set_spacing(10)
        box.pack_start(gtk.Label(_('Hide after tempo (sec)')), False, False)
        box.pack_end(self.timer, False, False)
        bBox.pack_start(box, False, True)

        # Smooth hide
        self.smooth_hide_checkbox = gtk.CheckButton(_('smooth hiding ( animation )'))
        self.smooth_hide_checkbox.set_active(self.config['smooth_hide'])
        self.smooth_hide_checkbox.connect("toggled", self.set_smooth_hide)
        
        bBox.pack_start(self.smooth_hide_checkbox, False, True)

        # fully transparent when hidden
        self.fade_hidden_checkbox = gtk.CheckButton(_('Fully transparent when hidden'))
        self.fade_hidden_checkbox.set_active(self.config['fade_hidden'])
        self.fade_hidden_checkbox.connect("toggled", self.set_fade_hidden)
        bBox.pack_start(self.fade_hidden_checkbox, False, True)


        ## final pack ..
        scrolled = gtk.ScrolledWindow()
        scrolled.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scrolled.add_with_viewport(bBox)

        label = gtk.Label('Advanced')
        self.nbook.append_page(scrolled, label)

    def popup_menu(self, widget):
        
        def get_position(menu):
            x, y, w, h = widget.get_allocation()
            win_x, win_y = self.window.get_position()
            return (win_x + x, win_y + y + h + 24, False)
        
        self.app_menu.menu.popup(None, None, get_position, 0, 0)

    def popup_plugin(self, widget):

        def get_position(menu):
            x, y, w, h = widget.get_allocation()
            win_x, win_y = self.window.get_position()
            return (win_x + x, win_y + y + h + 24, False)

        self.plugin_menu.menu.popup(None, None, get_position, 0, 0)

    def area_expose(self, area, event):
        ## graphic context
        style = area.get_style()
        gc = style.fg_gc[gtk.STATE_NORMAL]
        ## draw pixbuf as "screen"
        area.window.draw_pixbuf(gc, self.screen_pixbuf, 0, 0, 0, 0, -1, -1, gtk.gdk.RGB_DITHER_NORMAL, 0, 0)

        if self.pos_tab[self.position] == "bottom":
            x2, y2 = 50, 10
            if self.align_tab[self.align]== "start":
                x1, y1 = 21, 83
            elif self.align_tab[self.align]== "center":
                x1, y1 = 55, 83
            elif self.align_tab[self.align]== "end":
                x1, y1 = 89, 83

        if self.pos_tab[self.position] == "top":
            x2, y2 = 50, 10
            if self.align_tab[self.align]== "start":
                x1, y1 = 21, 20
            elif self.align_tab[self.align]== "center":
                x1, y1 = 55, 20
            elif self.align_tab[self.align]== "end":
                x1, y1 = 89, 20

        if self.pos_tab[self.position] == "left":
            x2, y2 = 10, 35
            if self.align_tab[self.align]== "start":
                x1, y1 = 21, 20
            elif self.align_tab[self.align]== "center":
                x1, y1 = 21, 40
            elif self.align_tab[self.align]== "end":
                x1, y1 = 21, 57

        if self.pos_tab[self.position] == "right":
            x2, y2 = 10, 35
            if self.align_tab[self.align]== "start":
                x1, y1 = 130, 20
            elif self.align_tab[self.align]== "center":
                x1, y1 = 130, 40
            elif self.align_tab[self.align]== "end":
                x1, y1 = 130, 57

        ## draw bar position on screen
        area.window.draw_rectangle(gc, True, x1, y1, x2, y2)
        return True

    def area_update_pos(self, widget, ind):
        self.position ,self.align = self.pos_align[ind]
        self.window.queue_draw()

        self.config['position'] = self.pos_tab[self.position]
        self.config['align'] = self.align_tab[self.align]
        self.bar.plg_mgr.set_orientation()
        self.bar.plg_mgr.resize_spacer()
        for ind in self.bar.plg_mgr.plugins:
            self.bar.plg_mgr.plugins[ind].resize()
        self.bar.update_all()

    def edit_item(self, view, path=None, view_column=None):
        selection = view.get_cursor()[0][0]
        if (selection is not None):
            model = view.get_model()
            Edit_Item(self, model, selection)

    def check_systray(self):
        for index in self.launcher:
            if self.launcher[index]['cmd'] == '@systray':
                return True
        return False

    def new_item_custom(self, widget):
        app = core.App()
        app.Name = 'Custom'
        app.Icon = 'system-run'
        self.new_item_menu(widget, app)
        self.edit_item(self.view)

    def new_item(self):
        index = str(int(time.time()))
        self.view.new_entry(index)
        position = self.view.get_cursor()[0][0]
        model   = self.view.get_model()
        item    = model.get_iter(position)
        
        if position == None:
            core.logINFO(' -- no position in view ?')
            return False
        
        return (index, position, model, item)

    def new_item_plugin(self, widget, plugin_name):
        if plugin_name == 'systray' and self.check_systray():
            print 'already one systray ..'
            return

        ret = self.new_item()
        
        if ret:
            (index, position, model, item) = ret
        else:
            return 

        model.set_value(item, ID_NAME, self.plugin_menu._list[plugin_name]['Name'])
        set_icon(self.plugin_menu._list[plugin_name]['Icon'], model, item)
        
        ## create new launcher
        self.launcher[index] = {}
        self.launcher[index]['cmd'] = '@' + plugin_name
        self.launcher[index]['icon'] = self.plugin_menu._list[plugin_name]['Icon']
        self.launcher[index]['name'] = self.plugin_menu._list[plugin_name]['Name']

        try:
            exec("import plugins.%s.config as plugin_conf" % plugin_name)
            for key in plugin_conf.settings:
                self.launcher[index][key] = plugin_conf.settings[key]
        except Exception, e:
            # no conf for this plugin ? so continue
            #~ traceback.print_exc()
            pass

        if plugin_name == 'systray':
            print 'add systray, need to restart ..'
            # need to restart !!
            self.saveconf()
            self.bar.restart()
            self.plg_mgr = self.bar.plg_mgr
        else:
            if self.plg_mgr.add_plugin(index, position):
                self.plg_mgr.plugins[index].on_init()
            else:
                self.remove_item(None)
                self.bar.configuration.l_ind.remove(index)
                self.launcher.pop(index)

    def new_item_menu(self, widget, app):
        
        ret = self.new_item()
        
        if ret:
            (index, position, model, item) = ret
        else:
            return 

        model.set_value(item, ID_NAME, app.Name)
        set_icon(app.Icon, model, item)

        ## create new launcher
        self.launcher[index] = {}
        self.launcher[index]['name'] = app.Name
        
        if len(app.Icon) > 1 and not app.Icon[0] == '/':
            if re.match(".*\.(png|xpm|svg)$", app.Icon) is not None:
                self.launcher[index]['icon'] = app.Icon[:-4]
            else:
                self.launcher[index]['icon'] = app.Icon
        else:
            self.launcher[index]['icon'] = app.Icon
 
        command = app.Exec.split('%')[0]
        if app.Terminal:
            command = 'x-terminal-emulator -e %s' % command
        self.launcher[index]['cmd'] = command
        
        self.plg_mgr.add_plugin(index, position)

    def remove_item(self, widget):
        self.view.remove_item()

    def close_and_save(self, widget=None):
        self.window.hide()
        self.window.destroy()

    def destroy(self, widget=None, data=None):
        ## save change
        self.bar.configuration.save()
        ## and clear conf .. 
        self.bar.bar_conf = None

    ### callback #######################################################
    
    def set_opacity(self, widget):
        self.bar.opacity = widget.get_value()/100.0
        self.config['opacity'] = widget.get_value()
        self.bar.draw_bg()
        self.bar.update()

    def set_bar_size(self, widget):
        self.config['bar_size'] = widget.get_value()
        self.bar.update_all()

    def set_bar_style(self, widget):
        self.config['bar_style'] = int(widget.get_active())
        self.bar.update_all()

    def set_auto_hide(self, widget):
        self.config['auto_hide'] = int(widget.get_active())
        self.bar.toggle_hidden()
        #~ self.bar.update()

    def set_icons_effects(self, widget):
        self.config['icons_effects'] = int(widget.get_active())

    def set_rounded_corner(self, widget):
        self.config['rounded_corner'] = widget.get_value()
        self.bar.draw_bg()
        self.bar.update()

    def set_offset_pos(self, widget):
        self.config['offset_pos'] = int(widget.get_value())
        self.bar.update_all()
        
    def set_offset_align(self, widget):
        self.config['offset_align'] = widget.get_value()
        self.bar.update_all()

    def set_icon_space(self, widget):
        self.config['icon_space'] = widget.get_value()
        self.bar.plg_mgr.box.set_spacing(int(widget.get_value()))
        self.bar.update_all()

    def set_padding(self, widget):
        self.config['padding'] = int(widget.get_value())
        self.bar.plg_mgr.resize_spacer()
        self.bar.update_all()

    def set_zoom_factor(self, widget):
        self.config['zoom_factor'] = widget.get_value()
        self.bar.zoom_size = self.config['icon_size'] * self.config['zoom_factor'] * 1.0
        for ind in self.bar.plg_mgr.plugins:
            #self.bar.plg_mgr.plugins[ind].resize()
            self.bar.plg_mgr.plugins[ind].set_icon()
        self.bar.plg_mgr.resize_spacer()
        self.bar.update_all()

    def set_icon_size(self, widget):
        self.config['icon_size'] = int(widget.get_value())
        
        # update zoom factor ( because icon_size changed .. )
        self.bar.zoom_size = self.config['icon_size'] * self.config['zoom_factor'] * 1.0
        
        # resize and update icon for all plugins
        for ind in self.bar.plg_mgr.plugins:
            self.bar.plg_mgr.plugins[ind].resize()
            self.bar.plg_mgr.plugins[ind].set_icon()
        self.bar.update_all()

    def set_hidden_size(self, widget):
        self.config['hidden_size'] = int(widget.get_value())
        self.bar.update_all()
        
    def set_timer(self, widget):
        self.config['timer'] = int(widget.get_value())
        
    def set_smooth_hide(self, widget):
        self.config['smooth_hide'] = int(widget.get_active())
        
    def set_fade_hidden(self, widget):
        self.config['hidden_size'] = int(widget.get_active())
        self.bar.update()


    # Color
    def set_bg_color(self, widget):
        color = widget.get_color()
        color = gtk.color_selection_palette_to_string([color])
        self.config['bg_color'] = color
        self.config['bg_color_rgb'] = core.hex2rgb(color)
        self.bar.draw_bg()
        self.bar.update()

    def set_bg_gradient_color(self, widget):
        color = widget.get_color()
        color = gtk.color_selection_palette_to_string([color])
        self.config['bg_gradient_color'] = color
        self.config['bg_gradient_color_rgb'] = core.hex2rgb(color)
        self.config['bg_gradient_alpha'] = widget.get_alpha()
        self.bar.draw_bg()
        self.bar.update()

    def set_bg_gradient(self, widget):
        self.config['bg_gradient'] = widget.get_active()
        self.bar.draw_bg()
        self.bar.update()

    def set_border_color(self, widget):
        color = widget.get_color()
        color = gtk.color_selection_palette_to_string([color])
        self.config['border_color'] = color
        self.config['border_color_rgb'] = core.hex2rgb(color)
        self.bar.draw_bg()
        self.bar.update()

    def set_border(self, widget):
        self.config['show_border'] = widget.get_active()
        self.bar.draw_bg()
        self.bar.update()

    def set_color_sub(self, widget):
        color = widget.get_color()
        color = gtk.color_selection_palette_to_string([color])
        self.config['bg_color_sub'] = color
        self.config['bg_color_sub_rgb'] = core.hex2rgb(color)

    def set_border_color_sub(self, widget):
        color = widget.get_color()
        color = gtk.color_selection_palette_to_string([color])
        self.config['border_color_sub'] = color
        self.config['border_color_sub_rgb'] = core.hex2rgb(color)

    def set_fixed_mode(self, widget):
        self.config['fixed_mode'] = widget.get_active()
        self.bar.plg_mgr.set_panel_mode()
        self.bar.update_all()

    def set_fixed_size(self, widget):
        self.config['fixed_size'] = widget.get_value()
        self.bar.update_all()

    def set_reserve_space(self, widget):
        self.config['reserve_space'] = widget.get_active()
        self.bar.update_strut(self.bar.win)
        
    def set_auto_raise(self, widget):
        self.config['auto_raise'] = widget.get_active()

    def set_keep_below(self, widget):
        self.config['keep_below'] = widget.get_active()
        self.bar.set_below_or_above()

    def set_fake_trans(self, widget):
        self.config['fake_trans'] = widget.get_active()
        self.bar.set_fake_trans()
        self.bar.update_all()

        if not self.bar.is_composited and not self.config['fake_trans']:
            self.opacity.set_sensitive(False)
        else:
            self.opacity.set_sensitive(True)

    def set_tooltips(self, widget):
        self.config['tooltips'] = widget.get_active()

        if self.bar.tooltip:
            self.bar.tooltip.destroy()
            self.bar.tooltip = None

        if self.config['tooltips']:
            self.bar.tooltip = ui.TooltipWindow(self.bar)

class Edit_Item:

    def __init__(self, conf, model, selection, from_drawer=False):

        self.conf = conf
        self.model = model
        self.selection = selection
        self.from_drawer = from_drawer

        if from_drawer:
            name = model.get_value(model.get_iter(selection), ID_NAME)
            command = model.get_value(model.get_iter(selection), ID_CMD)
            icon = model.get_value(model.get_iter(selection), ID_IMG)
        else:
            self.ind = model.get_value(model.get_iter(selection), ID_IND)
            launcher = conf.launcher[self.ind]
            name = launcher['name']
            command = launcher['cmd']
            icon = launcher['icon']

        is_plugin = False
        self.is_drawer = False
        self.plugin_conf = None

        if len(command) > 1 and command[0] == '@':
            is_plugin = True
            if command == '@drawer':
                self.is_drawer = True

        ## UI
        edit_box = gtk.VBox()
        edit_box.set_spacing(10)
        edit_box.set_border_width(5)       
        
        frame_settings = gtk.Frame()
        frame_settings.set_border_width(5)

        box_settings = gtk.HBox(False, 0)
        box_settings.set_border_width(5)
        box_settings.set_spacing(10)
        frame_settings.add(box_settings)

        label_name = gtk.Label(_("Name:"))
        self.text_name = gtk.Entry()
        self.text_name.set_text(name)

        self.text_command = gtk.Entry()
        command = command.replace("\\\"", "\"")
        self.text_command.set_text(command)

        if is_plugin:
            label_command = gtk.Label(_("Plugin:"))
            self.text_command.set_sensitive(False)
        else:
            label_command = gtk.Label(_("Command:"))

        self.button_command = gtk.Button("...")
        self.button_command.connect("clicked", self.button_command_clicked)

        #Icon options
        label_icon = gtk.Label(_("Icon:"))

        self.text_icon = gtk.Entry()
        self.text_icon.set_text(icon)
        self.text_icon.connect("changed", self.text_icon_change)

        self.button_icon = gtk.Button()
        self.button_icon.connect("clicked", self.button_icon_clicked)

        #Icon image in the frame:
        self.icon_image = gtk.Image()
        self.icon_image.set_size_request(80, 80)
        self.button_icon.add(self.icon_image)

        if os.path.isfile(icon) and '.' in icon:
            # Update property image:
            try:
                self.icon_image.set_from_pixbuf(core.pixbuf_from_file(icon,64,64))
            except:
                self.icon_image.set_from_stock(gtk.STOCK_MISSING_IMAGE, gtk.ICON_SIZE_DIALOG)
                
        elif core.ICON_THEME.has_icon(icon):
            pixbuf = core.ICON_THEME.load_icon(icon, 64, gtk.ICON_LOOKUP_USE_BUILTIN)
            self.icon_image.set_from_pixbuf(pixbuf)
        else:
            self.icon_image.set_from_stock(gtk.STOCK_MISSING_IMAGE, gtk.ICON_SIZE_DIALOG)


        #Table container inside frame
        table = gtk.Table(4,3)
        table.attach(label_name,0,1,0,1, gtk.SHRINK)
        table.attach(self.text_name,1,3,0,1)

        table.attach(label_command,0,1,1,2, gtk.SHRINK)
        table.attach(self.text_command,1,3,1,2)
        if not is_plugin:
            table.attach(self.button_command,3,4,1,2, gtk.SHRINK, gtk.SHRINK)

        table.attach(label_icon,0,1,2,3, gtk.SHRINK)
        table.attach(self.text_icon,1,3,2,3)

        box_settings.pack_start(self.button_icon, False, False)
        box_settings.pack_end(table, True, True)
        
        edit_box.pack_start(frame_settings, False, False)

        if is_plugin:
            if os.access("plugins/%s/config.py" % command[1:], os.F_OK|os.R_OK):
                try:
                    exec("import plugins.%s.config as plugin_conf" % command[1:])
                    
                    p_box = gtk.VBox()
                    p_box.set_spacing(10)
                    p_box.set_border_width(5)
                    edit_box.pack_start(p_box, True, True)
                    
                    self.plugin_conf = plugin_conf.config(p_box, self.conf, self.ind)

                except Exception, e:
                    traceback.print_exc()
                    self.plugin_conf = None

        ## Controls
        but_box = gtk.HButtonBox()
        but_box.set_spacing(10)
        but_box.set_layout(gtk.BUTTONBOX_END)
        
        button = gtk.Button(stock=gtk.STOCK_CANCEL)
        button.connect("clicked", self.close)
        but_box.add(button)

        button = gtk.Button(stock=gtk.STOCK_OK)
        button.connect("clicked", self.change_item)
        but_box.add(button)

        edit_box.pack_end(but_box, False, False) 
        edit_box.pack_end(gtk.HSeparator(), False, False) 
        
        self.conf.nbook.append_page(edit_box, None)
        self.conf.nbook.show_all()
        
        ## switch page
        self.conf.switch_page(from_drawer)

    def change_item(self, data):
        command = self.text_command.get_text()
        name = self.text_name.get_text()
        icon = self.text_icon.get_text()

        item = self.model.get_iter(self.selection)
        self.model.set_value(item, ID_NAME, name)

        if self.from_drawer:
            self.model.set_value(item, ID_CMD, command)
            self.model.set_value(item, ID_IMG, icon)
        else:
            launcher = self.conf.launcher[self.ind]
            launcher['name'] = name
            launcher['cmd'] = command
            launcher['icon'] = icon
            self.conf.plg_mgr.plugins[self.ind].set_icon(icon)
            self.conf.plg_mgr.plugins[self.ind].tooltip = name

        set_icon(icon, self.model, item)

        if self.plugin_conf:
            self.plugin_conf.save_change()
            del self.plugin_conf

        self.close()

    def close(self, widget=None, event=None):
        self.conf.switch_page(self.from_drawer)
        self.conf.nbook.remove_page(-1)

    def button_icon_clicked(self, widget):
        dialog = gtk.FileChooserDialog(_("Select image file.."),
                                        None,
                                        gtk.FILE_CHOOSER_ACTION_OPEN,
                                        (gtk.STOCK_CANCEL,
                                        gtk.RESPONSE_CANCEL,
                                        gtk.STOCK_OPEN,
                                        gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)

        filter = gtk.FileFilter()
        filter.set_name(_("Images"))
        filter.add_mime_type("image/png")
        filter.add_mime_type("image/jpeg")
        filter.add_mime_type("image/svg")
        filter.add_pattern("*.png")
        filter.add_pattern("*.jpg")
        filter.add_pattern("*.jpeg")
        filter.add_pattern("*.svg")
        dialog.add_filter(filter)
        filter = gtk.FileFilter()
        filter.set_name(_("All files"))
        filter.add_pattern("*")
        dialog.add_filter(filter)

        dialog.set_filename(self.text_icon.get_text())
        # Use directory specified in text field, fallback to icons dir
        url = os.path.dirname(self.text_icon.get_text())
        if os.path.exists(url):
            dialog.set_current_folder(url)
        else:
            dialog.set_current_folder('/usr/share/pixmaps/')

        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            #Set new icon information in place
            self.text_icon.set_text(dialog.get_filename())
        dialog.destroy()


    def text_icon_change(self, widget):
        #Replace icon to be displayed
        icon = self.text_icon.get_text()
        self.text_icon.modify_text(gtk.STATE_NORMAL, None)
        set_icon(icon, self.icon_image)

    def button_command_clicked(self, widget):
        dialog = gtk.FileChooserDialog(_("Select command.."),
                                        None,
                                        gtk.FILE_CHOOSER_ACTION_OPEN,
                                        (gtk.STOCK_CANCEL,
                                        gtk.RESPONSE_CANCEL,
                                        gtk.STOCK_OPEN,
                                        gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)

        filter = gtk.FileFilter()
        filter.set_name(_("All files"))
        filter.add_pattern("*")
        dialog.add_filter(filter)
        dialog.set_current_folder('/usr/share/applications')

        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            ## .desktop file selected ?
            filename = dialog.get_filename()
            if '.desktop' in filename:
                cmd, icon, name, category = Menu.info_desktop(filename)
                #~ print name, cmd, icon
                self.text_command.set_text(cmd)
                self.text_name.set_text(name)
                if icon:
                    icon = Menu.find_icon(icon)
                if not icon:
                    icon = 'images/def_icon.png'
                self.icon_image.set_from_pixbuf(core.pixbuf_from_file(icon, 64, 64))
                self.text_icon.set_text(icon)
            else:
                self.text_command.set_text(filename)
        dialog.destroy()

class View(gtk.TreeView):

    def __init__(self, conf):
        gtk.TreeView.__init__(self)
        self.conf = conf
        self.set_headers_visible(False)
        self.set_reorderable(True)
        self.get_selection().set_mode(gtk.SELECTION_SINGLE)

        self.model = gtk.ListStore(
            gtk.gdk.Pixbuf,         # icon pixbuf
            gobject.TYPE_STRING,    # name
            gobject.TYPE_STRING,    # ind
            )

        self.filtremodele = self.model.filter_new()
        self.set_model(self.model)

        cell_img = gtk.CellRendererPixbuf()
        col_img = gtk.TreeViewColumn(None, cell_img, pixbuf=ID_ICON)
        self.append_column(col_img)

        cell_text = gtk.CellRendererText()
        col_text = gtk.TreeViewColumn(None, cell_text, text=ID_NAME)
        self.append_column(col_text)

        cell_command = gtk.CellRendererText()
        col_command = gtk.TreeViewColumn(None, cell_command, text=ID_IND)
        col_command.set_visible(False)
        self.append_column(col_command)

    def remove_item(self):
        # remove item from configuration
        try:
            #self.view.grab_focus()
            pos = self.get_cursor()[0][0]
            if pos is None: # no selection
                return

            model = self.get_model()
            index = model.get_value(model.get_iter(pos), ID_IND)

            try:
                self.conf.plg_mgr.remove(index)
            except:
                pass

            model.remove(model.get_iter(pos))

            if pos < 0:
                pos = 0
            # Set the focus and cursor correctly
            self.set_cursor(pos);
            self.grab_focus()
            
        except TypeError:
            print( "> nothing to delete !?" )

    def add_launcher(self, name, icon, ind):

        model = self.get_model()
        item = model.append(None)
        set_icon(icon, model, item)
        model.set_value(item, ID_NAME, str(name))
        model.set_value(item, ID_IND, str(ind))

    def new_entry(self, index):

        self.grab_focus()
        model = self.get_model()
        position = None

        try:
            position = self.get_cursor()[0][0]
            try:
                iter = model.get_iter(position)
            except ValueError:
                print("> Empty list ?")
                iter = model.get_iter()

            item = model.insert_after(iter)
                
        except TypeError:
            #~ print "Error while adding new entry .."
            item = model.append(None)
            self.grab_focus()
        
        ## set default value for new entry
        model.set_value(item, ID_NAME, '')
        model.set_value(item, ID_IND, index)
        model.set_value(item, ID_ICON, core.pixbuf_from_file('images/no_fill.png', 32, 32))
        
        # add to list
        self.conf.launcher[index] = {'name':'', 'cmd':'', 'icon':''}
        
        ## Set focus to new entry
        if position is not None:
            path = model.get_path(model.get_iter(position+1))
        else:
            position = self.get_cursor()[0][0]
            path = model.get_path(model.get_iter(position))
        self.set_cursor(path)

    def row_deleted(self, treemodel, path):
        model = self.get_model()
        iter = model.get_iter_root()

        ind = 0
        self.conf.plg_mgr.index = []
        
        while (iter):
            index =  model.get_value(iter, ID_IND)
            iter = model.iter_next(iter)

            self.conf.plg_mgr.box.reorder_child(self.conf.plg_mgr.plugins[index], ind)
            self.conf.plg_mgr.index.append(index)
            ind += 1

    def row_inserted(self, treemodel, path, iter):
        pass

class PluginMenu:
    def __init__(self, callback):

        self.callback = callback
        self.menu = gtk.Menu()

        self.list_plugins()
        plugins_sort = []

        for plugin in self._list:
            plugins_sort.append(plugin)

        plugins_sort.sort()

        for plugin in plugins_sort:
            item = self.append_menu_item(self.menu, 
                                         self._list[plugin]['Name'], 
                                         self._list[plugin]['Icon'])
            item.connect("activate", self.callback, plugin)
            item.show()

    def create_menu_item(self, label, icon_name, comment):
        
        item = gtk.ImageMenuItem(label)
        icon_pixbuf = core.get_pixbuf_icon(icon_name)
        item.set_image(gtk.image_new_from_pixbuf(icon_pixbuf))
        return item

    def append_menu_item(self, menu, label, icon_name, comment=None):
        
        item = self.create_menu_item(label, icon_name, comment)
        menu.append(item)
        return item

    def list_plugins(self):
        
        self._list = {}
        for p in os.listdir('plugins'):
            if '.desktop' in p:
                plg_name = p[:-8]
                self._list[plg_name] = {}
                try:     
                    f = open('plugins/'+p, 'r')
                    for line in f:
                        ## empty or comment ..
                        if line == '\n' or line[0] == '#':
                            continue

                        line = line.strip('\n')
                        line = line.strip()
                        
                        tmp = line.split('=', 1)
                        key = tmp[0].strip()
                        keyval = tmp[1].strip()

                        self._list[plg_name][key] = keyval
                    f.close()
                except:
                    print 'Error while parsing config file ..'
