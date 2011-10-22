import gtk

import adesk.core as Core

settings = {
    'lockscreen':'xscreensaver-command -lock',
    'logout':'openbox --exit',
    'hibernate':'',
    'suspend':'',
    'reboot':'dbus-send --system --print-reply --dest="org.freedesktop.Hal" /org/freedesktop/Hal/devices/computer org.freedesktop.Hal.Device.SystemPowerManagement.Reboot',
    'shutdown':'dbus-send --system --print-reply --dest="org.freedesktop.Hal" /org/freedesktop/Hal/devices/computer org.freedesktop.Hal.Device.SystemPowerManagement.Shutdown',
    'show_label':True,
    'icon_size':32,
    }

class config():
    def __init__(self, box, conf, ind):

        self.conf = conf
        self.ind = ind

        for key in settings:
            if not key in conf.launcher[ind]:
                conf.launcher[ind][key] = settings[key]

        optionbox = gtk.HBox(False, 0)
        optionbox.set_border_width(0)
        optionbox.set_spacing(10)

        self.show_label_checkbox = gtk.CheckButton('Show label')
        self.show_label_checkbox.set_active(conf.launcher[ind]['show_label'])

        adjustment = gtk.Adjustment(value=conf.launcher[ind]['icon_size'], lower=16, upper=128, step_incr=1, page_incr=8, page_size=0)
        self.icon_size = gtk.SpinButton(adjustment=adjustment, climb_rate=0.0, digits=0)
        self.icon_size.set_tooltip_text('icon size in pixel')
        
        label = gtk.Label('icon size')
        
        optionbox.pack_start(self.show_label_checkbox, False, False)
        optionbox.pack_end(self.icon_size, False, False)
        optionbox.pack_end(label, False, False)

        table = gtk.Table()
        ligne = 0
        
        cmd = {'lockscreen':('Lock screen', 'system-lock-screen'),
               'logout':('Log out', 'gnome-session-logout'),
               'hibernate':('Hibernate', 'gnome-session-hibernate'),
               'suspend':('Suspend', 'gnome-session-suspend'),
               'reboot':('Reboot', 'gnome-session-reboot'),
               'shutdown':('Shutdown', 'gnome-session-halt')
               }
               
        self.widget_cmd = {}

        for key in ('lockscreen', 'logout', 'reboot', 'shutdown', 'hibernate', 'suspend'):

            label = gtk.Label(cmd[key][0])
            label.set_alignment(0, 1)

            self.widget_cmd[key] = gtk.Entry()
            self.widget_cmd[key].set_width_chars(45)
            self.widget_cmd[key].set_text(conf.launcher[ind][key])

            table.attach(label, 0, 1, ligne, ligne +1)
            ligne += 1
            table.attach(self.widget_cmd[key], 0, 1, ligne, ligne +1)
            ligne += 1

        table.set_col_spacings(4)
        table.set_row_spacings(4)
        table.set_border_width(4)
        table.set_homogeneous(False)
        
        scrolled = gtk.ScrolledWindow()
        scrolled.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scrolled.add_with_viewport(table)

        box.pack_start(optionbox, False, False)
        #~ box.pack_start(gtk.HSeparator(), False, False)
        box.pack_start(scrolled, True, True)

    def save_change(self):
        for key in self.widget_cmd:
            self.conf.launcher[self.ind][key] = self.widget_cmd[key].get_text()

        self.conf.launcher[self.ind]['icon_size'] = int(self.icon_size.get_value())
        self.conf.launcher[self.ind]['show_label'] = int(self.show_label_checkbox.get_active())
        self.conf.plg_mgr.plugins[self.ind].restart()
