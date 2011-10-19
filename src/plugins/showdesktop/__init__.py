# adesk : Show/Hide Desktop plugin

import adesk.plugin as Plg
import gtk

try:
    import wnck
except:
    Core.logINFO('Plugin "showdesktop" need python-wnck')
    Core.logINFO(' -- debian/ubuntu : "sudo apt-get install python-wnck"')

class Plugin(Plg.Plugin):

    def __init__(self, bar, settings):
        Plg.Plugin.__init__(self, bar, settings)
        self.can_zoom = True

        #~ screen = wnck.screen_get_default()
        #~ screen.connect("active_workspace_changed", self.workspace_changed)
        #~ self.active_workspace = gtk.Label()
        #~ self.add(self.active_workspace)
        #~ self.active_workspace.show()
        #~ self.workspace_changed(screen, None)

    def onClick(self, widget, event):
        screen = wnck.screen_get_default()
        # showing windows = not showing desktop
        showing_windows = not screen.get_showing_desktop()
        screen.toggle_showing_desktop(showing_windows)

    def resize(self):
        self.set_size_request(self.cfg['icon_size'], self.cfg['icon_size'])
        
    def workspace_changed(self, screen, space):
        active_wp = screen.get_active_workspace()
        num = active_wp.get_number()
        self.active_workspace.set_text(str(num+1))
