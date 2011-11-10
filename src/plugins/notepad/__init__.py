# adesk : "Notepad" plugin
# -*- coding: utf-8 -*-

import gtk
import time
import os

import adesk.plugin as Plg
import adesk.ui as UI
import adesk.core as Core

import locale
import gettext
## Translation
locale.setlocale(locale.LC_ALL, '')
#~ gettext.install('adeskbar', './locale', unicode=1)
gettext.bindtextdomain('adeskbar', './locale')
gettext.bind_textdomain_codeset('adeskbar','UTF-8')
gettext.textdomain('adeskbar')
_ = gettext.gettext

class Plugin(Plg.Plugin):

    def __init__(self, bar, settings):
        Plg.Plugin.__init__(self, bar, settings)

        self.lists = []

        self.text_first_item = ''
        self.notepad = Notepad(self, bar)
        self.lists = self.notepad.read()
        self.notepad.restart()

    def onClick(self, widget, event):
        self.notepad.toggle()

    def resize(self):
        self.set_size_request(self.cfg['icon_size'], self.cfg['icon_size'])

class Notepad(UI.PopupWindow):
    def __init__(self, plugin, bar):
        UI.PopupWindow.__init__(self, bar, plugin)
        self.plugin = plugin

        self.box = gtk.VBox(False, 0)
        self.add(self.box)
        self.init = 0
        self.restart()
        self.init = 1



    def restart(self):
        if self.init == 1:
          text = self.itemT.get_buffer()
          self.plugin.text_first_item = text.get_text(text.get_start_iter(), text.get_end_iter(), False)

        self.box.destroy()

        self.box = gtk.VBox(False, 0)
        self.add(self.box)
        self.resize(1, 1)
        self.box.set_size_request(-1, -1)

        for list in self.plugin.lists:
          item = gtk.Frame()
          item.set_border_width(5)

          itemV = gtk.VBox(False, 0)
          itemV.set_border_width(5)

          itemH = gtk.HBox(False, 0)

          itemN = gtk.Label(list['date'])
          itemN.set_width_chars(30)

          itemS = gtk.Button(_('Save'))
          itemS.set_border_width(2)
#          itemS.set_relief(gtk.RELIEF_NONE)
          itemS.set_focus_on_click(False)
          itemD = gtk.Button(_('Delete'))
          itemD.set_border_width(2)
#          itemD.set_relief(gtk.RELIEF_NONE)
          itemD.set_focus_on_click(False)
          itemT = gtk.TextView()
          itemT.set_border_width(2)
          itemT.set_wrap_mode(gtk.WRAP_WORD)
          itemT.get_buffer().set_text(list['text'].replace('\\n','\n'))

          itemD.connect("clicked", self.button_delete_clicked, list['date'])
          itemS.connect("clicked", self.button_save_clicked, list['date'], itemT.get_buffer())

          itemH.add(itemN)
          itemH.add(itemS)
          itemH.add(itemD)
          itemV.add(itemH)
          itemV.add(itemT)
          item.add(itemV)
          self.box.pack_end(item)


        item = gtk.Frame()
        item.set_border_width(5)

        itemV = gtk.VBox(False, 0)
        itemV.set_border_width(5)

        itemH = gtk.HBox(False, 0)

        itemN = gtk.Label('')
        itemN.set_width_chars(30)



        itemS = gtk.Button(_('Save'))
        itemS.set_border_width(2)
#        itemS.set_relief(gtk.RELIEF_NONE)
        itemS.set_focus_on_click(False)
        itemD = gtk.Button(_('Delete'))
        itemD.set_border_width(2)
#        itemD.set_relief(gtk.RELIEF_NONE)
        itemD.set_focus_on_click(False)

        self.itemT = gtk.TextView()
        self.itemT.set_border_width(2)
        self.itemT.set_wrap_mode(gtk.WRAP_WORD)
        self.itemT.get_buffer().set_text(self.plugin.text_first_item)

        itemD.connect("clicked", self.button_cleartext_clicked, self.itemT.get_buffer() )
        itemS.connect("clicked", self.button_save_clicked, 'now', self.itemT.get_buffer() )

        itemH.add(itemN)
        itemH.add(itemS)
        itemH.add(itemD)
        itemV.add(itemH)
        itemV.add(self.itemT)
        item.add(itemV)
        self.box.pack_end(item)

        self.itemT.grab_focus()
        self.box.show_all()

    def button_cleartext_clicked(self, widget, text):
        text.delete(text.get_start_iter(),  text.get_end_iter())

    def button_save_clicked(self, widget, date, text):
        text = text.get_text(text.get_start_iter(), text.get_end_iter(), False)
        got = 0
        for list in self.plugin.lists:
            if list['date'] == date:
               list['text'] = text
               got = 1
        if (got == 0) & (date == 'now') & (text != ''):
             newdict = {}
             newdict['date'] = time.strftime('%s' % ('%c'), time.localtime())
             newdict['text'] = text
             self.plugin.lists.append(newdict)

        self.save()
        self.restart()



    def button_delete_clicked(self, widget, date):
        for list in self.plugin.lists:
            if list['date'] == date:
               self.plugin.lists.remove(list)
               self.save()
               self.restart()




    def read(self):
        cfg_file = 'notepad'
        home = os.environ['HOME']
        if os.access("%s/.config/adeskbar/%s.cfg" % (home, cfg_file), os.F_OK|os.R_OK):
          conf_path = "%s/.config/adeskbar/%s.cfg" % (home, cfg_file)
        try:
          f = open(conf_path,'r')
          for line in f:
            self.plugin.lists = line.strip('\n')
          f.close()
        except Exception, e:
          self.plugin.lists = []

        self.lists = []
        list_dict = {}
        list_str=self.plugin.lists
        if self.plugin.lists.__class__ ==  str:
          if (list_str != '[]'):
            q=[]
            try:
              q=list_str[2:-2].split("}, {")
            except Exception, e:
              q.append(list_str[2:-2])
            for a in q:
              paras = a[1:-1].split("', '")
              for line in paras:
                k, v  = line.split("': '")
                list_dict[k]=v.replace('\\n','\n')

              self.lists.append(list_dict)
              list_dict={}

        return self.lists


    def save(self):
        home = os.environ['HOME']
        if not os.path.exists("%s/.config/adeskbar" % home):
            os.makedirs("%s/.config/adeskbar" % home)

        cfg_file = 'notepad'
        src = "%s/.config/adeskbar/%s.cfg" % (home,cfg_file)
        str_cfg = ''

        for key in self.plugin.lists:
          if key.__class__ == dict:
            if not key == {}:
              str_cfg += '{'
              for item in key:
                key[item]=key[item].replace('\n','\\n')
                str_cfg += '\'%s\': \'%s\', ' % (item, key[item])
              str_cfg = str_cfg[:-2]
              str_cfg += '}, '
        str_cfg = str_cfg[:-2]
        str_cfg = '['+str_cfg+']'

        configfile =  open(src, 'w')
        configfile.write(str_cfg)
        configfile.close()
