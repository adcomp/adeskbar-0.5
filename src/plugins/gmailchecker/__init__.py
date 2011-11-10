# -*- coding: utf-8 -*-

import gobject
import urllib
import xml.dom.minidom

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

mail = {}

class Plugin(Plg.Plugin):

    def __init__(self, bar, settings):
        Plg.Plugin.__init__(self, bar, settings)
        self.settings = settings

        self.id = 0
        self.settings['hide_icon'] = int(self.settings['hide_icon'])
        self.settings['icon_size'] = int(self.settings['icon_size'])

        self.gmail = Gmail(self, bar)

    def onClick(self, widget, event):
        if int(len(mail)) != 0:
          self.gmail.toggle()

    def update_time(self):
        username=self.settings['username']
        password=self.settings['password']

        mail.clear()
        error='No'
        icon = 'mail-read'

        try:
          usock = urllib.urlopen("https://"+username+":"+password+"@mail.google.com/mail/feed/atom")
          xmldoc = xml.dom.minidom.parse(usock)
          usock.close()
          #print xmldoc.toxml()
          collection = xmldoc.documentElement
          fullcount = collection.getElementsByTagName("fullcount")[0].childNodes[0].data
          entrys = collection.getElementsByTagName("entry")
        except Exception, e:
          entrys=''
          fullcount=0
          error='Yes'
          icon = 'mail-mark-important'
          if self.cfg['tooltips']:
            self.gmail.plugin.tooltip = _('Error loading mail')

        for entry in entrys:
           try:
             title = entry.getElementsByTagName('title')[0].childNodes[0].data
           except Exception, e:
             title=''

           try:
             summary = entry.getElementsByTagName('summary')[0].childNodes[0].data
           except Exception, e:
             summary=''

           link = entry.getElementsByTagName('link')[0].getAttribute("href")

           id = entry.getElementsByTagName('id')[0].childNodes[0].data

           authors = entry.getElementsByTagName('author')
           for author in authors:
             try:
               name = author.getElementsByTagName('name')[0].childNodes[0].data
             except Exception, e:
               name = ''

           title=title.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
           summary=summary.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
           name=name.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
           mail[id]=title, summary, name, link

        if int(fullcount) == 0:
            if error == 'Yes':
              self.can_show_icon = True
              self.set_size_request(self.cfg['icon_size'], self.cfg['icon_size'])
            else:
              #icon = 'stock_mail-open'
              #icon = 'mail-mark-read'
              if self.settings['hide_icon'] == 0:
                self.can_show_icon = True
                self.set_size_request(self.cfg['icon_size'], self.cfg['icon_size'])
              else:
                self.can_show_icon = False
                self.set_size_request(-1, -1)
              if self.cfg['tooltips']:
                self.gmail.plugin.tooltip = _('No unread mail')
        else:
            #icon = 'stock_mail-unread'
            #icon = 'mail-mark-unread'
            icon = 'mail-unread'
            self.can_show_icon = True
            self.set_size_request(self.cfg['icon_size'], self.cfg['icon_size'])
            if self.cfg['tooltips']:
              self.gmail.plugin.tooltip = _('Unread mail : ')+str(len(mail))
            if int(self.settings['play_sound']) == 1:
              if self.settings['file_sound'] != '':
                              if Core.isfile('/usr/bin/mplayer') | \
                                 Core.isfile('/usr/local/bin/mplayer'):
                                    Core.launch_command('mplayer -quiet "'+self.settings['file_sound']+'"&')

        self.gmail.update_icon_status(icon)

        self.gmail.restart()
        return True

    def resize(self):
        self.gmail.restart()

    def on_init(self):
        if self.settings['hide_icon'] == 0:
          self.can_show_icon = True
          self.set_size_request(self.cfg['icon_size'], self.cfg['icon_size'])
        else:
          self.can_show_icon = False
          self.set_size_request(-1, -1)
        if int(self.settings['checkonstart']) == 1:
          self.restart()

    def restart(self):
        if self.id != 0:
          gobject.source_remove(self.id)
        self.id=gobject.timeout_add(int(self.settings['minutes_to_update'])*60*1000, self.update_time)
        self.update_time()

class Gmail(UI.PopupWindow):
    def __init__(self, plugin, bar):
        UI.PopupWindow.__init__(self, bar, plugin)
        self.plugin = plugin

        self.box = gtk.VBox(False, 0)
        self.box.set_border_width(0)
        self.add(self.box)

        self.buttons = []
        self.create_session_button()

    def create_session_button(self):
        for key in mail.keys():
            label = (mail[key][0].ljust(80-len(mail[key][2]))+mail[key][2]).rjust(80)+"\n"+mail[key][1]
            button = Core.image_button(label, 'mail-unread', int(self.plugin.settings['icon_size']))
            button.connect("button-release-event", self.onClicked, self.plugin.settings['exec_cmd']+' "'+mail[key][3]+'"')
            self.box.pack_start(button, False)
            self.buttons.append(button)

        self.box.show_all()

    def onClicked(self, widget, event, action):
        Core.launch_command(action)
        ## hide window
        self.toggle(self)

    def restart(self):
        for button in self.buttons:
            self.box.remove(button)
            button.destroy()
        self.buttons = []
        self.resize(1, 1)
        self.box.set_size_request(-1, -1)
        self.create_session_button()

    def update_icon_status(self, icon):
        self.plugin.set_icon(icon)
