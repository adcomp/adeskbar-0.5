# coding: utf8

# adesk : "Alarm Clock" plugin

import gtk
import pango
import gobject
import time

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


class Plugin(Plg.PluginContainer):
    isshow = 0
    def __init__(self, bar, settings):
        Plg.PluginContainer.__init__(self, bar, settings)
        self.can_zoom = False
        self.can_show_icon = False
        self.settings = settings
        self.bar = bar

        self.locked = False
        
        self.box = gtk.VBox(False, 0)
        self.box.set_border_width(0)
        self.add(self.box)

        self.set_from_config()

        self.calendarplugin = Calendar(self, bar)
        self.connect('enter-notify-event', self.onShow)
        self.connect('leave-notify-event', self.onHide)
        if int(self.settings['mouseover']) == 1:
          self.has_tooltip = False
        else:
          if self.cfg['tooltips']:
            self.has_tooltip = True

        self.update_time()
        gobject.timeout_add(1000, self.update_time)

    def onShow(self, widget, event):
        if int(self.settings['mouseover']) == 1:
          self.calendarplugin.restart()
          self.calendarplugin.show()
          self.isshow=1

    def onHide(self, widget, event):
        if int(self.settings['mouseover']) == 1:
          self.calendarplugin.hide()
          self.isshow=0

    def onClick(self, widget, event):
          if int(self.isshow) == 0:
            self.isshow=1
            self.calendarplugin.show()
          else:
            self.isshow=0
            self.calendarplugin.hide()

    def set_from_config(self):
#        a = str('\xd0\xa3\xd0\xa0\xd0\x90!')
#        print a.decode('utf-8')
        # make new array from string
        # all value must be in string !
        # because when you save the array, it looks like a string: [{'text':'\xd0\xa3\xd0\xa0\xd0\x90'}]
        # but when the load value, adeskbar takes it as a string type
        self.alarmlist = []
        alarmlist_dict = {}
        alarmlist_str=self.settings['alarmlist']
        if self.settings['alarmlist'].__class__ ==  str:
          if (alarmlist_str != '[]'):
            q=[]
            try:
              q=alarmlist_str[2:-2].split("}, {")
            except Exception, e:
              q.append(alarmlist_str[2:-2])
            for a in q:
              paras = a[1:-1].split("', '")
              for line in paras:
                k, v  = line.split("': '")
                alarmlist_dict[k]=v

              self.alarmlist.append(alarmlist_dict)
              alarmlist_dict={}

        else:
          self.alarmlist = self.settings['alarmlist']

        self.min_for_alarm = ''
        self.time_txt = ''
        self.date_txt = ''
        self.lb_time = gtk.Label()
        self.lb_time.modify_font(pango.FontDescription(self.settings['time_font']))
        self.lb_time.set_use_markup(True)
        self.lb_time.set_alignment(0.5,0.5)
        self.box.pack_start(self.lb_time)

        if not self.settings['date'] == '':
            self.lb_date = gtk.Label()
            self.lb_date.modify_font(pango.FontDescription(self.settings['date_font']))
            self.lb_date.set_use_markup(True)
            self.lb_date.set_alignment(0.5,0.5)
            self.box.pack_start(self.lb_date)
        else:
            self.lb_date = None
        self.box.show_all()

    def update_time(self):
        if self.locked:
            return True

        now = time.localtime()
        time_current = time.strftime('<span color="%s">%s</span>' % (self.settings['time_color'], self.settings['time']), now)
        if self.lb_date:
            date_current = time.strftime('<span color="%s">%s</span>' % (self.settings['date_color'], self.settings['date']), now)
        if not time_current == self.time_txt:
            self.lb_time.set_markup(time_current)
            self.time_txt = time_current
            if self.lb_date:
                self.lb_date.set_markup(date_current)
                self.date_txt = date_current
        if self.cfg['tooltips'] & (self.settings['tooltip'] != ''):
            self.calendarplugin.plugin.tooltip = time.strftime(self.settings['tooltip'], now)




        min_for_alarm_current = str(time.strftime('%M', now))
        if not min_for_alarm_current == self.min_for_alarm:
          self.min_for_alarm = min_for_alarm_current

          if self.alarmlist != []:
            plus5min = time.localtime( time.time() + 300 )  #5 minutes *60
            for alarm in self.alarmlist:
              if alarm != {}:
                if   ( ( (alarm['date_d'] != '') & \
                         (str(alarm['date_m']) == str(time.strftime('%m', now))) ) & \
                         ((str(alarm['date_d']) == str(time.strftime('%d', now)) ) & \
                          (str(alarm['date_y']) == str(time.strftime('%Y', now)) ) & \
                          (str(alarm['time_h']) == str(time.strftime('%H', now)) ) & \
                          (str(alarm['time_m']) == str(time.strftime('%M', now)) ) ) ) | \
                        \
                     ( ( (alarm['date_d'] == '') & \
                         (str(alarm['time_m']) == str(time.strftime('%M', now)) ) & \
                         (str(alarm['time_h']) == str(time.strftime('%H', now)) ) ) & \
                           (( (str(time.strftime('%w', now)) == '1') & (str(alarm['day1']) == '1') ) | \
                            ( (str(time.strftime('%w', now)) == '2') & (str(alarm['day2']) == '1') ) | \
                            ( (str(time.strftime('%w', now)) == '3') & (str(alarm['day3']) == '1') ) | \
                            ( (str(time.strftime('%w', now)) == '4') & (str(alarm['day4']) == '1') ) | \
                            ( (str(time.strftime('%w', now)) == '5') & (str(alarm['day5']) == '1') ) | \
                            ( (str(time.strftime('%w', now)) == '6') & (str(alarm['day6']) == '1') ) | \
                            ( (str(time.strftime('%w', now)) == '0') & (str(alarm['day7']) == '1') ) ) ):
                          if (alarm['notify'] == '1') & (alarm['text'] != ''):
                              if Core.isfile('/usr/bin/notify-send') | \
                                 Core.isfile('/usr/local/bin/notify-send'):
                                Core.launch_command('notify-send "'+alarm['text']+'" -i task-due -t '+str(144000)+'&')  # 2 min
                              elif Core.isfile('/usr/bin/notify-osd') | \
                                 Core.isfile('/usr/local/bin/notify-osd'):
                                Core.launch_command('notify-osd "'+alarm['text']+'" -i task-due -t '+str(144000)+'&')  # 2 min
                              else:
                                try:
                                  import pynotify
                                  pynotify.init("Alamclock notification")
                                  n = pynotify.Notification(alarm['text'], "", "task-due")
                                  n.set_urgency(pynotify.URGENCY_CRITICAL)
                                  n.set_timeout(144000)
                                  n.show()
                                except:
                                  print "Error: need notify-osd or libnotify-bin or notify-send or python-notify"
                          if alarm['soundfile'] != '':               # /usr/bin/aplay -q
                              if Core.isfile('/usr/bin/mplayer') | \
                                 Core.isfile('/usr/local/bin/mplayer'):
                                    Core.launch_command('mplayer -quiet "'+alarm['soundfile']+'"&')

                          if alarm['cmd'] != '':
                            Core.launch_command('"'+alarm['cmd']+'"&')


                elif (alarm['remind'] == '1') & (alarm['text'] != '') & \
                     ( ( (alarm['date_d'] != '') & \
                         (str(alarm['date_m']) == str(time.strftime('%m', plus5min))) ) & \
                         ((str(alarm['date_d']) == str(time.strftime('%d', plus5min)) ) & \
                          (str(alarm['date_y']) == str(time.strftime('%Y', plus5min)) ) & \
                          (str(alarm['time_h']) == str(time.strftime('%H', plus5min)) ) & \
                          (str(alarm['time_m']) == str(time.strftime('%M', plus5min)) ) ) ) | \
                        \
                     ( ( (alarm['date_d'] == '') & \
                         (str(alarm['time_m']) == str(time.strftime('%M', plus5min)) ) & \
                         (str(alarm['time_h']) == str(time.strftime('%H', plus5min)) ) ) & \
                           (( (str(time.strftime('%w', plus5min)) == '1') & (str(alarm['day1']) == '1') ) | \
                            ( (str(time.strftime('%w', plus5min)) == '2') & (str(alarm['day2']) == '1') ) | \
                            ( (str(time.strftime('%w', plus5min)) == '3') & (str(alarm['day3']) == '1') ) | \
                            ( (str(time.strftime('%w', plus5min)) == '4') & (str(alarm['day4']) == '1') ) | \
                            ( (str(time.strftime('%w', plus5min)) == '5') & (str(alarm['day5']) == '1') ) | \
                            ( (str(time.strftime('%w', plus5min)) == '6') & (str(alarm['day6']) == '1') ) | \
                            ( (str(time.strftime('%w', plus5min)) == '0') & (str(alarm['day7']) == '1') ) ) ):

                              if Core.isfile('/usr/bin/notify-send') | \
                                 Core.isfile('/usr/local/bin/notify-send'):
                                Core.launch_command('notify-send "'+_("Remind you that after about 5 minutes to do ")+alarm['text']+'" -i task-due -t '+str(144000)+'&')  # 2 min
                              elif Core.isfile('/usr/bin/notify-osd') | \
                                 Core.isfile('/usr/local/bin/notify-osd'):
                                Core.launch_command('notify-osd "'+_("Remind you that after about 5 minutes to do ")+alarm['text']+'" -i task-due -t '+str(144000)+'&')  # 2 min
                              else:
                                try:
                                  import pynotify
                                  pynotify.init("Alamclock notification")
                                  n = pynotify.Notification(_("Remind you that after about 5 minutes to do ")+alarm['text'], "", "task-due")
                                  n.set_urgency(pynotify.URGENCY_CRITICAL)
                                  n.set_timeout(144000)
                                  n.show()
                                except:
                                  print "Error: need notify-osd or libnotify-bin or notify-send or python-notify"
        return True

    def resize(self):
        if self.bar.cfg['position']=='top' or self.bar.cfg['position']=='bottom':
            self.set_size_request(-1, self.cfg['icon_size'])
        else:
            self.set_size_request(self.cfg['icon_size'], -1)

    def restart(self):
        if int(self.settings['mouseover']) == 1:
          self.has_tooltip = False
        else:
          if self.cfg['tooltips']:
            self.has_tooltip = True

        self.locked = True
        self.box.remove(self.lb_time)
        self.lb_time.destroy()
        if self.lb_date:
            self.box.remove(self.lb_date)
            self.lb_date.destroy()
        self.set_from_config()
        self.locked = False
        self.resize()
        self.update_time()



class Calendar(UI.PopupWindow):
    def __init__(self, plugin, bar):
        UI.PopupWindow.__init__(self, bar, plugin)
        self.plugin = plugin

        self.box = gtk.HBox(False, 0)
        self.box.set_border_width(5)

        self.add(self.box)
        self.create_calendar()

    def create_calendar(self):
        now = time.localtime()

        calendarbox = gtk.Calendar()
        calendarbox.mark_day(int(time.strftime('%d', now)))
        cal = gtk.VBox(False, 0)
        cal.pack_start(calendarbox, False, False)
        self.box.pack_start(cal, False, False)

        alarmnow = []
        alarmnowpast = []
        alarmpast = []
        alarmtomorrow = []
        alarmtomorrow_wday = str(int(time.strftime('%w', now)) + 1)       #1234560
        if str(alarmtomorrow_wday) == '7':
          alarmtomorrow_wday = '0'
        alarmtomorrow_day = int(time.strftime('%d', now)) + 1    # fix me, if day = 32
        if (alarmtomorrow_day <= 9):
           alarmtomorrow_day=str('0'+str(alarmtomorrow_day))

        if self.plugin.alarmlist != []:
          for alarm in self.plugin.alarmlist:
              if alarm != {}:
                if   ( ( (alarm['date_d'] != '') & \
                         (str(alarm['date_m']) == str(time.strftime('%m', now))) ) & \
                         ((str(alarm['date_d']) == str(time.strftime('%d', now)) ) & \
                          (str(alarm['date_y']) == str(time.strftime('%Y', now)) ) & \
                      ( ( (str(alarm['time_h']) == str(time.strftime('%H', now)) ) & \
                          (str(alarm['time_m']) >= str(time.strftime('%M', now)) ) ) | \
                          (str(alarm['time_h']) > str(time.strftime('%H', now)) ) ) ) ) | \
                        \
                     ( ( (alarm['date_d'] == '') & \
                      ( ( (str(alarm['time_h']) == str(time.strftime('%H', now)) ) & \
                          (str(alarm['time_m']) >= str(time.strftime('%M', now)) ) ) | \
                          (str(alarm['time_h']) > str(time.strftime('%H', now)) ) ) ) & \
                           (( (str(time.strftime('%w', now)) == '1') & (str(alarm['day1']) == '1') ) | \
                            ( (str(time.strftime('%w', now)) == '2') & (str(alarm['day2']) == '1') ) | \
                            ( (str(time.strftime('%w', now)) == '3') & (str(alarm['day3']) == '1') ) | \
                            ( (str(time.strftime('%w', now)) == '4') & (str(alarm['day4']) == '1') ) | \
                            ( (str(time.strftime('%w', now)) == '5') & (str(alarm['day5']) == '1') ) | \
                            ( (str(time.strftime('%w', now)) == '6') & (str(alarm['day6']) == '1') ) | \
                            ( (str(time.strftime('%w', now)) == '0') & (str(alarm['day7']) == '1') ) ) ):
                          alarmnow.append(alarm['time_h']+':'+alarm['time_m']+' '+alarm['text'])

                elif (alarm['date_d'] != '') & \
                     (alarm['date_d'] == str(alarmtomorrow_day)) & \
                     (alarm['date_m'] == str(time.strftime('%m', now))) & \
                     (alarm['date_y'] == str(time.strftime('%Y', now))) | \
                     ( (alarm['date_d'] == '') & \
                           (( (str(alarmtomorrow_wday) == '1') & (str(alarm['day1']) == '1') ) | \
                            ( (str(alarmtomorrow_wday) == '2') & (str(alarm['day2']) == '1') ) | \
                            ( (str(alarmtomorrow_wday) == '3') & (str(alarm['day3']) == '1') ) | \
                            ( (str(alarmtomorrow_wday) == '4') & (str(alarm['day4']) == '1') ) | \
                            ( (str(alarmtomorrow_wday) == '5') & (str(alarm['day5']) == '1') ) | \
                            ( (str(alarmtomorrow_wday) == '6') & (str(alarm['day6']) == '1') ) | \
                            ( (str(alarmtomorrow_wday) == '0') & (str(alarm['day7']) == '1') ) ) ):
                          alarmtomorrow.append(alarm['time_h']+':'+alarm['time_m']+' '+alarm['text'])

                elif (alarm['date_d'] != '') & \
                     (alarm['date_d'] == str(time.strftime('%d', now))) & \
                     (alarm['date_m'] == str(time.strftime('%m', now))) & \
                     (alarm['date_y'] == str(time.strftime('%Y', now))) | \
                     ( ( (alarm['date_d'] == '') & \
                      ( ( (str(alarm['time_h']) <= str(time.strftime('%H', now)) ) & \
                          (str(alarm['time_m']) <= str(time.strftime('%M', now)) ) ) | \
                          (str(alarm['time_h']) < str(time.strftime('%H', now)) ) ) ) & \
                           (( (str(time.strftime('%w', now)) == '1') & (str(alarm['day1']) == '1') ) | \
                            ( (str(time.strftime('%w', now)) == '2') & (str(alarm['day2']) == '1') ) | \
                            ( (str(time.strftime('%w', now)) == '3') & (str(alarm['day3']) == '1') ) | \
                            ( (str(time.strftime('%w', now)) == '4') & (str(alarm['day4']) == '1') ) | \
                            ( (str(time.strftime('%w', now)) == '5') & (str(alarm['day5']) == '1') ) | \
                            ( (str(time.strftime('%w', now)) == '6') & (str(alarm['day6']) == '1') ) | \
                            ( (str(time.strftime('%w', now)) == '0') & (str(alarm['day7']) == '1') ) ) ):
                          alarmnowpast.append(alarm['time_h']+':'+alarm['time_m']+' '+alarm['text'])

                elif (alarm['date_d'] != '') & \
                   ( (alarm['date_m'] < str(time.strftime('%m', now))) & \
                     (alarm['date_y'] <= str(time.strftime('%Y', now))) ) | \
                   ( (alarm['date_m'] == str(time.strftime('%m', now))) & \
                     (alarm['date_d'] < str(time.strftime('%d', now))) & \
                     (alarm['date_y'] <= str(time.strftime('%Y', now))) ):
                          alarmpast.append(alarm['date_d']+'/'+alarm['date_m']+' '+alarm['time_h']+':'+alarm['time_m']+' '+alarm['text'])

          if (alarmnow == []) & (alarmnowpast == []) & (alarmtomorrow == []) & (alarmpast == []):
            self.box.show_all()
            return

          sep = gtk.HBox(False, 0)
          sep.set_border_width(5)
          self.box.pack_start(sep, False, False)

          table = gtk.Table()
          self.box.pack_start(table, False, False)

          if alarmnow != []:
            alarmnow.sort()
            alarmnow_text=''
            for text in alarmnow:
              alarmnow_text+=text+'\n'
            if (alarmnowpast == []) & (alarmtomorrow == []):
              alarmnow_text=alarmnow_text[:-1]
            label = gtk.Label()
            label.set_markup("<b>"+_('Today tasks:')+"</b>\n"+alarmnow_text)
            label.set_alignment(0, 0)
            table.attach(label, 2, 3, 1, 2)
          if alarmnowpast != []:
            alarmnowpast.sort()
            alarmnowpast_text=''
            for text in alarmnowpast:
              alarmnowpast_text+=text+'\n'
            if (alarmtomorrow == []) & (alarmpast == []):
                alarmnowpast_text=alarmnowpast_text[:-1]
            label = gtk.Label()
            label.set_markup("<b>"+_('Today past tasks:')+"</b>\n"+alarmnowpast_text)
            label.set_alignment(0, 0)
            table.attach(label, 2, 3, 2, 3)
          if alarmtomorrow != []:
            alarmtomorrow.sort()
            alarmtomorrow_text=''
            for text in alarmtomorrow:
              alarmtomorrow_text+=text+'\n'
            if alarmpast == []:
              alarmtomorrow_text=alarmtomorrow_text[:-1]
            label = gtk.Label()
            label.set_markup("<b>"+_('Tomorrow tasks:')+"</b>\n"+alarmtomorrow_text)
            label.set_alignment(0, 0)
            table.attach(label, 2, 3, 3, 4)
          if alarmpast != []:
            alarmpast.sort()
            alarmpast_text=''
            for text in alarmpast:
              alarmpast_text+=text+'\n'
            label = gtk.Label()
            label.set_markup("<b>"+_('Past tasks:')+"</b>\n"+alarmpast_text[:-1])
            label.set_alignment(0, 0)
            table.attach(label, 2, 3, 4, 5)

        self.box.show_all()

    def restart(self):
        self.box.destroy()
        self.box = gtk.HBox(False, 0)
        self.box.set_border_width(5)

        self.add(self.box)

        self.resize(1, 1)
        self.box.set_size_request(-1, -1)
        self.create_calendar()
