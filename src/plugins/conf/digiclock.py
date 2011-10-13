# -*- coding: utf-8 -*-

import gtk

settings = {
    'line1':'%H:%M', 'line1_color':'#EEEEEE', 'line1_font':'Sans Bold 12',
    'line2':'%d/%m', 'line2_color':'#B5B5B5', 'line2_font':'Sans Bold 8',
    }

INFO = """%a  Locale’s abbreviated weekday name.
%A  Locale’s full weekday name.
%b  Locale’s abbreviated month name.
%B  Locale’s full month name.
%c  Locale’s appropriate date and time representation.
%d  Day of the month as a decimal number [01,31].
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

        for key in settings:
            if not key in conf.launcher[ind]:
                conf.launcher[ind][key] = settings[key]

        self.settings = conf.launcher[ind]

        table = gtk.Table(4, 2, False)

        label = gtk.Label("Line 1 :")
        label.set_alignment(0, 0.5)
        self.line1_format = gtk.Entry()
        self.line1_format.set_width_chars(10)
        self.line1_format.set_text(self.settings['line1'])

        map = label.get_colormap()
        colour = map.alloc_color(self.settings['line1_color'])
        self.line1_color = gtk.ColorButton(colour)
        self.line1_font = gtk.FontButton(self.settings['line1_font'])

        table.attach(label, 0, 1, 0, 1)
        table.attach(self.line1_format, 1, 2, 0, 1)
        table.attach(self.line1_color, 2, 3, 0, 1)
        table.attach(self.line1_font, 3, 4, 0, 1)

        label = gtk.Label("Line 2 :")
        label.set_alignment(0, 0.5)
        self.line2_format = gtk.Entry()
        self.line2_format.set_width_chars(10)
        self.line2_format.set_text(self.settings['line2'])

        colour = map.alloc_color(self.settings['line2_color'])
        self.line2_color = gtk.ColorButton(colour)
        self.line2_font = gtk.FontButton(self.settings['line2_font'])

        table.attach(label, 0, 1, 1, 2)
        table.attach(self.line2_format, 1, 2, 1, 2)
        table.attach(self.line2_color, 2, 3, 1, 2)
        table.attach(self.line2_font, 3, 4, 1, 2)

        text_line1format = gtk.TextView()
        text_line1format.set_wrap_mode(gtk.WRAP_WORD)
        text_line1format.set_border_width(2)
        
        txt_buffer = text_line1format.get_buffer()
        txt_buffer.set_text(INFO)
        
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.add(text_line1format)

        expander = gtk.expander_new_with_mnemonic("_Info")
        expander.add(sw)

        box.pack_start(table, False, False)
        box.pack_start(expander, True, True)

    def save_change(self):
        self.conf.launcher[self.ind]['line1'] = self.line1_format.get_text()
        self.conf.launcher[self.ind]['line1_color'] = gtk.color_selection_palette_to_string([self.line1_color.get_color()])
        self.conf.launcher[self.ind]['line1_font'] = self.line1_font.get_font_name()
        self.conf.launcher[self.ind]['line2'] = self.line2_format.get_text()
        self.conf.launcher[self.ind]['line2_color'] = gtk.color_selection_palette_to_string([self.line2_color.get_color()])
        self.conf.launcher[self.ind]['line2_font'] = self.line2_font.get_font_name()
        self.conf.plg_mgr.plugins[self.ind].restart()
