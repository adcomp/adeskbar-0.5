import gtk

settings = {'terminal':'x-terminal-emulator', 'show_label':1, 'run':1}

class config():

    def __init__(self, box, conf, ind):

        self.conf = conf
        self.ind = ind

        for key in settings:
            if not key in conf.launcher[ind]:
                conf.launcher[ind][key] = settings[key]

        self.settings = conf.launcher[ind]
        if self.settings['show_label'] in ('False','false','0', 0):
            self.settings['show_label'] = 0
        else:
            self.settings['show_label'] = 1

        self.settings = conf.launcher[ind]
        if self.settings['run'] in ('False','false','0', 0):
            self.settings['run'] = 0
        else:
            self.settings['run'] = 1

        self.show_label_checkbox = gtk.CheckButton('Show category label')
        self.show_label_checkbox.set_active(self.settings['show_label'])

        term_box = gtk.HBox(False, 4)
        label = gtk.Label("Terminal :")
        label.set_alignment(0, 0.5)
        self.terminal = gtk.Entry()
        self.terminal.set_width_chars(20)
        self.terminal.set_text(conf.launcher[ind]['terminal'])
        term_box.pack_start(label, False, False)
        term_box.pack_start(self.terminal, True, True)

        self.show_run_checkbox = gtk.CheckButton('Show "run" entry')
        self.show_run_checkbox.set_active(self.settings['run'])

        box.pack_start(self.show_label_checkbox, False, False)
        box.pack_start(self.show_run_checkbox, False, False)
        box.pack_start(term_box, False, False)

    def save_change(self):
        self.conf.launcher[self.ind]['terminal'] = self.terminal.get_text()
        self.conf.launcher[self.ind]['show_label'] = int(self.show_label_checkbox.get_active())
        self.conf.launcher[self.ind]['run'] = int(self.show_run_checkbox.get_active())
        self.conf.plg_mgr.plugins[self.ind].restart()
        
