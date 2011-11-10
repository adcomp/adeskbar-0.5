# -*- coding: utf-8 -*-

import gtk
import gobject

import time
import os

import adesk.core as core

import locale
import gettext
## Translation
locale.setlocale(locale.LC_ALL, '')
#~ gettext.install('adeskbar', './locale', unicode=1)
gettext.bindtextdomain('adeskbar', './locale')
gettext.bind_textdomain_codeset('adeskbar','UTF-8')
gettext.textdomain('adeskbar')
_ = gettext.gettext


settings = {
    'time':'%H:%M', 'time_color':'#EEEEEE', 'time_font':'Sans Bold 12',
    'date':'%d/%m', 'date_color':'#B5B5B5', 'date_font':'Sans Bold 8',
    'tooltip':'%c',
    'mouseover':1,
    'alarmlist': [],
    }

# position in list
ID_date = 0
ID_time = 1
ID_days = 2
ID_text = 3
ID_IND = 4

INFO = """%a  Locale’s abbreviated weekday name.
%A  Locale’s full weekday name.
%b  Locale’s abbreviated month name.
%B  Locale’s full month name.
%c  Locale’s appropriate date and time representation.
%d  Day of the month as a decimal number [01,31].
%D  month/day/year as a decimal number [01,12]/[01,31]/[00,99].
%H  Hour (24-hour clock) as a decimal number [00,23].
%I  Hour (12-hour clock) as a decimal number [01,12].
%j  Day of the year as a decimal number [001,366].
%m  Month as a decimal number [01,12].
%M  Minute as a decimal number [00,59].
%p  Locale’s equivalent of either AM or PM.     (1)
%S  Second as a decimal number [00,61].     (2)
%U  Week number of the year (Sunday as the first day of the week) as a decimal number [00,53].
    All days in a new year preceding the first Sunday are considered to be in week 0.   (3)
%w  Weekday as a decimal number [0(Sunday),6].
%W  Week number of the year (Monday as the first day of the week) as a decimal number [00,53].
    All days in a new year preceding the first Monday are considered to be in week 0.   (3)
%x  Locale’s appropriate date representation.
%X  Locale’s appropriate time representation.
%y  Year without century as a decimal number [00,99].
%Y  Year with century as a decimal number.
%Z  Time zone name (no characters if no time zone exists).
%%  A literal '%' character.

Notes:

1. the %p directive only affects the output hour field if the %I directive is used to parse the hour.

2. The range really is 0 to 61; this accounts for leap seconds and the (very rare) double leap seconds.

3. %U and %W are only used in calculations when the day of the week and the year are specified.
"""

class config():
    
    def __init__(self, box, conf, ind):

        self.conf = conf
        self.ind = ind

        framebox = gtk.VBox(False, 0)
        framebox.set_border_width(5)
        framebox.set_spacing(10)
        box.pack_start(framebox)

        for key in settings:
            if not key in conf.launcher[ind]:
                conf.launcher[ind][key] = settings[key]

        self.settings = conf.launcher[ind]

        # make new array from string
        # because when you save the array, it looks like a string: [{'text':'\xd0\xa3\xd0\xa0\xd0\x90'}]
        # but when the load value, adeskbar takes it as a string type
        alarmlist_dict = {}
        alarmlist_str=self.settings['alarmlist']
        settings['alarmlist']=[]
        if str(alarmlist_str) != '[]':
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
              settings['alarmlist'].append(alarmlist_dict)
              alarmlist_dict={}

        table = gtk.Table(4, 2, False)

        label = gtk.Label(_("Time :"))
        label.set_alignment(0, 0.5)
        self.time_format = gtk.Entry()
        self.time_format.set_width_chars(10)
        self.time_format.set_text(self.settings['time'])

        map = label.get_colormap()
        colour = map.alloc_color(self.settings['time_color'])
        self.time_color = gtk.ColorButton(colour)
        self.time_font = gtk.FontButton(self.settings['time_font'])

        table.attach(label, 0, 1, 0, 1)
        table.attach(self.time_format, 1, 2, 0, 1)
        table.attach(self.time_color, 2, 3, 0, 1)
        table.attach(self.time_font, 3, 4, 0, 1)

        label = gtk.Label(_("Date :"))
        label.set_alignment(0, 0.5)
        self.date_format = gtk.Entry()
        self.date_format.set_width_chars(10)
        self.date_format.set_text(self.settings['date'])

        colour = map.alloc_color(self.settings['date_color'])
        self.date_color = gtk.ColorButton(colour)
        self.date_font = gtk.FontButton(self.settings['date_font'])

        table.attach(label, 0, 1, 1, 2)
        table.attach(self.date_format, 1, 2, 1, 2)
        table.attach(self.date_color, 2, 3, 1, 2)
        table.attach(self.date_font, 3, 4, 1, 2)

        label = gtk.Label(_("Tooltip :"))
        label.set_alignment(0, 0.5)
        self.tooltip_format = gtk.Entry()
        self.tooltip_format.set_width_chars(10)
        self.tooltip_format.set_text(self.settings['tooltip'])

        table.attach(label, 0, 1, 2, 3)
        table.attach(self.tooltip_format, 1, 2, 2, 3)


        framebox.pack_start(table, True)

        text_timeformat = gtk.TextView()
        text_timeformat.set_wrap_mode(gtk.WRAP_WORD)
        text_timeformat.set_border_width(2)
        buffer = text_timeformat.get_buffer()
        buffer.set_text(INFO)
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.add(text_timeformat)

        expander = gtk.expander_new_with_mnemonic(_("_Info"))
        expander.add(sw)
        framebox.pack_start(expander, True)















        self.mouseover_checkbox = gtk.CheckButton(_('Show on mouseover'))
        self.mouseover_checkbox.set_active(int(conf.launcher[ind]['mouseover']))

        framebox.pack_end(self.mouseover_checkbox, False, False)

        bBox = gtk.VBox(False,0)
        bBox.set_spacing(10)
        bBox.set_border_width(4)

        BoxListControls = gtk.HBox(False,0)

        # ListStore
        self.view = View(self)
        self.view.connect("row-activated", self.edit_item)

        index = 0
        if settings['alarmlist'] != []:
          for alarm in settings['alarmlist']:
            date_d = alarm['date_d']
            date_m = alarm['date_m']
            date_y = alarm['date_y']
            time_h = alarm['time_h']
            time_m = alarm['time_m']
            day1 = alarm['day1']
            day2 = alarm['day2']
            day3 = alarm['day3']
            day4 = alarm['day4']
            day5 = alarm['day5']
            day6 = alarm['day6']
            day7 = alarm['day7']
            soundfile = alarm['soundfile']
            cmd = alarm['cmd']
            text = alarm['text']
            notify = alarm['notify']
            remind = alarm['remind']
            index = alarm['index']
            self.view.add_launcher(date_d, date_m, date_y, time_h, time_m, day1, day2, day3, day4, day5, day6, day7, soundfile, cmd, text, notify, remind, index)

        self.view.model.connect("row-deleted", self.view.row_deleted)

        scrolled = gtk.ScrolledWindow()
        scrolled.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolled.add(self.view)
        scrolled.set_size_request(550, 100)
        frame = gtk.Frame()
        frame.add(scrolled)

        ## Control buttons for list

        # Add Launcher
        button = core.image_button(_('add new task'), './images/conf/add_custom.png', 24)
        button.connect("clicked", self.new_item_custom)
        BoxListControls.pack_start(button, False, False)


        # Remove
        button = core.image_button(_('remove'), './images/conf/remove.png', 24)
        button.connect("clicked", self.remove_item)
        BoxListControls.pack_start(button, False, False)

        bBox.pack_start(BoxListControls, False, False)
        bBox.pack_start(frame, False, False)
        framebox.pack_start(bBox, False, False)










    def edit_item(self, view, path=None, view_column=None):
        selection = view.get_cursor()[0][0]
        if (selection is not None):
            model = view.get_model()
            Edit_Item(self, model, selection)
            self.check_state(model, selection)

            item    = model.get_iter(selection)

            index = model.get_value(item, ID_IND)

            for alarm in settings['alarmlist']:
              if alarm['index'] == index:
                 if str(alarm['date_d']) == '':
                   model.set_value(item, ID_date, '')
                   model.set_value(item, ID_days, str(alarm['day1'])+str(alarm['day2'])+str(alarm['day3'])+str(alarm['day4'])+str(alarm['day5'])+str(alarm['day6'])+str(alarm['day7']))
                 else:
                   model.set_value(item, ID_date, str(alarm['date_d'])+'-'+str(alarm['date_m'])+'-'+str(alarm['date_y']))
                   model.set_value(item, ID_days, '')

                 model.set_value(item, ID_time, str(alarm['time_h'])+':'+str(alarm['time_m']))
                 model.set_value(item, ID_text, str(alarm['text']))
                 model.set_value(item, ID_IND, alarm['index'])

    def new_item_custom(self, widget):
        index = str(int(time.time()))
        self.view.new_entry(index)
        selection = self.view.get_cursor()[0][0]
        model   = self.view.get_model()
        item    = model.get_iter(selection)
        self.edit_item(self.view)

    def remove_item(self, widget):
        self.view.remove_item()

    def check_state(self, model, selection):
        pass









    def save_change(self):
        self.conf.launcher[self.ind]['time'] = self.time_format.get_text()
        self.conf.launcher[self.ind]['time_color'] = gtk.color_selection_palette_to_string([self.time_color.get_color()])
        self.conf.launcher[self.ind]['time_font'] = self.time_font.get_font_name()
        self.conf.launcher[self.ind]['date'] = self.date_format.get_text()
        self.conf.launcher[self.ind]['date_color'] = gtk.color_selection_palette_to_string([self.date_color.get_color()])
        self.conf.launcher[self.ind]['date_font'] = self.date_font.get_font_name()
        self.conf.launcher[self.ind]['tooltip'] = self.tooltip_format.get_text()
        self.conf.launcher[self.ind]['mouseover'] = int(self.mouseover_checkbox.get_active())

        str_cfg = '['
        for elem in settings['alarmlist']:
            if elem.__class__ == dict:
                if not elem == {}:
                    str_cfg += '{'
                    for item in elem:
                        str_cfg += '\'%s\': \'%s\', ' % (item, elem[item])
                    str_cfg = str_cfg[:-2]
                    str_cfg += '}, '
                else:
                    str_cfg += '\'%s\', ' % (elem)
        if not settings['alarmlist'] == []:
          str_cfg = str_cfg[:-2]
        str_cfg += ']'

        self.conf.launcher[self.ind]['alarmlist'] = str_cfg
        self.conf.plg_mgr.plugins[self.ind].restart()






class View(gtk.TreeView):

    def __init__(self, conf):
        gtk.TreeView.__init__(self)
        self.conf = conf
        self.set_headers_visible(False)
        self.set_reorderable(True)
        self.get_selection().set_mode(gtk.SELECTION_SINGLE)

#        self.columns_autosize()

        self.model = gtk.ListStore(
            gobject.TYPE_STRING,    # date
            gobject.TYPE_STRING,    # time
            gobject.TYPE_STRING,    # days
            gobject.TYPE_STRING,    # text
            gobject.TYPE_STRING,    # index
            )

        self.filtremodele = self.model.filter_new()
        self.set_model(self.model)

        cell_text = gtk.CellRendererText()
        col_text = gtk.TreeViewColumn(None, cell_text, text=ID_date)
        self.append_column(col_text)

        cell_text = gtk.CellRendererText()
        col_text = gtk.TreeViewColumn(None, cell_text, text=ID_time)
        self.append_column(col_text)

        cell_text = gtk.CellRendererText()
        col_text = gtk.TreeViewColumn(None, cell_text, text=ID_days)
        self.append_column(col_text)

        cell_text = gtk.CellRendererText()
        col_text = gtk.TreeViewColumn(None, cell_text, text=ID_text)
        self.append_column(col_text)

        cell_command = gtk.CellRendererText()
        col_command = gtk.TreeViewColumn(None, cell_command, text=ID_IND)
        col_command.set_visible(False)
        self.append_column(col_command)

    def remove_item(self):
        try:
            pos = self.get_cursor()[0][0]
            if pos is None: # no selection
                return

            model = self.get_model()
            index = model.get_value(model.get_iter(pos), ID_IND)

            try:
                for alarm in settings['alarmlist']:
                  if alarm['index'] == index:
                     settings['alarmlist'].remove(alarm)
            except:
                pass

            model.remove(model.get_iter(pos))

            if pos < 0:
                pos = 0
            # Set the focus and cursor correctly
            self.set_cursor(pos);
            self.grab_focus()

        except TypeError:
            pass
#            print( "> nothing to delete !?" )



    def add_launcher(self, date_d, date_m, date_y, time_h, time_m, day1, day2, day3, day4, day5, day6, day7, soundfile, cmd, text, notify, remind, index):
        model = self.get_model()
        item = model.append(None)

        if str(date_d) == '':
          model.set_value(item, ID_date, '')
          model.set_value(item, ID_days, str(day1)+str(day2)+str(day3)+str(day4)+str(day5)+str(day6)+str(day7))
        else:
          model.set_value(item, ID_date, str(date_d)+'-'+str(date_m)+'-'+str(date_y))
          model.set_value(item, ID_days, '')

        model.set_value(item, ID_time, str(time_h)+':'+str(time_m))
        model.set_value(item, ID_text, str(text))
        model.set_value(item, ID_IND, index)




    def new_entry(self, index):
        self.grab_focus()
        model = self.get_model()
        position = None

        try:
            position = self.get_cursor()[0][0]
            try:
                iter = model.get_iter(position)
            except ValueError:
#                print("> Empty list ?")
                iter = model.get_iter()

            item = model.insert_after(iter)

        except TypeError:
            #~ print "Error while adding new entry .."
            item = model.append(None)
            self.grab_focus()

        ## set default value for new entry
        now = time.localtime()
        model.set_value(item, ID_date, str(time.strftime('%d', now))+'-'+str(time.strftime('%m', now))+'-'+str(time.strftime('%Y', now)))
        model.set_value(item, ID_time, str(time.strftime('%H', now))+':'+str(time.strftime('%M', now)))
        model.set_value(item, ID_days, '')
        model.set_value(item, ID_text, _('Text new task'))
        model.set_value(item, ID_IND, index)

        # add to list

        ## Set focus to new entry
        if position is not None:
            path = model.get_path(model.get_iter(position+1))
        else:
            position = self.get_cursor()[0][0]
            path = model.get_path(model.get_iter(position))
        self.set_cursor(path)

        settings['alarmlist'].insert(int(position)+1, {'date_d':str(time.strftime('%d', now)), 'date_m':str(time.strftime('%m', now)), 'date_y':str(time.strftime('%Y', now)), \
        'time_h':str(time.strftime('%H', now)), 'time_m':str(time.strftime('%M', now)), \
        'day1':'', 'day2':'', 'day3':'', 'day4':'', 'day5':'', 'day6':'', 'day7':'', \
        'soundfile':'', 'cmd':'', 'text':_('Text new task'), 'notify':'1', 'remind':'1', 'index':index})

    def row_deleted(self, treemodel, path):
        pass

    def row_inserted(self, treemodel, path, iter):
        pass




































class Edit_Item:

    def __init__(self, conf, model, selection):
        self.conf = conf
        self.model = model
        self.selection = selection
        parent = None

        index = model.get_value(model.get_iter(selection), ID_IND)
        for alarm in settings['alarmlist']:
            if alarm['index'] == index:
                 date_d = alarm['date_d']
                 date_m = alarm['date_m']
                 date_y = alarm['date_y']
                 time_h = alarm['time_h']
                 time_m = alarm['time_m']
                 day1 = alarm['day1']
                 day2 = alarm['day2']
                 day3 = alarm['day3']
                 day4 = alarm['day4']
                 day5 = alarm['day5']
                 day6 = alarm['day6']
                 day7 = alarm['day7']
                 soundfile = alarm['soundfile']
                 cmd = alarm['cmd']
                 text = alarm['text']
                 notify = alarm['notify']
                 remind = alarm['remind']
                 index = alarm['index']

        self.typealarm = 'by_date'
        if date_d == '':
           now = time.localtime()
           date_d = str(time.strftime('%d', now))
           date_m = str(time.strftime('%m', now))
           date_y = str(time.strftime('%Y', now))
           self.typealarm = 'by_weekdays'

        # Create window
        self.window = gtk.Dialog(_("Edit"), parent, gtk.DIALOG_MODAL, buttons=None)
        self.window.set_position(gtk.WIN_POS_CENTER)

        frame_settings = gtk.Frame()
        frame_settings.set_border_width(5)

        box_settings = gtk.VBox(False, 0)
        box_settings.set_border_width(5)
        box_settings.set_spacing(10)
        frame_settings.add(box_settings)

        optionbox2 = gtk.HBox(False, 0)
        optionbox2.set_border_width(0)
        optionbox2.set_spacing(10)

        button1 = gtk.RadioButton(None, _("by date"))
        button1.connect("toggled", self.callback, self.typealarm)
        optionbox2.pack_start(button1, gtk.TRUE, gtk.TRUE, 0)
        button1.show()
        button2 = gtk.RadioButton(button1, _("by weekdays"))
        optionbox2.pack_start(button2, gtk.TRUE, gtk.TRUE, 0)
        button2.show()




        optionbox3 = gtk.HBox(False, 0)
        optionbox3.set_border_width(0)
        optionbox3.set_spacing(10)


        adjustment = gtk.Adjustment(value=int(date_d), lower=1, upper=31, step_incr=1, page_incr=1, page_size=0)
        self.date_d = gtk.SpinButton(adjustment=adjustment, climb_rate=0, digits=0)
        optionbox3.pack_start(self.date_d, False, False)
        adjustment = gtk.Adjustment(value=int(date_m), lower=1, upper=12, step_incr=1, page_incr=1, page_size=0)
        self.date_m = gtk.SpinButton(adjustment=adjustment, climb_rate=0, digits=0)
        optionbox3.pack_start(self.date_m, False, False)
        adjustment = gtk.Adjustment(value=int(date_y), lower=2011, upper=2100, step_incr=1, page_incr=1, page_size=0)
        self.date_y = gtk.SpinButton(adjustment=adjustment, climb_rate=0, digits=0)
        optionbox3.pack_start(self.date_y, False, False)
        adjustment = gtk.Adjustment(value=int(time_h), lower=0, upper=23, step_incr=1, page_incr=1, page_size=0)
        self.time_h = gtk.SpinButton(adjustment=adjustment, climb_rate=0, digits=0)
        optionbox3.pack_start(self.time_h, False, False)
        adjustment = gtk.Adjustment(value=int(time_m), lower=0, upper=59, step_incr=1, page_incr=1, page_size=0)
        self.time_m = gtk.SpinButton(adjustment=adjustment, climb_rate=0, digits=0)
        optionbox3.pack_start(self.time_m, False, False)


        if day1 == '':
           day1 = 1
        if day2 == '':
           day2 = 1
        if day3 == '':
           day3 = 1
        if day4 == '':
           day4 = 1
        if day5 == '':
           day5 = 1
        if day6 == '':
           day6 = 1
        if day7 == '':
           day7 = 1

        self.day1 = gtk.CheckButton(_('M'))
        self.day1.set_active(int(day1))
        self.day1.set_sensitive(False)
        optionbox3.pack_start(self.day1, False, False)
        self.day2 = gtk.CheckButton(_('T'))
        self.day2.set_active(int(day2))
        self.day2.set_sensitive(False)
        optionbox3.pack_start(self.day2, False, False)
        self.day3 = gtk.CheckButton(_('W'))
        self.day3.set_active(int(day3))
        self.day3.set_sensitive(False)
        optionbox3.pack_start(self.day3, False, False)
        self.day4 = gtk.CheckButton(_('Th'))
        self.day4.set_active(int(day4))
        self.day4.set_sensitive(False)
        optionbox3.pack_start(self.day4, False, False)
        self.day5 = gtk.CheckButton(_('F'))
        self.day5.set_active(int(day5))
        self.day5.set_sensitive(False)
        optionbox3.pack_start(self.day5, False, False)
        self.day6 = gtk.CheckButton(_('S'))
        self.day6.set_active(int(day6))
        self.day6.set_sensitive(False)
        optionbox3.pack_start(self.day6, False, False)
        self.day7 = gtk.CheckButton(_('Su'))
        self.day7.set_active(int(day7))
        self.day7.set_sensitive(False)
        optionbox3.pack_start(self.day7, False, False)

        self.textlabel = gtk.Label(_("Text:"))
        self.textlabel.set_alignment(0, 0.5)
        self.text = gtk.Entry()
        self.text.set_width_chars(55)
        self.text.set_text(text)


        self.soundlabel = gtk.Label(_("Sound file :"))
        self.soundlabel.set_alignment(0, 0.5)
        self.soundfile = gtk.Entry()
        soundfile = soundfile.replace("\\\"", "\"")
        self.soundfile.set_width_chars(55)
        self.soundfile.set_text(soundfile)

        self.cmdlabel = gtk.Label(_("Command:"))
        self.cmdlabel.set_alignment(0, 0.5)
        self.cmd = gtk.Entry()
        cmd = cmd.replace("\\\"", "\"")
        self.cmd.set_width_chars(55)
        self.cmd.set_text(cmd)

        self.index = gtk.Entry()
        self.index.set_text(index)

        self.notify = gtk.CheckButton(_('Show notify with text task'))
        self.notify.set_active(int(notify))

        self.remind = gtk.CheckButton(_('Show notify for 5 minutes before event'))
        self.remind.set_active(int(remind))

        self.sound_command = gtk.Button("...")
        self.sound_command.connect("clicked", self.button_sound_clicked)

        self.button_command = gtk.Button("...")
        self.button_command.connect("clicked", self.button_command_clicked)

        #Table container inside frame
        table = gtk.Table()
        table.attach(self.textlabel, 0,1,0,1)
        table.attach(self.text,1,2,0,1)

        table.attach(self.soundlabel, 0,1,1,2)
        table.attach(self.soundfile,1,2,1,2)
        table.attach(self.sound_command,2,3,1,2, gtk.SHRINK, gtk.SHRINK)

        table.attach(self.cmdlabel, 0,1,2,3)
        table.attach(self.cmd,1,2,2,3)
        table.attach(self.button_command,2,3,2,3, gtk.SHRINK, gtk.SHRINK)



        box_settings.pack_start(optionbox2, False, False)
        box_settings.pack_start(optionbox3, False, False)
        box_settings.pack_end(self.remind, False, False)
        box_settings.pack_end(self.notify, False, False)
        box_settings.pack_end(table, False, False)
        self.window.vbox.pack_start(frame_settings, False, False)

        #self.window.set_default_size(500, 400)

        ## Controls
        bouton = gtk.Button(stock=gtk.STOCK_CANCEL)
        bouton.connect("clicked", self.close)
        self.window.action_area.pack_start(bouton, True, True, 0)
        bouton.show()

        bouton = gtk.Button(stock=gtk.STOCK_OK)
        bouton.connect("clicked", self.change_item)
        self.window.action_area.pack_start(bouton, True, True, 0)
        bouton.show()

        if self.typealarm == 'by_weekdays':
          button2.set_active(gtk.TRUE)

        #Show main window frame and all content
        self.window.show_all()
        self.window.run()



    def callback(self, widget, data=None):
        self.typealarm=("by_weekdays", "by_date")[widget.get_active()]
        if self.typealarm == 'by_date':
          self.date_d.set_sensitive(True)
          self.date_m.set_sensitive(True)
          self.date_y.set_sensitive(True)
          self.day1.set_sensitive(False)
          self.day2.set_sensitive(False)
          self.day3.set_sensitive(False)
          self.day4.set_sensitive(False)
          self.day5.set_sensitive(False)
          self.day6.set_sensitive(False)
          self.day7.set_sensitive(False)
        else:
          self.date_d.set_sensitive(False)
          self.date_m.set_sensitive(False)
          self.date_y.set_sensitive(False)
          self.day1.set_sensitive(True)
          self.day2.set_sensitive(True)
          self.day3.set_sensitive(True)
          self.day4.set_sensitive(True)
          self.day5.set_sensitive(True)
          self.day6.set_sensitive(True)
          self.day7.set_sensitive(True)

    def change_item(self, data):
        index = self.index.get_text()

        for alarm in settings['alarmlist']:
            if alarm['index'] == index:
               if self.typealarm == 'by_weekdays':
                 alarm['date_d'] = ''
                 alarm['date_m'] = ''
                 alarm['date_y'] = ''
                 alarm['day1'] = str(int(self.day1.get_active()))
                 alarm['day2'] = str(int(self.day2.get_active()))
                 alarm['day3'] = str(int(self.day3.get_active()))
                 alarm['day4'] = str(int(self.day4.get_active()))
                 alarm['day5'] = str(int(self.day5.get_active()))
                 alarm['day6'] = str(int(self.day6.get_active()))
                 alarm['day7'] = str(int(self.day7.get_active()))
               else:
                 if int(self.date_d.get_value()) < 10:
                   alarm['date_d'] = '0'+str(int(self.date_d.get_value()))
                 else:
                   alarm['date_d'] = str(int(self.date_d.get_value()))
                 if int(self.date_m.get_value()) < 10:
                   alarm['date_m'] = '0'+str(int(self.date_m.get_value()))
                 else:
                   alarm['date_m'] = str(int(self.date_m.get_value()))
                 alarm['date_y'] = str(int(self.date_y.get_value()))
                 alarm['day1'] = ''
                 alarm['day2'] = ''
                 alarm['day3'] = ''
                 alarm['day4'] = ''
                 alarm['day5'] = ''
                 alarm['day6'] = ''
                 alarm['day7'] = ''
               if int(self.time_h.get_value()) < 10:
                 alarm['time_h'] = '0'+str(int(self.time_h.get_value()))
               else:
                 alarm['time_h'] = str(int(self.time_h.get_value()))
               if int(self.time_m.get_value()) < 10:
                 alarm['time_m'] = '0'+str(int(self.time_m.get_value()))
               else:
                 alarm['time_m'] = str(int(self.time_m.get_value()))
               alarm['soundfile'] = self.soundfile.get_text()
               alarm['cmd'] = self.cmd.get_text()
               alarm['text'] = self.text.get_text()
               alarm['notify'] = str(int(self.notify.get_active()))
               alarm['remind'] = str(int(self.remind.get_active()))
               alarm['index'] = self.index.get_text()

        self.close()

    def close(self, widget=None, event=None):
        self.window.hide()
        self.window.destroy()

    def button_sound_clicked(self, widget):
        dialog = gtk.FileChooserDialog(_("Select sound file.."),
                                        None,
                                        gtk.FILE_CHOOSER_ACTION_OPEN,
                                        (gtk.STOCK_CANCEL,
                                        gtk.RESPONSE_CANCEL,
                                        gtk.STOCK_OPEN,
                                        gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)

        filter = gtk.FileFilter()
        filter.set_name(_("Sounds"))
        filter.add_mime_type("image/wav")
        filter.add_mime_type("image/mp3")
        filter.add_mime_type("image/ogg")
        filter.add_pattern("*.wav")
        filter.add_pattern("*.mp3")
        filter.add_pattern("*.ogg")
        dialog.add_filter(filter)
        filter = gtk.FileFilter()
        filter.set_name(_("All files"))
        filter.add_pattern("*")
        dialog.add_filter(filter)

        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            self.soundfile.set_text(dialog.get_filename())
        dialog.destroy()



    def button_command_clicked(self, widget):
        dialog = gtk.FileChooserDialog(_("Select command.."),
                                        None,
                                        gtk.FILE_CHOOSER_ACTION_OPEN,
                                        (gtk.STOCK_CANCEL,
                                        gtk.RESPONSE_CANCEL,
                                        gtk.STOCK_OPEN,
                                        gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)

        filter = gtk.FileFilter()
        filter.set_name(_("All files"))
        filter.add_pattern("*")
        dialog.add_filter(filter)

        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            self.cmd.set_text(dialog.get_filename())
        dialog.destroy()
