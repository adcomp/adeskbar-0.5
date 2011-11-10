# -*- coding: utf-8 -*-
#
# ADeskBar - "Session" plugin
#
##

import gtk

import adesk.plugin as Plg
import adesk.core as Core
import adesk.ui as UI

import locale
import gettext
## Translation
locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain('adeskbar', './locale')
gettext.bind_textdomain_codeset('adeskbar','UTF-8')
gettext.textdomain('adeskbar')
_ = gettext.gettext

session = { 'logout':(_('Log Out'),_('log out the session.'), 'system-log-out'),
            'hibernate':(_('Hibernate'),_('save session and power off.'), 'gnome-session-hibernate'),
            'suspend':(_('Suspend'),_('suspend session.'), 'gnome-session-suspend'),
            'reboot':(_('Reboot'),_('restart computer.'), 'gnome-session-reboot'),
            'shutdown':(_('Shut Down'),_('power off computer.'), 'system-shutdown'),
            'lockscreen':(_('Lock Screen'),_('lock screen to prevent unauthotised use.'), 'system-lock-screen'),
}

class Plugin(Plg.Plugin):
    def __init__(self, bar, settings):
        Plg.Plugin.__init__(self, bar, settings)
        
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
        
        self.box = gtk.VBox(False, 0)
        self.box.set_border_width(0)
        self.add(self.box)

        self.buttons = []
        self.create_session_button()

    def create_session_button(self):
        for action in ('lockscreen', 'logout', 'reboot', 'shutdown', 'hibernate', 'suspend'):
            if not self.plugin.settings[action] == '':
                
                if self.plugin.settings['show_label']:
                    label = '<b>%s</b>\n<small>%s</small>' % (session[action][0], session[action][1])
                    pixbuf = Core.get_pixbuf_icon(session[action][2], self.plugin.settings['icon_size'])
                    if pixbuf == None:
                       pixbuf = Core.pixbuf_from_file('images/plugins/session/'+session[action][2]+'.png', self.plugin.settings['icon_size'], self.plugin.settings['icon_size'])
                    button = Core.image_button(label, pixbuf, self.plugin.settings['icon_size'])
                else:
                    button = gtk.Button()
                    button.set_relief(gtk.RELIEF_NONE)
                    img = gtk.Image()
                    pixbuf = Core.get_pixbuf_icon(session[action][2], self.plugin.settings['icon_size'])
                    if pixbuf == None:
                       pixbuf = Core.pixbuf_from_file('images/plugins/session/'+session[action][2]+'.png', self.plugin.settings['icon_size'], self.plugin.settings['icon_size'])
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
