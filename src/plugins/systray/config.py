import gtk

settings = {
    'gradient_divider': 1.50, 
    'gradient_invert': 0
    }

class config():
    def __init__(self, box, conf, ind):

        self.conf = conf
        self.ind = ind

        for key in settings:
            if not key in conf.launcher[ind]:
                conf.launcher[ind][key] = settings[key]

        self.settings = conf.launcher[ind]

        table = gtk.Table(2, 4, False)

        label = gtk.Label("Background gradient divider :")
        label.set_alignment(0, 0.5)
        adjustment = gtk.Adjustment(value=float(self.settings['gradient_divider']), lower=1.0, upper=2.0, step_incr=0.05, page_size=0)
        self.gradient_divider = gtk.SpinButton(adjustment=adjustment, climb_rate=0.0, digits=2)
        table.attach(label, 0, 1, 0, 1)
        table.attach(self.gradient_divider, 1, 2, 0, 1)

        self.gradient_invert = gtk.CheckButton('Invert background gradient before dividing')
        self.gradient_invert.set_active(int(self.settings['gradient_invert']))

        table.attach(self.gradient_invert, 0, 2, 1, 2)

        label = gtk.Label('')
        label.set_alignment(0, 0.5)
        table.attach(label, 0, 2, 2, 3)

        label = gtk.Label('These apply only when bar background is set to gradient.')
        label.set_alignment(0, 0.5)
        table.attach(label, 0, 2, 3, 4)

        box.pack_start(table, False, False)

    def save_change(self):
        self.conf.launcher[self.ind]['gradient_divider'] = float(self.gradient_divider.get_value())
        self.conf.launcher[self.ind]['gradient_invert'] = int(self.gradient_invert.get_active())
