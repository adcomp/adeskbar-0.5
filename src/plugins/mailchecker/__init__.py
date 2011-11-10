# -*- coding: utf-8 -*-

# - Uses some code from "Conky Email" by Mark Buck (Kaivalagi) <m_buck@hotmail.com>

import gobject

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

import imaplib, socket, re
from email.header import decode_header

mail = {}

class Option:
     def __init__(self,servername,folder,username,password,connectiontimeout,mailinfo):
          self.servername = servername
          self.folder = folder
          self.username = username
          self.password = password
          self.connectiontimeout = connectiontimeout
          self.mailinfo = mailinfo



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

        options = Option(self.settings['servername'],self.settings['folder'],self.settings['username'],self.settings['password'],int(self.settings['connectiontimeout']),int(self.settings['mailinfo']))

        emailinfo = EmailInfo(options)
        mail=emailinfo.writeOutput()

        if mail == None:
            icon = 'mail-mark-important'
            self.can_show_icon = True
            self.set_size_request(self.cfg['icon_size'], self.cfg['icon_size'])
            if self.cfg['tooltips']:
              self.gmail.plugin.tooltip = _('Error loading mail')
        elif mail == {}:
            icon = 'mail-read'
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
            label = (mail[key][1].ljust(80-len(mail[key][0]))+mail[key][0]).rjust(80)
            button = Core.image_button(label, 'mail-unread', int(self.plugin.settings['icon_size']))
            button.connect("button-release-event", self.onClicked, self.plugin.settings['exec_cmd'])
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










































class EmailData:
    def __init__(self, servername, folder, username, num, sender, subject):
        self.servername = servername
        self.folder = folder
        self.username = username
        self.num = num
        self.sender = sender
        self.subject = subject

class EmailInfo:

    IMAP_SEARCH_OPTION = "UNSEEN" # "RECENT"

    emaillist = []

    def __init__(self,options):
        self.options = options

    def getOutputData(self,servername,folder,username,password,connectiontimeout,mailinfo):
        try:
            socket.setdefaulttimeout(connectiontimeout)
            count = self.getIMAPEmailData(servername,folder,username,password,mailinfo)

            if count == None:
                return None
            elif count == 0:
                mail.clear()
            else:
                if mailinfo > 0:
                    counter = -1
                    for emaildata in self.emaillist:
                        counter = counter - 1
                        if mailinfo >= counter:
                            emaildata.sender=emaildata.sender.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
                            emaildata.subject=emaildata.subject.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
                            mail[counter]=emaildata.sender.encode("utf-8"), emaildata.subject.encode("utf-8")

            return mail

        except Exception, e:
            self.logError("getOutputData:Unexpected error:" + e.__str__())
            return None

    def getEmailData(self,servername,folder,username,num,lines):

        try:
            self.logInfo("Processing email data to determine 'From', 'Subject' and 'Received Date'")

            sender = None
            subject = None

            for line in lines:
                if sender is None and line.find("From: ") >= 0:
                    text = line.replace("From: ","").strip("\r ")
                    try:
                        text = self.decodeHeader(text)
                    except Exception, e:
                        sender = text
                        self.logError("getEmailData:Unexpected error when decoding sender:" + e.__str__())
                    sender = re.sub('<.*?@.*?>','',text).strip().lstrip('"').rstrip('"') # remove trailing email in <>
                elif subject is None and line.find("Subject: ") >= 0:
                    text = line.replace("Subject: ","").strip("\r\" ")
                    try:
                        subject = self.decodeHeader(text)
                    except Exception, e:
                        subject = text
                        self.logError("getEmailData:Unexpected error when decoding subject:" + e.__str__())

                if sender is not None and \
                   subject is not None:
                    break

            if subject is None:
                subject = ""

            emaildata = EmailData(servername, folder, username, num, sender, subject)

            return emaildata

        except Exception, e:
            self.logError("getEmailData:Unexpected error:" + e.__str__())
            return None


    def getIMAPEmailData(self,servername,folder,username,password,mailinfo):

        try:

            self.logInfo("Logging on to IMAP server: "+ servername)
            imap = imaplib.IMAP4_SSL(servername)
            imap.login(username, password)

            self.logInfo("Searching for new mail on IMAP server \"%s\" in folder \"%s\""%(servername,folder))

            imap.select(folder)
            typ, data = imap.search(None, self.IMAP_SEARCH_OPTION)
            for item in data:
                if item == '':
                    data.remove(item)

            if len(data) > 0:
                nums = data[0].split()
                count = (len(nums))
            else:
                count = 0

            if count > 0 and mailinfo > 0:

                self.logInfo("Extracting message data for IMAP server: "+ servername)

                self.emaillist = []

                for num in nums:
                    typ, message = imap.fetch(num, '(BODY.PEEK[HEADER])')
                    lines = message[0][1].split("\n") # grab the content we want and split out lines

                    emaildata = self.getEmailData(servername,folder,username,num,lines)
                    if emaildata is not None:
                        self.emaillist.append(emaildata)

            self.logInfo("Logging of from IMAP server: "+ servername)

            #imap.close()
            #imap.logout()
            imap.shutdown()

            return count

        except Exception, e:
            self.logError("getIMAPEmailData:Unexpected error:" + e.__str__())
            return None

    def writeOutput(self):

        mail = self.getOutputData(self.options.servername,self.options.folder,self.options.username,self.options.password,self.options.connectiontimeout,self.options.mailinfo)
        return mail #.encode("utf-8")

    def decodeHeader(self,header_text):

        text,encoding = decode_header(header_text)[0]
        if encoding:
            try:
                return text.decode(encoding)
            except: # fallback on decode error to windows encoding as this may be introduced by sloppy mail clients
                return text.decode('cp1252')
        else:
            return text

    def logInfo(self, text):
        return
        #print "INFO: " + text

    def logError(self, text):
        return
        #print "ERROR: " + text
