import gtk

settings = {
    'zip_code':'2123260',
    'units':'c',
    'metric':1,
    'showtomorrow':1,
    'mouseover':1,
}

import locale
import gettext
## Translation
locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain('adeskbar', './locale')
gettext.bind_textdomain_codeset('adeskbar','UTF-8')
gettext.textdomain('adeskbar')
_ = gettext.gettext

class config():
    def __init__(self, box, conf, ind):
        self.conf = conf
        self.ind = ind

        for key in settings:
            if not key in conf.launcher[ind]:
                conf.launcher[ind][key] = settings[key]

        table = gtk.Table()
        box.pack_start(table, False, False)

        label = gtk.Label(_("Enter WOEID of your city from http://weather.yahoo.com : "))
        label.set_alignment(0, 0.5)
        self.zip_code = gtk.Entry()
        self.zip_code.set_width_chars(8)
        self.zip_code.set_text(conf.launcher[ind]['zip_code'])

        table.attach(label, 0, 1, 1, 2)
        table.attach(self.zip_code, 1, 2, 1, 2)

        separator = gtk.HSeparator()
        box.pack_start(separator, gtk.FALSE, gtk.TRUE, 0)

        optionbox = gtk.HBox(False, 0)
        optionbox.set_border_width(0)
        optionbox.set_spacing(10)



        button = gtk.RadioButton(None, _("use C degree"))
        button.connect("toggled", self.callback, "units")
        if settings['units'] == 'c':
          button.set_active(gtk.TRUE)
        optionbox.pack_start(button, gtk.TRUE, gtk.TRUE, 0)
        button.show()

        button = gtk.RadioButton(button, _("use F degree"))
        if settings['units'] == 'f':
          button.set_active(gtk.TRUE)
        optionbox.pack_start(button, gtk.TRUE, gtk.TRUE, 0)
        button.show()

        box.pack_start(optionbox, False, False)

        separator = gtk.HSeparator()
        box.pack_start(separator, gtk.FALSE, gtk.TRUE, 0)


        optionbox2 = gtk.HBox(False, 0)
        optionbox2.set_border_width(0)
        optionbox2.set_spacing(10)

        button = gtk.RadioButton(None, _("use metric of measures"))
        button.connect("toggled", self.callback2, "metric")
        if settings['metric'] == '1':
          button.set_active(gtk.TRUE)
        optionbox2.pack_start(button, gtk.TRUE, gtk.TRUE, 0)
        button.show()

        button = gtk.RadioButton(button, _("use english of measures"))
        if settings['metric'] == '0':
          button.set_active(gtk.TRUE)
        optionbox2.pack_start(button, gtk.TRUE, gtk.TRUE, 0)
        button.show()

        box.pack_start(optionbox2, False, False)


        optionbox = gtk.HBox(False, 0)
        optionbox.set_border_width(0)
        optionbox.set_spacing(10)
        box.pack_start(optionbox, False, False)
        box.pack_start(gtk.HSeparator(), False, False)

        self.showtomorrow_label_checkbox = gtk.CheckButton(_('Show the forecast for tomorrow'))
        self.showtomorrow_label_checkbox.set_active(int(conf.launcher[ind]['showtomorrow']))
        box.pack_start(self.showtomorrow_label_checkbox, False, False)

        self.mouseover_checkbox = gtk.CheckButton(_('Show on mouseover'))
        self.mouseover_checkbox.set_active(int(conf.launcher[ind]['mouseover']))
        box.pack_start(self.mouseover_checkbox, False, False)

    def save_change(self):
        self.conf.launcher[self.ind]['zip_code'] = self.zip_code.get_text()
        self.conf.launcher[self.ind]['units'] = settings['units']
        self.conf.launcher[self.ind]['metric'] = settings['metric']
        self.conf.launcher[self.ind]['showtomorrow'] = int(self.showtomorrow_label_checkbox.get_active())
        self.conf.launcher[self.ind]['mouseover'] = int(self.mouseover_checkbox.get_active())
        self.conf.plg_mgr.plugins[self.ind].restart()

    def callback(self, widget, data=None):
        settings[data]=("f", "c")[widget.get_active()]

    def callback2(self, widget, data=None):
        settings[data]=("0", "1")[widget.get_active()]
