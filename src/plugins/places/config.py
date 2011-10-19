import gtk

settings = {'filemanager':'xdg-open'}

class config():
    def __init__(self, box, conf, ind):

        self.conf = conf
        self.ind = ind

        for key in settings:
            if not key in conf.launcher[ind]:
                conf.launcher[ind][key] = settings[key]

        label = gtk.Label("Filemanager :")
        label.set_alignment(0, 0.5)
        self.filemanager = gtk.Entry()
        self.filemanager.set_width_chars(20)
        self.filemanager.set_text(conf.launcher[ind]['filemanager'])

        box.pack_start(label, False, False)
        box.pack_start(self.filemanager, False, False)

    def save_change(self):
        self.conf.launcher[self.ind]['filemanager'] = self.filemanager.get_text()
