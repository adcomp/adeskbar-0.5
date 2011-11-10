import gtk

settings = {
    'minutes_to_update':15,
    'username':'username_without_@gmail.com',
    'password':'password',
    'exec_cmd':'xdg-open',
    'hide_icon':0,
    'icon_size':24,
    'play_sound':0,
    'file_sound':'',
    'checkonstart':0,
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

        optionbox = gtk.HBox(False, 0)
        optionbox.set_border_width(0)
        optionbox.set_spacing(10)
        box.pack_start(optionbox, False, False)
        box.pack_start(gtk.HSeparator(), False, False)

        self.checkonstart_label_checkbox = gtk.CheckButton(_('Check mail on start'))
        self.checkonstart_label_checkbox.set_active(int(conf.launcher[ind]['checkonstart']))

        optionbox.pack_start(self.checkonstart_label_checkbox, False, False)



        optionbox = gtk.HBox(False, 0)
        optionbox.set_border_width(0)
        optionbox.set_spacing(10)
        box.pack_start(optionbox, False, False)
        box.pack_start(gtk.HSeparator(), False, False)

        self.show_label_checkbox = gtk.CheckButton(_('Hide icon, if no mail'))
        self.show_label_checkbox.set_active(conf.launcher[ind]['hide_icon'])

        adjustment = gtk.Adjustment(value=float(conf.launcher[ind]['icon_size']), lower=16, upper=128, step_incr=1, page_incr=8, page_size=0)
        self.icon_size = gtk.SpinButton(adjustment=adjustment, climb_rate=0.0, digits=0)
        self.icon_size.set_tooltip_text(_('icon size in pixels'))

        label = gtk.Label(_('icon size'))

        optionbox.pack_start(self.show_label_checkbox, False, False)
        optionbox.pack_end(self.icon_size, False, False)
        optionbox.pack_end(label, False, False)



        optionbox = gtk.HBox(False, 0)
        optionbox.set_border_width(0)
        optionbox.set_spacing(10)
        box.pack_start(optionbox, False, False)
        box.pack_start(gtk.HSeparator(), False, False)

        self.play_sound_label_checkbox = gtk.CheckButton(_('Play sound file'))
        self.play_sound_label_checkbox.set_active(int(conf.launcher[ind]['play_sound']))

        optionbox.pack_start(self.play_sound_label_checkbox, False, False)



        table = gtk.Table()
        box.pack_start(table, False, False)

        label = gtk.Label(_("Login :"))
        label.set_alignment(0, 0.5)
        self.username = gtk.Entry()
        self.username.set_width_chars(20)
        self.username.set_text(conf.launcher[ind]['username'])

        table.attach(label, 0, 1, 1, 2)
        table.attach(self.username, 1, 2, 1, 2)


        label = gtk.Label(_("Password :"))
        label.set_alignment(0, 0.5)
        self.password = gtk.Entry()
        self.password.set_visibility(False)
        self.password.set_width_chars(20)
        self.password.set_text(conf.launcher[ind]['password'])

        table.attach(label, 0, 1, 2, 3)
        table.attach(self.password, 1, 2, 2, 3)


        label = gtk.Label(_("Browser :"))
        label.set_alignment(0, 0.5)
        self.exec_cmd = gtk.Entry()
        self.exec_cmd.set_width_chars(20)
        self.exec_cmd.set_text(conf.launcher[ind]['exec_cmd'])

        table.attach(label, 0, 1, 3, 4)
        table.attach(self.exec_cmd, 1, 2, 3, 4)


        label = gtk.Label(_("Minutes to update : "))
        label.set_alignment(0, 0.5)
        self.minutes_to_update = gtk.Entry()
        self.minutes_to_update.set_width_chars(20)
        self.minutes_to_update.set_text(str(conf.launcher[ind]['minutes_to_update']))

        table.attach(label, 0, 1, 4, 5)
        table.attach(self.minutes_to_update, 1, 2, 4, 5)


        label = gtk.Label(_("Sound file :"))
        label.set_alignment(0, 0.5)
        self.file_sound = gtk.Entry()
        self.file_sound.set_width_chars(20)
        command = conf.launcher[ind]['file_sound'].replace("\\\"", "\"")
        self.file_sound.set_text(command)

        self.button_command = gtk.Button("...")
        self.button_command.connect("clicked", self.button_command_clicked)

        table.attach(label, 0, 1, 5, 6)
        table.attach(self.file_sound, 1, 2, 5, 6)

        table.attach(self.button_command,3,4,5,6, gtk.SHRINK, gtk.SHRINK)


    def button_command_clicked(self, widget):
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
            self.file_sound.set_text(dialog.get_filename())
        dialog.destroy()

    def save_change(self):
        self.conf.launcher[self.ind]['minutes_to_update'] = self.minutes_to_update.get_text()
        self.conf.launcher[self.ind]['username'] = self.username.get_text()
        self.conf.launcher[self.ind]['password'] = self.password.get_text()
        self.conf.launcher[self.ind]['exec_cmd'] = self.exec_cmd.get_text()
        self.conf.launcher[self.ind]['icon_size'] = int(self.icon_size.get_value())
        self.conf.launcher[self.ind]['hide_icon'] = int(self.show_label_checkbox.get_active())
        self.conf.launcher[self.ind]['play_sound'] = int(self.play_sound_label_checkbox.get_active())
        self.conf.launcher[self.ind]['file_sound'] = self.file_sound.get_text()
        self.conf.launcher[self.ind]['checkonstart'] = int(self.checkonstart_label_checkbox.get_active())
        self.conf.plg_mgr.plugins[self.ind].restart()

