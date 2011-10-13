## based on volti : http://code.google.com/p/volti/

import gtk
import alsaaudio as alsa
import pango

import adesk.core as Core

settings = {'mixer':'xterm -e alsamixer','card_index':0, 'control':'Master'}

class config():
    def __init__(self, box, conf, ind):

        self.conf = conf
        self.ind = ind

        for key in settings:
            if not key in conf.launcher[ind]:
                conf.launcher[ind][key] = settings[key]

        self.settings = conf.launcher[ind]

        mixerbox = gtk.HBox(False, 0)
        box.pack_start(mixerbox, False, False)

        label = gtk.Label("Mixer :")
        label.set_alignment(0, 0.5)

        self.mixer = gtk.combo_box_entry_new_text()

        mixer_list = (
            "aumix",
            "xfce4-mixer",
            "xterm -e alsamixer",
            "alsamixergui",
            "gamix" ,
            "gmixer",
            "gnome-alsamixer",
            "gnome-volume-control",
            "pavucontrol"
            )

        if not conf.launcher[ind]['mixer'] in mixer_list:
            mixer_list = (conf.launcher[ind]['mixer'], ) + mixer_list

        ind_mixer = 0 # FIXME !!
        for mixer in mixer_list:
            self.mixer.append_text(mixer)
            if mixer == conf.launcher[ind]['mixer']:
                self.mixer.set_active(ind_mixer)
            ind_mixer += 1

        self.mixer.child.connect('changed', self.changed_mixer)

        mixerbox.pack_start(label)
        mixerbox.pack_start(self.mixer)

        self.alsactrl = AlsaControl(int(self.settings["card_index"]), self.settings["control"])

        """ Initialize treeview with mixers """
        self.liststore = gtk.ListStore(bool, str, int)
        for mixer in self.alsactrl.get_mixers():
            active = (mixer == self.settings["control"])
            if active:
                self.liststore.append([active, mixer, pango.WEIGHT_BOLD])
            else:
                self.liststore.append([active, mixer, pango.WEIGHT_NORMAL])

        self.treeview = gtk.TreeView(self.liststore)
        self.treeview.set_headers_visible(False)

        cell1 = gtk.CellRendererToggle()
        cell1.set_radio(True)
        cell1.set_property("activatable", True)
        cell1.connect('toggled', self.on_treeview_toggled, self.liststore)
        column1 = gtk.TreeViewColumn()
        column1.pack_start(cell1, True)
        column1.add_attribute(cell1, 'active', 0)
        self.treeview.append_column(column1)

        cell2 = gtk.CellRendererText()
        column2 = gtk.TreeViewColumn()
        column2.pack_start(cell2, True)
        column2.add_attribute(cell2, 'text', 1)
        column2.add_attribute(cell2, 'weight', 2)
        self.treeview.append_column(column2)

        scrolledwindow = gtk.ScrolledWindow()
        scrolledwindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolledwindow.add(self.treeview)

        """ Initialize combobox with list of audio cards """
        icon = Core.pixbuf_from_file('images/conf/audio-card.png', 22, 22)

        self.combo_model = gtk.ListStore(int, gtk.gdk.Pixbuf, str)
        cards = self.alsactrl.get_cards()
        for index, card in enumerate(cards):
            if card is not None:
                self.combo_model.append([index, icon, card])

        card_combobox = gtk.ComboBox()
        card_combobox.set_model(self.combo_model)
        card_combobox.set_active(int(self.settings["card_index"]))

        cell1 = gtk.CellRendererPixbuf()
        cell1.set_property("xalign", 0)
        cell1.set_property("xpad", 3)
        card_combobox.pack_start(cell1, False)
        card_combobox.add_attribute(cell1, "pixbuf", 1)

        cell2 = gtk.CellRendererText()
        cell2.set_property("xpad", 10)
        card_combobox.pack_start(cell2, True)
        card_combobox.set_attributes(cell2, text=2)

        card_combobox.connect("changed", self.on_card_combobox_changed)

        box.pack_start(card_combobox, False, False)
        box.pack_end(scrolledwindow, True)

    def on_card_combobox_changed(self, widget=None):
        """ Callback for card_combobox_changed event """
        model = widget.get_model()
        iter = widget.get_active_iter()
        card_index = model.get_value(iter, 0)
        self.settings["card_index"] = card_index
        self.alsactrl.card_index = card_index
        self.settings["control"] = self.alsactrl.get_mixers()[0]

        self.liststore.clear()

        for mixer in self.alsactrl.get_mixers():
            active = (mixer == self.settings["control"])
            if active:
                self.liststore.append([active, mixer, pango.WEIGHT_BOLD])
            else:
                self.liststore.append([active, mixer, pango.WEIGHT_NORMAL])

    def on_treeview_toggled(self, cell, path, model):
        """ Callback for treeview_toggled event """
        iter = model.get_iter_from_string(path)
        active = model.get_value(iter, 0)
        if not active:
            model.foreach(self.radio_toggle)
            model.set(iter, 0, not active)
            model.set(iter, 2, pango.WEIGHT_BOLD)
            self.settings["control"] = model.get_value(iter, 1)

    def radio_toggle(self, model, path, iter):
        """ Toggles radio buttons status """
        active = model.get(iter, 0)
        if active:
            model.set(iter, 0, not active)
            model.set(iter, 2, pango.WEIGHT_NORMAL)

    def changed_mixer(self, entry):
        self.conf.launcher[self.ind]['mixer'] = entry.get_text()
        print entry.get_text(), self.conf.launcher[self.ind]['mixer']

    def save_change(self):
        pass

class AlsaControl():
    """ Interface to ALSA mixer API. """

    def __init__(self, card_index, control):
        """ Constructor """
        try:
            self.muted = False
            self.card_index = card_index
            self.control = control
            self.channel = alsa.MIXER_CHANNEL_ALL
            self.mixer = alsa.Mixer(control=self.control, cardindex=self.card_index)

        except Exception, err:
            print "can't open %s control for card %s\nerror: %s\n" % (self.control, self.get_card_name(), str(err))
            try:
                self.mixer = alsa.Mixer(control=self.get_mixers()[0], cardindex=self.card_index)
            except Exception, err:
                print "can't open %s control for card %s\nerror: %s\nExiting\n" % (self.control, self.get_card_name(), str(err))

    def get_card_name(self):
        """ Returns card name """
        try:
            return alsa.cards()[self.card_index]
        except IndexError, err:
            print str(err)

    def get_mixer_name(self):
        """ Returns mixer name """
        try:
            return self.mixer.mixer()
        except alsa.ALSAAudioError, err:
            print str(err)

    def get_cards(self):
        """ Returns cards list """
        cards = []
        acards = alsa.cards()
        for index, card in enumerate(acards):
            try:
                alsa.mixers(index)[0]
            except Exception, err:
                # card doesn't have any mixer control
                cards.append(None)
                print str(err)
            else:
                cards.append(acards[index])
        return cards

    def get_mixers(self):
        """ Returns mixers list """
        try:
            return alsa.mixers(self.card_index)
        except Exception, err:
            print str(err)
