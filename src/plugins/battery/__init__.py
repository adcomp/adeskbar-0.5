# -*- coding: utf-8 -*-
#
# ADeskBar - "Battery" plugin
#
##

import gtk
import gobject
import os
import re

import adesk.plugin as Plg
import adesk.core as Core
import adesk.ui as UI

try:
    import power
except:
    Core.logINFO('Plugin "battery" needs python-power => 1.5')
    Core.logINFO(' -- github: https://github.com/oskarirauta/Power')

class Plugin(Plg.Plugin):
    def __init__(self, bar, settings):
        Plg.Plugin.__init__(self, bar, settings)

        self.can_zoom = True
        self.battery = Battery(self, bar)

    def onClick(self, widget, event):
        self.battery.update_status()
        self.battery.toggle()

    def resize(self):
        self.set_size_request(self.cfg['icon_size'], self.cfg['icon_size'])

class Battery(UI.PopupWindow):
    def __init__(self, plugin, bar):
        UI.PopupWindow.__init__(self, bar, plugin)
        self.power = power.PowerManagement()
        self.firstAttempt = True

        box = gtk.HBox(False, 4)
        box.set_border_width(2)
        self.add(box)
        self.label = gtk.Label()
        self.label.set_use_markup(True)
        self.label.set_markup('no battery ..')
        box.pack_start(self.label)
        box.show_all()

        gobject.timeout_add(4000, self.initial_update_status)
        gobject.timeout_add(60000, self.update_status)

    def update_icon_status(self, icon):
        self.plugin.set_icon('images/plugins/battery/' + icon + '.svg')

    def initial_update_status(self):
        self.update_status()
        return False
        
    def update_status(self):
        # batteries = get_batts()
        power_status, time_remaining, capacity = self.power.get_ac_status()
        error_encountered = False
        tooltip_txt = 'On AC'
        label_txt = 'AC only'
        time_remaining_str = 'Unlimited'

        if capacity < 5:
            icon = 'notification-battery-000'
        elif capacity <= 15:
            icon = 'notification-battery-010'
        elif capacity <= 25:
            icon = 'notification-battery-020'
        elif capacity <= 35:
            icon = 'notification-battery-030'
        elif capacity <= 45:
            icon = 'notification-battery-040'
        elif capacity <= 55:
            icon = 'notification-battery-050'
        elif capacity <= 65:
            icon = 'notification-battery-060'
        elif capacity <= 75:
            icon = 'notification-battery-070'
        elif capacity <= 85:
            icon = 'notification-battery-080'
        elif capacity <= 95:
            icon = 'notification-battery-090'
        else:
            icon = 'notification-battery-100'
        
        if time_remaining >= 0:
            offset_h, offset_m = divmod(int(time_remaining), 60)
            time_delimeter = ':'
            time_remaining_str = '{:02d}{}{:02d}'.format(abs(offset_h), time_delimeter, offset_m)
        elif time_remaining == -1.0:
            time_remaining_str = 'Unknown'
            error_encountered = True
        
        if power_status == 1:
            icon = 'notification-on-ac'
            tooltip_txt = 'On AC'
            label_txt = 'AC only'
        elif power_status == 2:
            icon += '-plugged'
            tooltip_txt = str(int(capacity)) + '%'
            label_txt = 'Charge: <b>' + str(int(capacity)) + '%</b>'
            label_txt += '\nTime remaining until charged: <b>' + time_remaining_str + '</b>'
        elif power_status == 3:
            tooltip_txt = str(capacity) + '%'
            label_txt = 'Charge: <b>' + str(int(capacity)) + '%</b>'
            label_txt += '\nTime remaining until empty: <b>' + time_remaining_str + '</b>'
        elif power_status == 4:
            icon = 'notification-battery-100-plugged'
            tooltip_txt = 'Full'
            label_txt = 'Battery is <b>full</b>.'
            label_txt += '\nTime remaining until empty: <b>' + time_remaining_str + '</b>'
        elif power_status == 5:
            icon = 'notification-on-ac'
            tooltip_txt = 'Full, on AC'
            label_txt = 'Battery is <b>full</b> and AC is plugged.'
        else:
            error_encountered = True

        if not error_encountered:
            self.update_icon_status(icon)
            self.plugin.tooltip = tooltip_txt
            self.label.set_markup(label_txt)
        elif error_encountered and self.firstAttempt:
            icon = 'notification-on-ac'
            tooltip_txt = 'On AC'
            label_txt = 'AC only'
            self.update_icon_status(icon)
            self.plugin.tooltip = tooltip_txt
            self.label.set_markup(label_txt)

        self.firstAttempt = False
        return True
