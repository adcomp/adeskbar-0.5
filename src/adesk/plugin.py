# -*- coding: utf-8 -*-

import gtk
import cairo 

import adesk.core as Core

import ui

# Only for debugging : False / True
DEBUG = 0

ICON_THEME = Core.ICON_THEME	
		
class PluginContainer(gtk.EventBox):
    """PluginContainer is a gtk EventBox."""
    def __init__(self, app, settings):
        gtk.EventBox.__init__(self)
        self.set_border_width(0)
        self.set_visible_window(False)
        self.app = app
        self.cfg = app.cfg
        self.settings = settings
        self.index = None
        self.is_visible = False

        self.can_zoom = False
        self.can_show_icon = True

        self.tooltip = ''
        self.has_tooltip = True

    def draw(self, cr):
        pass

    def resize(self):
        pass
        
    def restart(self):
        pass

    def stop(self):
        pass
        
    def onClick(self, widget, event):
        pass

    def on_init(self):
        pass

    def set_icon(self, icon=None):
        pass

class Plugin(gtk.EventBox):
    """Plugin is a gtk EventBox with a cairo surface painted over it."""
    __gsignals__ = {'expose-event' : 'override',}
    
    def __init__(self, app, settings):
        gtk.EventBox.__init__(self)
        self.set_visible_window(False)
        self.app = app
        self.cfg = app.cfg
        self.settings = settings
        self.index = None

        self.pixbuf = None
        self.pixbuf_zoom = None
        self.current_icon = None

        self.can_zoom = True
        self.can_show_icon = True

        self.focus = False
        self.is_pressed = False
        self.is_visible = False
        self.tooltip = ''
        self.has_tooltip = True

    def do_expose_event(self, event):
        a = self.get_allocation()
        x, y = a.x, a.y

        if self.focus and self.can_zoom and not self.is_visible:
            offset = int( (self.app.zoom_size - self.cfg['icon_size'])/2 )
            w, h = self.app.zoom_size, self.app.zoom_size
            if self.cfg['position']=='top':
                x = x - offset
            elif self.cfg['position']=='bottom':
                x = x - offset
                y = y - 2*offset
            elif self.cfg['position']=='right':
                x = x - 2*offset
                y = y - offset
            elif self.cfg['position']=='left':
                y = y - offset
        else:
            w, h = a.width, a.height
                
        ctx = self.window.cairo_create()
        
        if self.is_visible or self.cfg['icons_effects']==1:
            ctx.rectangle(x-2, y-2, w+4, h+4)
        else:
            ctx.rectangle(x-1, y-1, w+2, h+2)
        ctx.clip()

        if DEBUG:
            ctx.set_source_rgb(1, 0.2, 0.2)
            ctx.set_line_width(1)
            ctx.rectangle(a.x, a.y, a.width, a.height)
            ctx.stroke()

        if self.can_show_icon:
            
            if self.is_visible:
                self.draw_frame(ctx, a.x, a.y)
            
            if self.focus and self.can_zoom and not self.is_visible and self.is_pressed:
                self.draw_frame(ctx, a.x, a.y)
                ctx.set_source_pixbuf(self.pixbuf, a.x, a.y)
                
            elif self.focus and not self.cfg['icons_effects']==0 and self.can_zoom and not self.is_visible:
                if self.cfg['icons_effects']==1:
                    self.draw_frame(ctx, a.x, a.y)
                    ctx.set_source_pixbuf(self.pixbuf, a.x, a.y)
                elif self.cfg['icons_effects']==2:
                    pixbuf = self.pixbuf.copy()
                    self.pixbuf.saturate_and_pixelate(pixbuf, 2, False)
                    ctx.set_source_pixbuf(pixbuf, a.x, a.y)
                elif self.cfg['icons_effects']==3:
                    ctx.set_source_pixbuf(self.pixbuf_zoom, x, y)
            else:
                ctx.set_source_pixbuf(self.pixbuf, a.x, a.y)

            ctx.paint()

        try:
            self.get_child().send_expose(event)
        except:
            # no child ?
            pass

        return False

    def draw_frame(self, ctx, x, y):
        if self.is_pressed:
            pixbuf = self.app.pixbuf_pressed.scale_simple(self.cfg['icon_size']+4, self.cfg['icon_size']+4, gtk.gdk.INTERP_BILINEAR)
        else:
            pixbuf = self.app.pixbuf_glow.scale_simple(self.cfg['icon_size']+4, self.cfg['icon_size']+4, gtk.gdk.INTERP_BILINEAR)
        ctx.set_source_pixbuf(pixbuf, x-2, y-2)
        ctx.paint()
        return

    def set_tooltip(self, tooltip):
        self.tooltip = tooltip
        self.app.tooltip.set_tooltip(tooltip)
        self.app.tooltip.reposition(self)

    def get_tooltip(self, tooltip):
        return self.tooltip

    def set_icon(self, path_icon=None, is_separator=False):
        #~ print 'set_icon :', path_icon
        if path_icon == '':
            path_icon = 'images/def_icon.png'

        if not path_icon:
            path_icon = self.current_icon

        w = h = self.cfg['icon_size']
        self.pixbuf = None

        if is_separator:
            if self.cfg['position'] == 'bottom' or self.cfg['position'] == 'top':
                w = w // 4
            else:
                h = h // 4

        if not path_icon:
            self.pixbuf = Core.pixbuf_from_file('images/def_icon.png', w, h)
            self.pixbuf_zoom = Core.pixbuf_from_file('images/def_icon.png', self.app.zoom_size, self.app.zoom_size)
            self.current_icon = 'images/def_icon.png'
            
        ## real path .. load from file
        elif path_icon[0] == '/' or ( len(path_icon) > 7 and path_icon[:7] == 'images/'):
            self.pixbuf = Core.pixbuf_from_file(path_icon, w, h)
            self.pixbuf_zoom = Core.pixbuf_from_file(path_icon, self.app.zoom_size, self.app.zoom_size)
            self.current_icon = path_icon
            
        ## load from icon theme
        elif ICON_THEME.has_icon(path_icon):
            
            ## FIX : gio.Error: Error opening file: No such file or directory
            try:
                self.pixbuf = ICON_THEME.load_icon(path_icon, self.cfg['icon_size'], gtk.ICON_LOOKUP_USE_BUILTIN)
                self.pixbuf = self.pixbuf.scale_simple(self.cfg['icon_size'], self.cfg['icon_size'], gtk.gdk.INTERP_BILINEAR)
                #~ self.pixbuf_zoom = ICON_THEME.load_icon(path_icon, int(self.app.zoom_size), gtk.ICON_LOOKUP_USE_BUILTIN)
                self.pixbuf_zoom = self.pixbuf.scale_simple(int(self.app.zoom_size), int(self.app.zoom_size), gtk.gdk.INTERP_BILINEAR)
                self.current_icon = path_icon
            except:
                pass


        ## check if pixbuf is ok
        if not self.pixbuf:
            self.pixbuf = Core.pixbuf_from_file('images/def_icon.png', w, h)
            self.pixbuf_zoom = Core.pixbuf_from_file('images/def_icon.png', self.app.zoom_size, self.app.zoom_size)
            self.current_icon = 'images/def_icon.png'

        if self.app.init_flag:
            self.app.update()

    def draw(self, cr):
        pass

    def resize(self):
        pass
        
    def restart(self):
        pass

    def stop(self):
        pass

    def onClick(self, widget, event):
        pass

    def on_init(self):
        pass

    def call_bar_update(self):
        self.app.update()
