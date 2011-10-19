# adesk Systray plugin

# INFO:
# - Uses some code from pyPanel

import adesk.plugin as Plg
import adesk.core as Core
import adesk.ui as UI

import gtk
import gobject
import sys
from gtk import gdk
import cairo
import string

try:
    from Xlib import X, display, error, Xatom, Xutil
    import Xlib.protocol.event
    from Xlib.protocol import request, rq
except:
    Core.logINFO('Plugin "systray" need python-xlib')
    Core.logINFO(' -- debian/ubuntu : "sudo apt-get install python-xlib"')

SIZE = 24
OFFSET = 2

BORDER = 2

SPACE = 2

HIGH = 1
ICONSIZE = 24
CUSTOM_Y = 2

class Plugin(Plg.PluginContainer):
    def __init__(self, bar, settings):
        Plg.PluginContainer.__init__(self, bar, settings)
        self.can_zoom = False
        self.can_show_icon = False
        self.settings = settings
        self.bar = bar
        self.cfg = bar.cfg

        global BG_COLOR
        BG_COLOR = bar.cfg['background_color']

        self.systray = SysTray(display, error, self, bar)

    def destroy(self):
        Core.logINFO("attempt to cleanly close, in such a way that the icons do not get an X window error")
        self.systray.cleanup()

    def trayWorks(self,widget):
        #~ self.align.add(widget)
        self.add(widget)

    def resize(self):
        if self.bar.cfg['position']=='top' or self.bar.cfg['position']=='bottom':
            self.set_size_request(-1, self.cfg['icon_size'])
        else:
            self.set_size_request(self.cfg['icon_size'], -1)

class Obj(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

class SysTray(gtk.Widget):

    def __init__(self, display, error, plugin, bar):
        gtk.Widget.__init__(self)

        # Define widget value and set to default
        self.curr_x = 1 
        self.curr_y = 1

        # references to Xlib
        self.dsp = display.Display()      
        self.scr = self.dsp.screen()
        self.root = self.scr.root
        self.error = error.CatchError()

        self.plugin = plugin
        self.bar = bar

        # Is the Xwindow realized yet? if not, can cause problems with certain functions
        self.realized= 0
                                         
        ourmask = (X.ButtonPressMask|X.ButtonReleaseMask|X.ExposureMask)

        # Create an X window to hold icons
        self.wind = self.root.create_window(0, 0, 1, 10,
                0, self.scr.root_depth, window_class=X.InputOutput,
                visual=X.CopyFromParent, colormap=X.CopyFromParent,
                event_mask=ourmask)

        self.wind.change_property(self.dsp.intern_atom("_NET_WM_DESKTOP"), Xatom.CARDINAL, 32, [0xffffffffL])

        # set background colour to match the screenlet background
        col = hex(string.atoi(BG_COLOR[1:],16))
        self.intColour = int(col,16)
        self.wind.change_attributes(background_pixel=self.intColour) 

        # Create an empty Object, this will contain all the data on icons
        # to be added, and all currently managed
        self.tray = Obj(id="tray", tasks={}, order=[],
                    first=0, last=0, window=self.wind)

        # Create a non-visible window to be the selection owner
        self._OPCODE = self.dsp.intern_atom("_NET_SYSTEM_TRAY_OPCODE")
        self.manager = self.dsp.intern_atom("MANAGER")
        self.selection = self.dsp.intern_atom(
            "_NET_SYSTEM_TRAY_S%d" % self.dsp.get_default_screen())
            
        self.selowin = self.scr.root.create_window(-1,
                                  -1, 1, 1, 0, self.scr.root_depth)
        owner = self.dsp.get_selection_owner(self.selection)

        if owner != X.NONE:
            Core.logINFO("Another System Tray is already running")
            print "Another System Tray is already running"

        else:
            self.selowin.set_selection_owner(self.selection, X.CurrentTime)
            self.tr__sendEvent(self.root, self.manager,
                  [X.CurrentTime, self.selection, self.selowin.id],
                  (X.StructureNotifyMask))

            self.tr__setProps(self.dsp, self.wind)
            # Set a list of Properties that we'll need

            self.dsp.flush()
            # Show the window and flush the display
            plugin.trayWorks(self)

    def do_realize(self):
        self.set_flags(gtk.REALIZED)


        #Create a gtk.gdk.Window wrapper around topWindow, child of the screenlets gtk.gdk.Window
        #   -allows masking of the icons through gdk
        #   -also imposes the screenlets window properties on the icons, i.e. no drop shadow, no window decoration
        
        #~ self.realIcons = gtk.gdk.window_foreign_new(self.wind.id)
        #~ self.realIcons.reparent(self.plugin.window,0,0)

        #Greate a gtk.gdk.Window to hold images of the icons.
        #This is shown on the screenlet while the real icons are moved out of the screenlet's
        #clip area for unmaksing.  This prevents the icons from flickering as their
        #masks are updated.
        
        #~ self.fakeIcons = gtk.gdk.Window(self.plugin.window,96,48,gtk.gdk.WINDOW_CHILD,0,gtk.gdk.INPUT_OUTPUT)
        #~ self.fakeIcons.move(0,0)
        #~ self.fakeIcons.lower()


        self.window = gdk.window_foreign_new(self.wind.id)
        self.window.reparent(self.plugin.window, 0, 0)

        # Take the system manager window (not selection owner!)
        # And make it the gdk.window of the custom widget.
        
        
        self.window.set_user_data(self)
        #~ self.style.attach(self.window)
        # Set it up as a custom widget and tell it what style (theme) to use

        #~ self.style.set_background(self.window, gtk.STATE_NORMAL)
        self.window.move_resize(*self.allocation)
        # Tell it to use the background colour as background colour...
        # Im sure theres a reason i need to tell it that ;)

        self.tr__updatePanel(self.root, self.wind)
        # First render. Grab all the icons we know about, tell them where to
        # draw, and call a resize if necessary (likely, the first time around)

        gobject.io_add_watch(self.dsp.fileno(), gobject.IO_IN | gobject.IO_PRI,
                             self.tr__testTiming)

        self.redraw()

        self.realized= 1
        # and now we can safely render alpha :D

    def do_unrealize(self):
        # The do_unrealized method is responsible for freeing the GDK resources
        # Lol.
        return 1

    def do_size_request(self, requisition):
        # Widget is bieng asked what size it would like to be.
        requisition.width = self.curr_x
        requisition.height = self.curr_y

    def do_size_allocate(self, allocation):
        # The do_size_allocate is called by when the actual size is known
        # and the widget is told how much space could actually be allocated
        self.allocation = allocation

        # If we're realized, move and resize the window to the
        # requested coordinates/positions
        if self.flags() & gtk.REALIZED:
            self.window.move_resize(*allocation)

    def tr__taskDelete(self, tid):
    #--------------------------------
        """ Delete the given task ID if it's in the tray/task list """
        if tid in self.tray.tasks:
            del self.tray.tasks[tid]
            self.tray.order.remove(tid)
            return 1
        return 0

    def tr__updatePanel(self, root, win):

        for t in self.tray.tasks.values():
            iwant=0
            ifail=0
            try:
                iwant=t.obj.get_wm_normal_hints().min_width
            except:
                ifail=1
                pass
            if ifail==0:
                t.width = ICONSIZE

        w1 = SIZE + BORDER*2
        h1 = SIZE + BORDER*2
               
        w = 2 * OFFSET + len(self.tray.order) * (w1 + SPACE) - SPACE
        h = self.bar.cfg['icon_size']

        x1 = OFFSET
        y1 = int((h - SIZE)/2.0) #+ BORDER

        if self.bar.cfg['position'] == 'top' or self.bar.cfg['position'] == 'bottom':
            self.set_size_request(w, h)
        else:
            self.set_size_request(h, w)

        # telling each icon where it is to go now.
        ind = 0
        for tid in self.tray.order:
            t = self.tray.tasks[tid]

            if self.bar.cfg['position'] == 'top' or self.bar.cfg['position'] == 'bottom':
                t.x = OFFSET + ind * (w1 + SPACE) + BORDER
                t.y = y1
            else:
                t.y = OFFSET + ind * (w1 + SPACE) + BORDER
                t.x = y1
            
            ind += 1
                        
            t.obj.configure(onerror=self.error, x=t.x, y=t.y,
                            width=SIZE, height=SIZE)
            t.obj.map(onerror=self.error)

        self.tr__updateAlpha(False)

    def tr__updateAlpha(self, returnvar):

        if self.realized == 1:
            #~ self.update_alpha_mask()
            self.update_alpha_cairo()


    def update_alpha_cairo(self):
            rr = self.window.get_geometry()
            w, h = rr[2], rr[3]
            
            pixmap = gtk.gdk.Pixmap(None, w, h, 1)
            cr = pixmap.cairo_create()

            # Clear the bitmap to False
            cr.set_source_rgb(0, 0, 0)
            cr.set_operator(cairo.OPERATOR_DEST_OUT)
            cr.paint()

            # Draw our shape into the bitmap using cairo
            cr.set_operator(cairo.OPERATOR_OVER)
            cr.set_source_rgb(1, 1, 1)
            cr.set_line_width(1)
            radius = 4
            
            w1 = SIZE + BORDER*2
            h1 = SIZE + BORDER*2

            x1 = OFFSET
            y1 = int((h - h1)/2.0)
            
            if self.bar.cfg['position'] == 'top' or self.bar.cfg['position'] == 'bottom':
                rect = (x1, y1, w-2*OFFSET, h1)
            else:
                y1 = int((w - w1)/2.0)
                rect = (y1, x1, h1, h-2*OFFSET)
                
            self.draw_rounded_rect(cr, rect, radius)
            self.window.shape_combine_mask(pixmap, 0, 0)

    def update_alpha_mask(self):
            rr = self.window.get_geometry()
            w, h = rr[2], rr[3]
                       
            w1 = SIZE + BORDER*2
            h1 = SIZE + BORDER*2

            x1 = OFFSET + BORDER
            y1 = int((h - h1)/2.0) + BORDER

            self.wind.change_attributes(background_pixel=self.intColour) 
            tmpwin = gtk.gdk.pixmap_foreign_new(self.wind.id)  
            
            mask = gtk.gdk.Pixmap (None, w, h, 1)
            im = mask.get_image(0,0, w, h)
            
            ## reset mask
            for x in range(0, w):
                for y in range(0, h):
                    im.put_pixel(x, y, 0)

            for k in range(len(self.tray.order)):
                
                #Try to update the icon's mask
                tmpim = gtk.gdk.Image(gtk.gdk.IMAGE_NORMAL,gtk.gdk.visual_get_system(), SIZE, SIZE)
                tmpwin.copy_to_image(tmpim, x1, y1, 0, 0, SIZE, SIZE)

                for x in range(0, SIZE):
                    for y in range(0, SIZE):
                        if not tmpim.get_pixel(x,y)==self.intColour:

                            im.put_pixel(x1+x, y1+y, 1)
                
                x1 = OFFSET + BORDER + (w1 + SPACE)*k

            self.window.shape_combine_mask(mask, 0, 0)

    def draw_rounded_rect(self, cr, rect, radius):
        x, y, width, height = rect[0], rect[1], rect[2], rect[3]
        cr.translate(x, y)
        cr.move_to  (0, radius)
        cr.arc (radius, radius, radius, 3.14, 1.5 * 3.14)
        cr.line_to (width - radius, 0)
        cr.arc (width - radius, 0 + radius, radius, 1.5 * 3.14, 0.0)
        cr.line_to (width , height - radius)
        cr.arc (width - radius, height - radius, radius, 0.0, 0.5 * 3.14)
        cr.line_to (radius, height)
        cr.arc (radius, height - radius, radius, 0.5 * 3.14, 3.14)
        cr.close_path ()
        cr.fill()
        #~ cr.stroke()
        
        #~ cr.rectangle(BORDER, BORDER, SIZE, SIZE)
        #~ cr.stroke()

    def tr__sendEvent(self, win, ctype, data, mask=None):
    #------------------------------------------------
        """ Send a ClientMessage event to the root """
        data = (data+[0]*(5-len(data)))[:5]
        ev = Xlib.protocol.event.ClientMessage(window=win,
                       client_type=ctype, data=(32, (data)))

        if not mask:
            mask = (X.SubstructureRedirectMask|X.SubstructureNotifyMask)
        self.root.send_event(ev, event_mask=mask)

    def tr__testTiming(self,var,var2):
        # Event "loop"
        # called every 1/10th second, does all events and quits
        # quickest hack towards multi-threading i had ;)
        while self.dsp.pending_events()>0:
            e = self.dsp.next_event()
            if e.type == X.ButtonRelease:
                if(e.detail == 3):
                    # Button 3 is right click.
                    pass
            if e.type == X.DestroyNotify:
                if self.tr__taskDelete(e.window.id):
                    self.tr__updatePanel(self.root, self.wind)
            if e.type == X.ConfigureNotify:
                task = self.tray.tasks[e.window.id]
                task.obj.configure(onerror=self.error,
                     width=ICONSIZE, height=ICONSIZE)
                self.tr__updatePanel(self.root, self.wind)
            if e.type == X.Expose and e.count==0:
                if(e.window.id==self.wind.id):
                    self.wind.clear_area(0, 0, 0, 0)
                    self.tr__updatePanel(self.root, self.wind)
            if e.type == X.ClientMessage:
                data = e.data[1][1]
                task = e.data[1][2]
                if e.client_type == self._OPCODE and data == 0:
                    obj = self.dsp.create_resource_object("window", task)
                    pid=0
                    try:
                        pidob= obj.get_property(self._PIDTHING,
                            X.AnyPropertyType, 0, 1024)
                        pid = pidob.value[0]
                    except:
                        pass
                    # we either get its Process ID, or an X-error
                    # Yay :D

                    if pid:

                        obj.reparent(self.tray.window.id, 0, 0)
                        ourmask = (X.ExposureMask|X.StructureNotifyMask)
                        obj.change_attributes(event_mask=ourmask)
                        self.tray.tasks[task] = Obj(obj=obj, x=0, y=0,
                            width=0, height=ICONSIZE, pid=pid)
                        self.tray.order.append(task)
                        self.tr__updatePanel(self.root, self.wind)
        return True

    def tr__setProps(self, dsp, win):
    #----------------------------
        """ Set necessary X atoms and panel window properties """
        self._ABOVE = dsp.intern_atom("_NET_WM_STATE_ABOVE")
        self._BELOW = dsp.intern_atom("_NET_WM_STATE_BELOW")
        self._BLACKBOX = dsp.intern_atom("_BLACKBOX_ATTRIBUTES")
        self._CHANGE_STATE = dsp.intern_atom("WM_CHANGE_STATE")
        self._CLIENT_LIST = dsp.intern_atom("_NET_CLIENT_LIST")
        self._CURRENT_DESKTOP = dsp.intern_atom("_NET_CURRENT_DESKTOP")
        self._DESKTOP = dsp.intern_atom("_NET_WM_DESKTOP")
        self._DESKTOP_COUNT = dsp.intern_atom("_NET_NUMBER_OF_DESKTOPS")
        self._DESKTOP_NAMES = dsp.intern_atom("_NET_DESKTOP_NAMES")
        self._HIDDEN = dsp.intern_atom("_NET_WM_STATE_HIDDEN")
        self._ICON = dsp.intern_atom("_NET_WM_ICON")
        self._NAME = dsp.intern_atom("_NET_WM_NAME")
        self._RPM = dsp.intern_atom("_XROOTPMAP_ID")
        self._SHADED = dsp.intern_atom("_NET_WM_STATE_SHADED")
        self._SHOWING_DESKTOP = dsp.intern_atom("_NET_SHOWING_DESKTOP")
        self._SKIP_PAGER = dsp.intern_atom("_NET_WM_STATE_SKIP_PAGER")
        self._SKIP_TASKBAR = dsp.intern_atom("_NET_WM_STATE_SKIP_TASKBAR")
        self._STATE = dsp.intern_atom("_NET_WM_STATE")
        self._STICKY = dsp.intern_atom("_NET_WM_STATE_STICKY")
        self._STRUT = dsp.intern_atom("_NET_WM_STRUT")
        self._STRUTP = dsp.intern_atom("_NET_WM_STRUT_PARTIAL")
        self._WMSTATE = dsp.intern_atom("WM_STATE")
        self._PIDTHING = dsp.intern_atom("_NET_WM_PID")

        win.set_wm_name("ADeskBar_Systray")
        win.set_wm_class("ADeskBar_Systray", "ADeskBar_Systray")

        win.set_wm_hints(flags=(Xutil.InputHint|Xutil.StateHint),
            input=0, initial_state=1)
        win.set_wm_normal_hints(flags=(
            Xutil.PPosition|Xutil.PMaxSize|Xutil.PMinSize),
            min_width=80, min_height=48,
            max_width=2000, max_height=48)
        win.change_property(dsp.intern_atom("_WIN_STATE"),
            Xatom.CARDINAL, 32, [1])
        win.change_property(dsp.intern_atom("_MOTIF_WM_HINTS"),
            dsp.intern_atom("_MOTIF_WM_HINTS"), 32, [0x2, 0x0, 0x0, 0x0, 0x0])
        win.change_property(self._DESKTOP, Xatom.CARDINAL, 32, [0xffffffffL])
        win.change_property(dsp.intern_atom("_NET_WM_WINDOW_TYPE"),
            Xatom.ATOM, 32, [dsp.intern_atom("_NET_WM_WINDOW_TYPE_UTILITY")])

    def cleanup(self):
        # This is my attempt to cleanly close, in such a way that the icons do
        # not get an X window error
        for tid in self.tray.order:
            t = self.tray.tasks[tid]
            g= t.obj.query_tree()
            t.obj.unmap()
            t.obj.unmap_sub_windows()
            self.dsp.sync()
            t.obj.reparent(g.root.id, 0, 0)
            
        #Release the selection so that other system trays can start.
        #This would be done automatically by the X-server anyway when the screenlet exits
        request.SetSelectionOwner(display = self.selowin.display, onerror = None, window = 0, selection = self.selection,time = X.CurrentTime)
        self.tr__sendEvent(self.root, self.manager,[X.CurrentTime, self.selection, 0], (X.StructureNotifyMask))
        self.dsp.sync()

    def redraw(self):
        #~ self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("red"))
        print 'Systray redraw ..'
        self.window.clear_area_e(0, 0, self.allocation.width, self.allocation.height)
        return

gobject.type_register(SysTray)
