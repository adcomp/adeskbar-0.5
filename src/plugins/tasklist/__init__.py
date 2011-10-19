# -*- coding: utf-8 -*-

import os
import time
import gtk
import pango

import adesk.plugin as Plg
import adesk.core as Core
import adesk.draw

try:
    import wnck
except:
    Core.logINFO('Plugin "tasklist" need python-wnck')
    Core.logINFO(' -- debian/ubuntu : "sudo apt-get install python-wnck"')

def_settings = { 
    'desktop_color':'#EEEEEE', 'desktop_font':'Sans Bold 12',
    'show_desk_pos':0, 'show_desk_name':0, 'show_all_win':1,
    'active_color':'#7F7F7F', 'padding':10, 'opacity':32767
    }

class Plugin(Plg.PluginContainer):
    def __init__(self, bar, settings):
        Plg.PluginContainer.__init__(self, bar, settings)
        self.can_zoom = False
        self.can_show_icon = False
        self.bar = bar

        ## FIXME!!
        for key in def_settings:
            if not key in self.settings:
                self.settings[key] = def_settings[key]

        self.button_focus = None
        self.active_window = None

        gtk.gdk.error_trap_push() # silently ignore x errors 
        
        self.screen_signals = []
        self.pixbufs = {}
        self.ui_tasklist()
        
        # Fix active window
        self.window_active_changed(self.screen, None)

    def init_screen_callback(self, screen):
        self.screen_signals.append(screen.connect('window-opened', self.window_opened))
        self.screen_signals.append(screen.connect('window-closed', self.window_closed))
        self.screen_signals.append(screen.connect('active-window-changed', self.window_active_changed))
        # workspace callback
        self.screen_signals.append(screen.connect('workspace-created', self.workspace_add))
        self.screen_signals.append(screen.connect('workspace-destroyed', self.workspace_remove))

    def ui_tasklist(self):
        self.workspaces = {}
        self.windows = {}
        self.windows_needing_attention = {}

        self.settings['padding'] = int(self.settings['padding'])
        self.settings['opacity'] = int(self.settings['opacity'])
        
        self.opacity = self.settings['opacity'] / 65535.0
        self.active_color = Core.hex2rgb(self.settings['active_color'])

        if self.bar.cfg['position'] == 'top' or self.bar.cfg['position'] == 'bottom':
            self.container = gtk.HBox(False, 0)
            self.mainbox = gtk.HBox(False, 0)
        else:
            self.container = gtk.VBox(False, 0)
            self.mainbox = gtk.VBox(False, 0)
            
        self.mainbox.set_spacing(4)
        self.mainbox.pack_start(self.container, True)
        
        self.container.set_border_width(0)
        
        if int(self.settings['show_all_win']):
            self.container.set_spacing(4)
        else:
            self.container.set_spacing(0)

        wnck.set_client_type(wnck.CLIENT_TYPE_PAGER)
        screen = wnck.screen_get_default()
        self.screen = screen
        screen.force_update()
        windows = screen.get_windows()

        self.scr_width = screen.get_width()
        self.scr_height = screen.get_height()
        ws = screen.get_active_workspace()
        
        self.is_virtual = ws.is_virtual()
        self.num_workspaces = screen.get_workspace_count()                
        self.use_viewports = self.is_virtual and self.num_workspaces == 1
        
        if self.use_viewports:
            # the compiz path: 1 workspace and it is virtual
            ws_width = ws.get_width()
            ws_height = ws.get_height()        
            self.num_viewports = ws_width // self.scr_width
            
            for i in range(0, self.num_viewports):
                self.workspace_add(screen, i)
        else:
            for i in range(0, screen.get_workspace_count()):
                self.workspace_add(screen, i)

        for window in windows:
            self.window_opened(screen, window)

        self.add(self.mainbox)
        self.init_screen_callback(screen)
        self.create_menu()
        
        if int(self.settings['show_desk_pos']):
            #~ screen.connect("active_workspace_changed", self.workspace_changed)
            self.active_workspace = gtk.Label()
            self.active_workspace.modify_font(pango.FontDescription(self.settings['desktop_font']))
            self.active_workspace.set_use_markup(True)
            #~ self.active_workspace.set_alignment(0.5,0.5)
            self.mainbox.pack_end(self.active_workspace, False, False)
            
            if self.bar.cfg['position'] == 'top' or self.bar.cfg['position'] == 'bottom':
                self.active_workspace.set_size_request(-1, self.bar.cfg['icon_size'])
            else:
                self.active_workspace.set_size_request(self.bar.cfg['icon_size'], -1)
            self.active_workspace.show()

        if int(self.settings['show_desk_pos']) or not int(self.settings['show_all_win']):
            if self.use_viewports:
                self.screen_signals.append(screen.connect('viewports-changed', self.workspace_changed))
            else:
                self.screen_signals.append(screen.connect("active_workspace_changed", self.workspace_changed))

        self.show_all()

    def on_init(self):
        self.workspace_changed(self.screen, None)

    def restart(self):
        for signal in self.screen_signals:
            self.screen.disconnect(signal)
        self.screen_signals = []
        
        self.container.destroy()
        self.mainbox.destroy()
        
        ## set_child_packing(child, expand, fill, padding, pack_type)
        if int(self.settings['expand']):
            self.bar.plg_mgr.box.set_child_packing(self, True, True, 0, gtk.PACK_START)
        else:
            self.bar.plg_mgr.box.set_child_packing(self, False, False, 0, gtk.PACK_START)
        
        self.ui_tasklist()
        self.workspace_changed(self.screen, None)

    def _get_num_desktops(self):
        if self.use_viewports:
            return self.num_viewports
        else:
            return self.num_workspaces

    
    def _get_active_desktop(self):
        ws = self.screen.get_active_workspace()
        if self.use_viewports:           
            return ws.get_viewport_x() // self.scr_width
        else:
            return ws.get_number()
    
    def get_desktop_num_for_win(self, win):
        if self.use_viewports:           
            ws = self.screen.get_active_workspace()
            x = ws.get_viewport_x()
            
            offset = x // self.scr_width            
            x, y, width, height = win.get_geometry()
            num = (x + offset * self.scr_width) // self.scr_width
            if num < 0 or num >= self._get_num_desktops():
                return 0
            return num
        else:
            ws = win.get_workspace()
            if not ws:
                # None for sticky windows, docks, desktop, etc.
                return self.screen.get_active_workspace().get_number()
            return ws.get_number()

    def switch_to_desktop(self, number):
        if self.use_viewports:
            # move to correct desktop
            x = self.scr_width * number
            self.screen.move_viewport(x, 0)
            
        else:
            timestamp = int(time.time())
            self.screen.get_workspace(number).activate(timestamp)

    def showdesktop(self, widget, event):
        showing_windows = not self.screen.get_showing_desktop()
        self.screen.toggle_showing_desktop(showing_windows)

    def window_get_icon(self, window):
        size = self.bar.cfg['icon_size']
        app = window.get_application()
        
        if app is not None:
            if Core.ICON_THEME.has_icon(app.get_icon_name()):
                pbuf = Core.ICON_THEME.load_icon(app.get_icon_name(), size, gtk.ICON_LOOKUP_USE_BUILTIN)
            else:
                pbuf = window.get_icon().copy()
        else:
            pbuf = window.get_icon().copy()
        
        self.pixbufs[window] = pbuf.scale_simple(size, size, gtk.gdk.INTERP_BILINEAR)

    def workspace_add(self, screen, space):
        ws_event =  gtk.EventBox()
        ws_event.set_visible_window(False)
        ws_event.connect("button-press-event", self.go_to_workspace, space)
        ws_event.connect('enter-notify-event', self.workspace_hover)
        ws_event.connect('leave-notify-event', self.workspace_unhover)

        if self.bar.cfg['position'] == 'top' or self.bar.cfg['position'] == 'bottom':
            workspace = gtk.HBox(False, 0)
        else:
            workspace = gtk.VBox(False, 0)
        workspace.set_border_width(0)
        workspace.set_spacing(8)

        separator = None

        if len(self.workspaces) > 0 and int(self.settings['show_all_win']):
            separator = gtk.Image()
            if self.bar.cfg['position'] == 'top' or self.bar.cfg['position'] == 'bottom':
                img_path = 'images/plugins/tasklist/separator_h.png'
            else:
                img_path = 'images/plugins/tasklist/separator_v.png'
            pbuf = Core.pixbuf_from_file(img_path)
            separator.set_from_pixbuf(pbuf)
            self.container.pack_start(separator, False, False)
            separator.show()

        ws_event.add(workspace)
        self.workspaces[space] = [workspace, separator, ws_event]

        self.container.pack_start(ws_event, True, True)
        ws_event.show()
        workspace.show()

    def go_to_workspace(self, widget, event, space):
        if event.button==1: # left click
            self.switch_to_desktop(space)
        return False

    def workspace_hover(self, widget, event):
        self.bar.can_hide = False
 
    def workspace_unhover(self, widget, event):
        self.bar.can_hide = True
        
    def workspace_remove(self, screen, space):
        self.workspaces[space][0].destroy()
        if self.workspaces[space][1]:
            self.workspaces[space][1].destroy()
        del self.workspaces[space]

    def icon_clicked_cb(self, widget, event):
        window = wnck.window_get(int(widget.get_name()))
        wsp = self.get_desktop_num_for_win(window)
        active_wsp = self._get_active_desktop()
        active_win = self.screen.get_active_window()
        
        if event.button == 1: # left click

            if not wsp == active_wsp:
                self.switch_to_desktop(wsp)
                window.activate(event.get_time())
            elif window.is_minimized():
                window.unminimize(event.get_time())
                window.activate(event.get_time())
            elif window == active_win:
                window.minimize()
            else:
                window.activate(event.get_time())

        elif event.button==3: # right click
            self.button_focus = window
            self.popupMenu.popup(None, None, None, event.button, event.time)
        
        ## need this to avoid call to Bar menu
        return True

    def icon_hover_cb(self, widget, event):
        window = wnck.window_get(int(widget.get_name()))
        
        widget.pixbuf = widget.pixbuf_origin.copy()
        widget.pixbuf.saturate_and_pixelate(widget.pixbuf, 2, False)

        if self.cfg['tooltips']:
            self.bar.tooltip.run(widget)
            
        ### FIXME !!
        self.bar.can_hide = False
        self.bar.update()
        return True

    def icon_unhover_cb(self, widget, event):
        window = wnck.window_get(int(widget.get_name()))
        widget.pixbuf = widget.pixbuf_origin.copy()
        if window.is_minimized():
            widget.pixbuf.saturate_and_pixelate(widget.pixbuf, 0.3, False)
        
        ### FIXME !!
        self.bar.can_hide = True
        self.bar.update()
        return True

    def window_add(self, window):
        if window.is_skip_tasklist():
            return
        
        self.window_get_icon(window)

        def window_add(window, workspace):

            button = CairoWindowButton(self)
            button.tooltip = window.get_name()
            button.set_name(str(window.get_xid()))
            button.pixbuf_origin = self.pixbufs[window]
            button.pixbuf = button.pixbuf_origin.copy()

            size = self.bar.cfg['icon_size']
            if self.bar.cfg['position']=='bottom' or self.bar.cfg['position']=='top':
                button.set_size_request(size + self.settings['padding'], size)
            else:
                button.set_size_request(size, size + self.settings['padding'])

            button.connect('button_press_event', self.icon_clicked_cb)
            button.connect('enter-notify-event', self.icon_hover_cb)
            button.connect('leave-notify-event', self.icon_unhover_cb)
            button.connect('scroll-event', self.on_scroll_event)
            self.workspaces[workspace][0].pack_start(button, False, False)

            button.show()
            return button

        workspace = window.get_workspace()
        desktop_num = self.get_desktop_num_for_win(window)

        buttons = []

        if workspace:
            buttons.append(window_add(window, desktop_num))
        else:
            for workspace in self.workspaces: buttons.append(window_add(window, desktop_num))

        self.windows[window] = [buttons, desktop_num]

    def window_remove(self, window):
        try:
            wn = self.windows[window]
            for button in wn[0]:
                button.destroy()
        except: pass

    def window_workspace_changed(self, window):
        self.window_remove(window)
        self.window_add(window)

    def window_name_changed(self, window):
        buttons = self.windows[window][0]
        for button in buttons:
            button.set_tooltip_text(window.get_name())

    def pixbuf_tint(self, pixbuf, fraction):
        w = pixbuf.get_width()
        h = pixbuf.get_height()
        blank = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, w, h)
        blank.fill(0)

        # dest, dest_x, dest_y, dest_width, dest_height, offset_x, offset_y, scale_x, scale_y, interp_type, overall_alpha
        pixbuf.composite(blank, 0, 0, w, h, 0, 0, 1, 1, gtk.gdk.INTERP_NEAREST, int(fraction * 255.0))
        return blank

    def window_icon_changed(self, window):
        pos = -1
        if window.get_workspace(): # not sticky
            widget = self.windows[window][0][0]
            parent = widget.get_parent()
            if parent:
                pos = parent.get_children().index(widget)

        self.window_remove(window)
        self.window_add(window)

        if pos != -1:
            widget = self.windows[window][0][0]
            widget.get_parent().reorder_child(widget, pos)

    def window_opened(self, screen, window):
        if window.is_skip_tasklist():
            return
        window.connect('workspace-changed', self.window_workspace_changed)
        window.connect('name-changed', self.window_name_changed)
        window.connect('icon-changed', self.window_icon_changed)
        self.window_add(window)

    def window_closed(self, screen, window):
        if window in self.windows:
            self.window_remove(window)
            del self.windows[window]

    def window_active_changed(self, screen, previous):
        ## reset last active flag
        if self.active_window is not None:
            if self.active_window in self.windows:
                for button in self.windows[self.active_window][0]:
                    button.is_active = False

        self.active_window = screen.get_active_window()
        
        if self.active_window in self.windows:
            for button in self.windows[self.active_window][0]:
                button.is_active = True

        for win in self.windows:
            if win.is_minimized():
                for button in self.windows[win][0]:
                    button.pixbuf = button.pixbuf_origin.copy()
                    button.pixbuf.saturate_and_pixelate(button.pixbuf, 0.3, False)
            else:
                for button in self.windows[win][0]:
                    button.pixbuf = button.pixbuf_origin.copy()

        # Fix!! need to refresh ?
        self.bar.update()

    def on_scroll_event(self, widget, event):
        window = wnck.window_get(int(widget.get_name()))
        
        if event.direction == gtk.gdk.SCROLL_DOWN:
                if window.is_minimized():
                    window.unminimize(event.get_time())
                else:
                    window.minimize()
        elif event.direction == gtk.gdk.SCROLL_UP:
            if window.is_maximized():
                window.unmaximize()
            else:
                window.maximize()

    def create_menu(self):
        self.popupMenu = gtk.Menu()
        
        menuPopup = gtk.ImageMenuItem(gtk.STOCK_ZOOM_100)
        menuPopup.get_children()[0].set_label('Maximize')
        menuPopup.connect("activate", self.maximize_active_window)
        self.popupMenu.add(menuPopup)
        
        menuPopup = gtk.ImageMenuItem(gtk.STOCK_UNDO)
        menuPopup.get_children()[0].set_label('MInimize')
        menuPopup.connect("activate", self.minimize_active_window)
        self.popupMenu.add(menuPopup)
        
        menuPopup = gtk.ImageMenuItem(gtk.STOCK_CLOSE)
        menuPopup.connect("activate", self.close_active_window)
        self.popupMenu.add(menuPopup)
        
        self.popupMenu.show_all()
        
    def close_active_window(self, widget):
        timestamp = int(time.time())
        self.button_focus.close(timestamp)

    def maximize_active_window(self, widget):
        if self.button_focus.is_maximized():
            self.button_focus.unmaximize()
        else:
            self.button_focus.maximize()
        
    def minimize_active_window(self, widget):
        if self.button_focus.is_minimized():
            timestamp = int(time.time())
            self.button_focus.unminimize(timestamp)
        else:
            self.button_focus.minimize()
        
    def workspace_changed(self, screen, space=None):
        active_wp = screen.get_active_workspace()

        if int(self.settings['show_desk_pos']):
            if int(self.settings['show_desk_name']) and not self.use_viewports:
                active_wp = screen.get_active_workspace()
                label = active_wp.get_name()
            else:
                label = self._get_active_desktop() + 1
                label = str(label)
            
            label = '<span color="%s"> %s </span>' % (self.settings['desktop_color'], label)
            self.active_workspace.set_markup(label)
        
        if not int(self.settings['show_all_win']):
            for wp in self.workspaces:
                self.workspaces[wp][2].hide()
            self.workspaces[self._get_active_desktop()][2].show()
            
        self.bar.update()

    def resize(self):
        if self.bar.cfg['position']=='top' or self.bar.cfg['position']=='bottom':
            self.set_size_request(-1, self.cfg['icon_size'])
        else:
            self.set_size_request(self.cfg['icon_size'], -1)

        ## FIXME!!
        if self.bar.cfg['position'] == 'top' or self.bar.cfg['position'] == 'bottom':
            self.container.set_orientation(gtk.ORIENTATION_HORIZONTAL)
            self.mainbox.set_orientation(gtk.ORIENTATION_HORIZONTAL)
            for ws in self.workspaces:
                self.workspaces[ws][0].set_orientation(gtk.ORIENTATION_HORIZONTAL)
                
            (but_width, but_height) = (self.cfg['icon_size'] + self.settings['padding'],
                                       self.cfg['icon_size'])
        else:
            self.container.set_orientation(gtk.ORIENTATION_VERTICAL)
            self.mainbox.set_orientation(gtk.ORIENTATION_VERTICAL)
            for ws in self.workspaces:
                self.workspaces[ws][0].set_orientation(gtk.ORIENTATION_VERTICAL)
                
            (but_width, but_height) = (self.cfg['icon_size'],
                                       self.cfg['icon_size'] + self.settings['padding'])

        self.container.set_border_width(0)
        
        for win in self.windows:
            self.window_get_icon(win)
            for button in self.windows[win][0]:
                button.set_size_request(but_width, but_height)
                button.pixbuf_origin = self.pixbufs[win].copy()
                button.pixbuf = button.pixbuf_origin

class CairoWindowButton(gtk.EventBox):
    """CairoButton is a gtk button with a cairo surface painted over it."""
    
    __gsignals__ = {'expose-event' : 'override',}
    
    def __init__(self, plugin):
        gtk.EventBox.__init__(self)
        self.set_border_width(0)
        self.set_visible_window(False)
        self.is_active = False
        
        self.plg = plugin
        self.cfg = plugin.bar.cfg

        ## FIXME! quick hack for tooltip
        self.tooltip = ''
        self.is_visible = False
        
        self.pixbuf_origin = None
        self.pixbuf = None
        self.pixbuf_over = Core.pixbuf_from_file('./images/plugins/tasklist/button.png')

    def do_expose_event(self, event):
        ctx = self.window.cairo_create()
        a = self.get_allocation()
        
        if self.is_active:
            self.draw_overlay(ctx, a.x-1, a.y-1, a.width+2, a.height+2)
        else:
            mx , my = self.get_pointer()
            if mx >= 0 and mx < a.width and my >= 0 and my < a.height:
                self.draw_overlay(ctx, a.x-1, a.y-1, a.width+2, a.height+2)
        
        self.draw_icon(ctx, a.x-1, a.y-1, a.width+2, a.height+2)

    def draw_icon(self, ctx, x, y, w, h):
        if not self.pixbuf == None:
            x1 = x + int((w - self.cfg['icon_size'])//2.0)
            y1 = y + int((h - self.cfg['icon_size'])//2.0)
            ctx.set_source_pixbuf(self.pixbuf, x1, y1)
            ctx.paint()

    def draw_overlay(self, ctx, x, y, w, h):
        ## bg color 
        r = self.plg.active_color[0]
        g = self.plg.active_color[1]
        b = self.plg.active_color[2]
        opacity = self.plg.opacity
        
        ctx.set_source_rgba(r, g, b, opacity)                
        adesk.draw.rounded_rect(ctx, [x+1, y+1, w-2, h-2], 8, 'bottom', fill=True)
        pixbuf = self.pixbuf_over.scale_simple(w, h, gtk.gdk.INTERP_BILINEAR)
        ctx.set_source_pixbuf(pixbuf, x, y)
        ctx.paint()
