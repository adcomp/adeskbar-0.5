import gtk

settings = {'filemanager':'xdg-open'}

class config(gtk.Frame):
    def __init__(self, conf, ind):
        gtk.Frame.__init__(self)
        self.conf = conf
        self.ind = ind

        self.set_border_width(5)
        framebox = gtk.HBox(False, 0)
        framebox.set_border_width(5)
        framebox.set_spacing(10)
        self.pack_start(framebox, False, False)

        for key in settings:
            if not conf.launcher[ind].has_key(key):
                conf.launcher[ind][key] = settings[key]

        label = gtk.Label("Filemanager :")
        label.set_alignment(0, 0.5)
        self.filemanager = gtk.Entry()
        self.filemanager.set_width_chars(20)
        self.filemanager.set_text(conf.launcher[ind]['filemanager'])

        framebox.pack_start(label)
        framebox.pack_end(self.filemanager)

    def save_change(self):
        self.conf.launcher[self.ind]['filemanager'] = self.filemanager.get_text()
