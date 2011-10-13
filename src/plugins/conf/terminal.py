import gtk

settings = {
    'width':500,
    'height':300,
    'font':'monospace 10',
    'opacity':80,
    'exec_cmd':'',
    }

class config():
    def __init__(self, box, conf, ind):

        self.conf = conf
        self.ind = ind

        for key in settings:
            if not key in conf.launcher[ind]:
                conf.launcher[ind][key] = settings[key]

        self.settings = conf.launcher[ind]

        label = gtk.Label("Size / Font / Opacity  :")
        label.set_alignment(0, 0.5)

        val = int(self.settings['width'])
        adjustment = gtk.Adjustment(value=val, lower=100, upper=2000, step_incr=10, page_incr=100, page_size=0)
        self.term_w = gtk.SpinButton(adjustment=adjustment, climb_rate=0.0, digits=0)

        val = int(self.settings['height'])
        adjustment = gtk.Adjustment(value=val, lower=100, upper=2000, step_incr=10, page_incr=100, page_size=0)
        self.term_h = gtk.SpinButton(adjustment=adjustment, climb_rate=0.0, digits=0)

        val = int(self.settings['opacity'])
        adjustment = gtk.Adjustment(value=val, lower=0, upper=100, step_incr=1, page_incr=10, page_size=0)
        self.term_opacity = gtk.SpinButton(adjustment=adjustment, climb_rate=0.0, digits=0)

        self.term_font = gtk.FontButton(self.settings['font'])

        hbox = gtk.HBox()
        hbox.set_spacing(10)
        hbox.pack_start(label, True)
        hbox.pack_start(self.term_w, False, False)
        hbox.pack_start(gtk.Label('x'), False, False)
        hbox.pack_start(self.term_h, False, False)
        hbox.pack_start(self.term_font, False, False)
        hbox.pack_end(self.term_opacity, False, False)
        
        box.pack_start(hbox, False, False)

        label = gtk.Label("Execute command :")
        label.set_alignment(0, 0.5)
        self.exec_cmd = gtk.Entry()
        self.exec_cmd.set_text(self.settings['exec_cmd'])
        
        hbox = gtk.HBox()
        hbox.set_spacing(10)
        hbox.pack_start(label, False, False)
        hbox.pack_end(self.exec_cmd, True)
        
        box.pack_start(hbox, False, False)


    def save_change(self):
        self.conf.launcher[self.ind]['width'] = int(self.term_w.get_value())
        self.conf.launcher[self.ind]['height'] = int(self.term_h.get_value())
        self.conf.launcher[self.ind]['opacity'] = int(self.term_opacity.get_value())
        self.conf.launcher[self.ind]['font'] = self.term_font.get_font_name()
        self.conf.launcher[self.ind]['exec_cmd'] = self.exec_cmd.get_text()
        self.conf.plg_mgr.plugins[self.ind].restart()
