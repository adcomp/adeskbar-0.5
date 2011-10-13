# -*- coding: utf-8 -*-

import gtk

import adesk.plugin as Plg
import adesk.core as Core
import adesk.ui as UI

session = { 'logout':('Log Out','log out the session.', 'gnome-session-logout'),
            'hibernate':('Hibernate','save session and power off.', 'gnome-session-hibernate'),
            'suspend':('Suspend','suspend session.', 'gnome-session-suspend'),
            'reboot':('Reboot','restart computer.', 'gnome-session-reboot'),
            'shutdown':('Shut Down','power off computer.', 'gnome-session-halt'),
            'lockscreen':('Lock Screen','lock screen to prevent unauthotised use.', 'system-lock-screen'),
          }

class Plugin(Plg.Plugin):
    def __init__(self, bar, settings):
        Plg.Plugin.__init__(self, bar, settings)
        self.settings = settings
        self.can_zoom = True
        
        # FIXME !! new in v0.3.9
        if not 'show_label' in self.settings:
            self.settings['show_label'] = True
        else:
            if self.settings['show_label'] in (True, 'true','True','1','yes'):
                self.settings['show_label'] = True
            else:
                self.settings['show_label'] = False
        if not 'icon_size' in self.settings:
            self.settings['icon_size'] = 32
        else:
            self.settings['icon_size'] = int(self.settings['icon_size'])
            
        self.session = Session(self, bar)

    def onClick(self, widget, event):
        self.session.toggle()

    def resize(self):
        self.set_size_request(self.cfg['icon_size'], self.cfg['icon_size'])

    def restart(self):
        self.session.restart()
        
class Session(UI.PopupWindow):

    def __init__(self, plugin, bar):
        UI.PopupWindow.__init__(self, bar, plugin)
        self.plugin = plugin
        
        self.box = gtk.VBox(False, 0)
        self.box.set_border_width(0)
        self.add(self.box)

        self.buttons = []
        self.create_session_button()

    def create_session_button(self):
        for action in ('lockscreen','logout','hibernate','suspend',
                       'reboot','shutdown'):
                           
            if not self.plugin.settings[action] == '':
                
                if self.plugin.settings['show_label']:
                    label = '<b>%s</b>\n<small>%s</small>' % (session[action][0], session[action][1])
                    button = Core.image_button(label, session[action][2], self.plugin.settings['icon_size'])
                else:
                    button = gtk.Button()
                    button.set_relief(gtk.RELIEF_NONE)
                    img = gtk.Image()
                    pixbuf = Core.get_pixbuf_icon(session[action][2], self.plugin.settings['icon_size'])
                    img.set_from_pixbuf(pixbuf)
                    button.add(img)
                button.connect("button-release-event", self.onClicked, self.plugin.settings[action])
                self.box.pack_start(button, False)
                self.buttons.append(button)
                
        self.box.show_all()

    def onClicked(self, widget, event, action):
        Core.launch_command(action)
        self.toggle(self)

    def restart(self):
        for button in self.buttons:
            self.box.remove(button)
            button.destroy()
        self.buttons = []
        self.resize(1, 1)
        self.box.set_size_request(-1, -1)
        self.create_session_button()
