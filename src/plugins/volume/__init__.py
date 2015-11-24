# -*- coding: utf-8 -*-
#
# ADeskBar - "Volume" plugin
#
##

# INFO:
# - Uses some code from Volti

import gtk
import gobject

import adesk.plugin as Plg
import adesk.core as Core
import adesk.ui as UI

import locale
import gettext
## Translation
locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain('adeskbar', './locale')
gettext.bind_textdomain_codeset('adeskbar','UTF-8')
gettext.textdomain('adeskbar')
_ = gettext.gettext

try:
    import alsaaudio as alsa
except:
    Core.logINFO('Plugin "volume" need python-alsaaudio')
    Core.logINFO(' -- debian/ubuntu : "sudo apt-get install python-alsaaudio"')

INC = 5

class Plugin(Plg.Plugin):
    
    def __init__(self, bar, settings):
        Plg.Plugin.__init__(self, bar, settings)

        ## FIXME!! check if settings for card_index/control
        if not 'card_index' in self.settings: self.settings['card_index']=0
        if not 'control' in self.settings: self.settings['control']='Master'

        self.volume = Volume(self, bar)
        self.connect('scroll-event', self.on_scroll_event)

    def onClick(self, widget, event):
        self.volume.update_status()
        self.volume.toggle()

    def resize(self):
        self.set_size_request(self.cfg['icon_size'], self.cfg['icon_size'])

    def on_scroll_event(self, widget, event):
        if event.direction == gtk.gdk.SCROLL_UP:
            self.volume.change_volume(INC)
        elif event.direction == gtk.gdk.SCROLL_DOWN:
            self.volume.change_volume(- INC)
            
    def on_init(self):
        self.volume.on_init()

class Volume(UI.PopupWindow):
    def __init__(self, plugin, bar):
        UI.PopupWindow.__init__(self, bar, plugin)

        self.card_index = int(plugin.settings['card_index'])
        self.control = plugin.settings['control']

        try:
            self.mixer = alsa.Mixer(control=self.control, cardindex=self.card_index)
        except Exception, err:
            print 'Mixer plugin ERR:', err
            try:
                self.mixer = alsa.Mixer(control=alsa.mixers(self.card_index).get_mixers()[0], cardindex=self.card_index)
            except Exception, err:
                print 'Mixer plugin ERR:', err
                self.mixer = None
                self.set_volume(0)

        if self.mixer:
            try:
                vol = self.mixer.getvolume()[0]
            except alsa.ALSAAudioError, err:
                print 'Mixer plugin ERR:', err
                vol = 0
                self.update_icon_status('audio-volume-muted')
        else:
            self.update_icon_status('audio-volume-muted')
            vol = 0

        adj = gtk.Adjustment(value=vol, lower=0, upper=100, step_incr=1, page_incr=5)

        self.scale = gtk.VScale(adjustment=adj)
        self.scale.set_size_request(30, 170)
        self.scale.set_inverted(True)
        self.scale.set_digits(0)
        self.scale.show()
        self.scale.connect("value_changed", self.on_value_changed)

        self.box = gtk.VBox(False, 4)
        self.box.set_border_width(2)

        mixer_bt = gtk.Button()
        image =  gtk.Image()
        pixbuf = Core.get_pixbuf_icon('multimedia-volume-control', self.cfg['icon_size'])
        image.set_from_pixbuf(pixbuf)
        mixer_bt.set_image(image)
        mixer_bt.connect("clicked", self.onClicked)
        mixer_bt.set_relief(gtk.RELIEF_NONE)
        mixer_bt.set_border_width(0)
        mixer_bt.set_focus_on_click(False)
        mixer_bt.set_property('can-focus', False)
        mixer_bt.show()

        self.box.pack_start(self.scale)
        self.box.pack_end(mixer_bt)
        self.add(self.box)
        self.box.show()
        
        self.set_volume(vol)
 
        gobject.timeout_add(15000, self.update_status)

    def update_icon_status(self, icon):
        self.plugin.set_icon(icon)

    def update_status(self):
        if self.mixer:
            self.mixer = alsa.Mixer(control=self.control, cardindex=self.card_index)
            self.scale.set_value(int(self.mixer.getvolume()[0]))
            return True
        return False
        
    def set_volume(self, volume):
        if self.mixer:
            try:
                self.mixer.setvolume(int(volume))
                if self.cfg['tooltips']:
                  if volume == 0:
                    self.plugin.tooltip = _('Muted')
                  else:
                    self.plugin.tooltip = _('Volume')+' : %s %%' % int(volume)
            except:
                if self.cfg['tooltips']:
                  self.plugin.tooltip = _("No such channel")
        else:
            return

        if volume < 1:
            icon = 'audio-volume-muted'
#        elif volume < 10:
#            icon = 'audio-volume-low'
        elif volume < 33:
            icon = 'audio-volume-low'
        elif volume < 66:
            icon = 'audio-volume-medium'
        else:
            icon = 'audio-volume-high'
        self.update_icon_status(icon)

    def onClicked(self, widget):
        Core.launch_command(self.plugin.settings['mixer'])

    def on_value_changed(self, widget):
        if self.mixer:
            vol = self.scale.get_value()
            if vol == 0:
               self.mixer.setmute(1)
            else:
               self.mixer.setmute(0)
        else:
            vol = 0
        self.set_volume(vol)

#    def get_volume_tooltip(self):
#        if self.mixer:
#            return 'Volume : %s %%' % self.mixer.getvolume()[0]
#        else:
#            return 'no mixer'

    def change_volume(self, data=None):
        if self.mixer:
            vol = self.mixer.getvolume()[0]
            vol = int(vol)
            if data:
                vol += data
                if vol < 0:
                    vol = 0
                elif vol > 100:
                    vol = 100
                self.scale.set_value(vol)

    def on_init(self):
        if self.mixer:
           volume = self.mixer.getvolume()[0]
           self.set_volume(volume)
