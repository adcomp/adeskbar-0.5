# -*- coding: utf-8 -*-

import gtk
import gobject
import os
import re

import adesk.plugin as Plg
import adesk.core as Core
import adesk.ui as UI

class Plugin(Plg.Plugin):
    def __init__(self, bar, settings):
        Plg.Plugin.__init__(self, bar, settings)
        self.settings = settings
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
        self.bar = bar
        self.plugin = plugin

        box = gtk.HBox(False, 4)
        box.set_border_width(2)
        self.add(box)
        self.label = gtk.Label()
        self.label.set_use_markup(True)
        self.label.set_markup('no battery ..')
        box.pack_start(self.label)
        box.show_all()

        gobject.timeout_add(60000, self.update_status)

    def update_icon_status(self, icon):
        self.plugin.set_icon('images/plugins/battery/' + icon + '.svg')

    def update_status(self):
        batteries = get_batts()

        if not batteries:
            self.update_icon_status('notification-battery-000')
            self.plugin.tooltip = "no battery"
            self.label.set_markup("no battery")
            return False
        else:
            for battery in batteries:
                percent_left, charging_state, time_remaining = get_info(battery)
                percent_left = float(percent_left)

            if percent_left < 5:
                icon = 'notification-battery-000'
            elif percent_left <= 15:
                icon = 'notification-battery-010'
            elif percent_left <= 25:
                icon = 'notification-battery-020'
            elif percent_left <= 35:
                icon = 'notification-battery-030'
            elif percent_left <= 45:
                icon = 'notification-battery-040'
            elif percent_left <= 55:
                icon = 'notification-battery-050'
            elif percent_left <= 65:
                icon = 'notification-battery-060'
            elif percent_left <= 75:
                icon = 'notification-battery-070'
            elif percent_left <= 85:
                icon = 'notification-battery-080'
            elif percent_left <= 95:
                icon = 'notification-battery-090'
            else:
                icon = 'notification-battery-100'

            if charging_state=="charging":
                icon += '-plugged'

            self.update_icon_status(icon)
            self.plugin.tooltip = str(percent_left) + " %"

            temp = "Charge : <b>" + str(int(percent_left)) + " %</b>"
            if charging_state == 'discharging':
                temp += "\n\nTime Left : <b>" + time_remaining + "</b>"
            else:
                temp += "\n\nTime Left : <b>--:--</b>"
            self.label.set_markup(temp)
        return True

batt_basedir = "/proc/acpi/battery"

def get_batts():
    """ return an array of all available batteries in batt_basedir """
    try:
        return os.listdir(batt_basedir)
    except Exception, e:
        print "Unable to find a battery in '"+batt_basedir+"'"
        return None

def read_lines(file):
    """ read file contents and return readlines() """
    try:
        f = open(file)
        string = f.readlines()
        f.close()
        return string
    except Exception, e:
        print "Unable to open '"+file+"':\n" +str(e)
        return None

def get_value(contents, property):
    """ return value of property from file contents (readlines) """
    for c in contents:
        if property in c:
            try:
                return c.split(':')[1].strip()
            except IndexError, e:
                print "Unable to parse file contents: "+str(e)
                return None
    return None

def batt_percent(capacity, remaining_capacity):
    """ calculate and return remaining battery percentage as a string """
    # strip out units
    try:
        capacity = float(re.sub('\D', '', capacity))
        remaining_capacity = float(re.sub('\D', '', remaining_capacity))
    except:
        # must be 'unknown' values, i.e. a bad battery return N/A
        #~ print 'N/A'
        return 'N/A'
    # convert to float and calculate
    percent = float((remaining_capacity * 100) / capacity)
    # round to hundredths. 23.3524 || 23.3245 -> 23.35999 || 23.35000 + 0.001 = 23.360 || 23.351
    percent = round(percent, 2) + 0.001
    percent = str(percent)
    # remove extra thousandths place from rounding
    percent = percent[:(len(percent)-1)]
    #~ print percent
    return percent

def time_left(remaining_capacity, present_rate):
    """ calculate and return remaining time in 00:00 hours units """
    # strip units
    try:
        remaining_capacity = float(re.sub('\D', '', remaining_capacity))
        present_rate = float(re.sub('\D', '', present_rate))
    except:
        return 'N/A'
    # get decimal time i.e. 1.34 hours
    #~ print remaining_capacity, present_rate

    decimal_time = remaining_capacity / present_rate
    # round to hundreths (see batt_percent() for more info)
    decimal_time = round(decimal_time, 2) + 0.001
    decimal_time = str(decimal_time)
    decimal_time = decimal_time[:(len(decimal_time)-1)]
    # split to the left and right of the decimal and convert the right (hundredths) to minutes
    whole = decimal_time.split('.')[0]
    # pad <num> to 0<num>
    if len(whole) == 1: whole = '0'+whole
    hundredths = decimal_time.split('.')[1]
    # convert hundredths place to minutes
    minutes = (int(hundredths) * 60) / 100
    minutes = str(minutes)
    if len(minutes) == 1: minutes = '0'+minutes
    return whole+':'+minutes

def capacity_deviation(capacity, design_capacity):
    """ calculate and return the gain or loss of capacity based on spec and last charge """
    try:
        int_capacity = int(re.sub('\D', '', capacity))
        int_design_capacity = int(re.sub('\D', '', design_capacity))
        if int_capacity > int_design_capacity:
            diff = int_capacity - int_design_capacity
            diff = str(diff)
            return '+'+batt_percent(capacity, diff)
        elif int_capacity < int_design_capacity:
            diff = int_design_capacity - int_capacity
            diff = str(diff)
            return '-'+batt_percent(design_capacity, diff)
        else: return '0.00'
    except:
        return 'N/A'

def get_info(battery):
    batt_dir = os.path.join(batt_basedir, battery)

    # info data
    info_file = os.path.join(batt_dir, 'info')
    info_contents = read_lines(info_file)
    if not info_contents: return

    # state data
    state_file = os.path.join(batt_dir, 'state')
    state_contents = read_lines(state_file)
    if not state_contents: return

    charging_state          = get_value(state_contents, 'charging state')
    remaining_capacity      = get_value(state_contents, 'remaining capacity')
    present_rate            = get_value(state_contents, 'present rate')
    capacity_low            = get_value(info_contents, 'design capacity low')
    capacity_warning        = get_value(info_contents, 'design capacity warning')
    #~ manufacturer            = get_value(info_contents, 'OEM info')
    #~ model_number            = get_value(info_contents, 'model number')
    #~ battery_type            = get_value(info_contents, 'battery type')
    #~ battery_tech            = get_value(info_contents, 'battery technology')
    design_capacity         = get_value(info_contents, 'design capacity')
    last_full_capacity      = get_value(info_contents, 'last full capacity')

    #~ print charging_state
    #~ print remaining_capacity
    #~ print present_rate
    #~ print capacity_low
    #~ print capacity_warning
    #~ print manufacturer
    #~ print model_number
    #~ print battery_type
    #~ print battery_tech
    #~ print design_capacity
    #~ print last_full_capacity


    if last_full_capacity != '':
        capacity = last_full_capacity
    else:
        capacity = design_capacity

    # calculate percent left on battery
    percent_left = batt_percent(capacity, remaining_capacity)

    # calculate capacity gain or loss
    capacity_dev = capacity_deviation(capacity, design_capacity)

    # determine time remaining based on charging state
    if charging_state == 'discharging':
        # time left to discharge
        time_remaining = time_left(remaining_capacity, present_rate)
    elif charging_state == 'charging':
        # time left to charge
        # use the difference between total capacity and remaining capacity
        try:
            remaining = int(re.sub('\D', '', remaining_capacity))
            capy = int(re.sub('\D', '', capacity))
            net = capy - remaining
            net = str(net)
            time_remaining = time_left(net, present_rate)
        except:
            time_remaining = 'N/A'
    else:
        # must be charged: nothing to calculate; ACPWR
        time_remaining = "--:--"

    # determine alert status
    try:
        if int(re.sub('\D', '', remaining_capacity)) <= int(re.sub('\D', '', capacity_low)): alert = 'LOW!'
        elif int(re.sub('\D', '', remaining_capacity)) <= int(re.sub('\D', '', capacity_warning)): alert = 'WARNING!'
        else: alert = 'ok'
    except:
        alert = 'N/A'

    # manufacturer, model number and battery technology may not have values; use N/A for screen output
    #if not manufacturer: manufacturer = 'N/A'
    #if not model_number: model_number = 'N/A'
    #if not battery_tech: batter_tech = 'N/A'

    # don't display anything larger than 100.00%
    try:
        if float(percent_left) > 100.00: percent_left = '100.00'
    except:
        pass

    # output 100.00% if we have a 'charged' state
    if charging_state == 'charged': percent_left = '100.00'

    # output to screen
    #~ print "         << "+battery+" >>"
    #~ #print manufacturer+' - '+model_number+' | '+battery_type+' | '+battery_tech
    #~ print "Remaining Charge           : "+percent_left+" %"
    #~ print "Time Left                  : "+time_remaining+' Hrs'
    #~ print "Charging State             : "+charging_state
    #~ #print "Rated Capacity Deviation   : "+capacity_dev+" %"
    #~ print "Charge Alert               : "+alert

    return percent_left, charging_state, time_remaining
