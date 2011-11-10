# -*- coding: utf-8 -*-
import gobject
import urllib
from xml.dom import minidom

import gtk

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



class Plugin(Plg.Plugin):
    weather = {}
    condition_codes={
'0':_('Tornado'),
'1':_('Tropical storm'),
'2':_('Hurricane'),
'3':_('Severe thunderstorms'),
'4':_('Thunderstorms'),
'5':_('Mixed rain and snow'),
'6':_('Mixed rain and sleet'),
'7':_('Mixed snow and sleet'),
'8':_('Freezing drizzle'),
'9':_('Drizzle'),
'10':_('Freezing rain'),
'11':_('Showers'),
'12':_('Showers'),
'13':_('Snow flurries'),
'14':_('Light snow showers'),
'15':_('Blowing snow'),
'16':_('Snow'),
'17':_('Hail'),
'18':_('Sleet'),
'19':_('Dust'),
'20':_('Foggy'),
'21':_('Haze'),
'22':_('Smoky'),
'23':_('Blustery'),
'24':_('Windy'),
'25':_('Cold'),
'26':_('Cloudy'),
'27':_('Mostly cloudy'),
'28':_('Mostly cloudy'),
'29':_('Partly cloudy'),
'30':_('Partly cloudy'),
'31':_('Clear'),
'32':_('Sunny'),
'33':_('Fair'),
'34':_('Fair'),
'35':_('Mixed rain and hail'),
'36':_('Hot'),
'37':_('Isolated thunderstorms'),
'38':_('Scattered thunderstorms'),
'39':_('Scattered thunderstorms'),
'40':_('Scattered showers'),
'41':_('Heavy snow'),
'42':_('Scattered snow showers'),
'43':_('Heavy snow'),
'44':_('Partly cloudy'),
'45':_('Thundershowers'),
'46':_('Snow showers'),
'47':_('Isolated thundershowers'),
'48':_('Scattered thundershowers')
}
    isday = 'd'
    isshow = 0

    def __init__(self, bar, settings):
        Plg.Plugin.__init__(self, bar, settings)
        self.settings = settings
        #self.can_zoom = True #False
        self.has_tooltip = False
        self.bar = bar

        self.id = 0
        self.weatherplugin = Weather(self, bar)
        self.connect('enter-notify-event', self.onShow)
        self.connect('leave-notify-event', self.onHide)

    def onShow(self, widget, event):
        if int(self.settings['mouseover']) == 1:
          if self.weather != None:
            self.weatherplugin.show()
            self.isshow=1

    def onHide(self, widget, event):
        if int(self.settings['mouseover']) == 1:
          if self.weather != None:
            self.weatherplugin.hide()
            self.isshow=0

    def onClick(self, widget, event):
        if self.weather != None:
          if int(self.isshow) == 0:
            self.isshow=1
            self.weatherplugin.show()
          else:
            self.isshow=0
            self.weatherplugin.hide()

    def update_time(self):
        zip_code = self.settings['zip_code']
        units = self.settings['units']
        metric = int(self.settings['metric'])

        error='No'
        icon = 'weather-clear'

        try:
          self.weather = weather_for_zip(str(zip_code), str(units))
        except Exception, e:
          self.weather=None

        if self.weather == None:
            print "Plugin Weather Yahoo: Error loading weather!"
            icon = 'weather-severe-alert'
            self.set_size_request(self.cfg['icon_size'], self.cfg['icon_size'])
        else:

          if self.weather['lastBuildDate'].count(' am ') != 0:
            n,d,m,y,t,p,z = self.weather['lastBuildDate'].split(' ')
            h, m = t.split(':')
            if int(h) < 6:
              self.isday = 'n'
            elif int(h) == 12:
              self.isday = 'n'
          else:
            n,d,m,y,t,p,z = self.weather['lastBuildDate'].split(' ')
            h, m = t.split(':')
            if (int(h) > 8) & (int(h) < 12):
              self.isday = 'n'
#  7:29 am = 07.29
# 12:29 pm = 12.29
#  1:29 pm = 13.29
          try:
            self.weather['current_condition'] = self.condition_codes[self.weather['current_code']]
          except Exception, e:
            pass
          try:
            self.weather['forecasts'][1]['condition'] = self.condition_codes[self.weather['forecasts'][1]['code']]
          except Exception, e:
            pass

          if int(self.weather['wind_direction']) == 360:
             self.weather['wind_direction'] = _('Nord')
          elif int(self.weather['wind_direction']) >= 315:
             self.weather['wind_direction'] = _('Nord-West')
          elif int(self.weather['wind_direction']) >= 270:
             self.weather['wind_direction'] = _('West')
          elif int(self.weather['wind_direction']) >= 225:
             self.weather['wind_direction'] = _('South-West')
          elif int(self.weather['wind_direction']) >= 180:
             self.weather['wind_direction'] = _('South')
          elif int(self.weather['wind_direction']) >= 135:
             self.weather['wind_direction'] = _('South-East')
          elif int(self.weather['wind_direction']) >= 90:
             self.weather['wind_direction'] = _('East')
          elif int(self.weather['wind_direction']) >= 45:
             self.weather['wind_direction'] = _('Nord-East')
          elif int(self.weather['wind_direction']) >= 0:
             self.weather['wind_direction'] = _('Nord')

          if int(metric) == 1:
             self.weather['wind_speed'] = str(round(float(self.weather['wind_speed']) / 3.6, 2))
             self.weather['units_speed'] = _('m/s')
             self.weather['units_distance'] = _('km')
             self.weather['units_pressure'] = _('mb')

             if self.weather['astronomy_sunrise'].count(' pm') != 0:
                self.weather['astronomy_sunrise'] = self.weather['astronomy_sunrise'][:-3]
                h, m = self.weather['astronomy_sunrise'].split(':')
                h=int(h)+12
                self.weather['astronomy_sunrise'] = str(str(h)+':'+str(m))
             else:
                self.weather['astronomy_sunrise'] = self.weather['astronomy_sunrise'][:-3]

             if self.weather['astronomy_sunset'].count(' pm') != 0:
                self.weather['astronomy_sunset'] = self.weather['astronomy_sunset'][:-3]
                h, m = self.weather['astronomy_sunset'].split(':')
                h=int(h)+12
                self.weather['astronomy_sunset'] = str(str(h)+':'+str(m))
             else:
                self.weather['astronomy_sunset'] = self.weather['astronomy_sunset'][:-3]

             self.weather['atmosphere_pressure'] = str(int(float(self.weather['atmosphere_pressure']) / 1.3332))
          else:
             self.weather['units_speed'] = _('mph')
             self.weather['units_distance'] = _('mi')
             self.weather['units_pressure'] = _('in')

          icon = 'images/plugins/weatheryahoo/small/'+self.weather['current_code']+'.png'
          #icon = 'images/plugins/weatheryahoo/big/'+self.weather['current_code']+self.isday+'.png'
          self.set_size_request(self.cfg['icon_size'], self.cfg['icon_size'])

        self.weatherplugin.update_icon_status(icon)
        self.weatherplugin.restart()
        return True

    def resize(self):
        self.set_size_request(self.cfg['icon_size'], self.cfg['icon_size'])
        self.weatherplugin.restart()

    def on_init(self):
       self.restart()

    def restart(self):
        if self.id != 0:
          gobject.source_remove(self.id)
#30*60000 30 min
        self.id=gobject.timeout_add(1800000, self.update_time)
        self.update_time()



def weather_for_zip(zip_code, units):
          WEATHER_URL = 'http://xml.weather.yahoo.com/forecastrss?w=%s&u=%s'
          WEATHER_NS = 'http://xml.weather.yahoo.com/ns/rss/1.0'
          url = WEATHER_URL % (zip_code, units)
          dom = minidom.parse(urllib.urlopen(url))
          forecasts = []
          for node in dom.getElementsByTagNameNS(WEATHER_NS, 'forecast'):
            forecasts.append({
                'day': node.getAttribute('day'),
                'date': node.getAttribute('date'),
                'low': node.getAttribute('low'),
                'high': node.getAttribute('high'),
                'condition': node.getAttribute('text'),
                'code': node.getAttribute('code')
            })
          atmosphere = dom.getElementsByTagNameNS(WEATHER_NS, 'atmosphere')[0]
          astronomy = dom.getElementsByTagNameNS(WEATHER_NS, 'astronomy')[0]
          wind = dom.getElementsByTagNameNS(WEATHER_NS, 'wind')[0]
          units = dom.getElementsByTagNameNS(WEATHER_NS, 'units')[0]
          ycondition = dom.getElementsByTagNameNS(WEATHER_NS, 'condition')[0]
          return {
                 'current_condition': ycondition.getAttribute('text'),
                 'current_temp': ycondition.getAttribute('temp'),
                 'current_code': ycondition.getAttribute('code'),
                 'forecasts': forecasts,
                 'lastBuildDate': dom.getElementsByTagName('lastBuildDate')[0].firstChild.data,
                 'atmosphere_humidity': atmosphere.getAttribute('humidity'),
                 'atmosphere_visibility': atmosphere.getAttribute('visibility'),
                 'atmosphere_pressure': atmosphere.getAttribute('pressure'),
                 'astronomy_sunrise': astronomy.getAttribute('sunrise'),
                 'astronomy_sunset': astronomy.getAttribute('sunset'),
                 'wind_chill': wind.getAttribute('chill'),
                 'wind_direction': wind.getAttribute('direction'),
                 'wind_speed': wind.getAttribute('speed'),
                 'units_temperature': units.getAttribute('temperature'),
                 'units_distance': units.getAttribute('distance'),
                 'units_pressure': units.getAttribute('pressure'),
                 'units_speed': units.getAttribute('speed')
          }

class Weather(UI.PopupWindow):
    def __init__(self, plugin, bar):
        UI.PopupWindow.__init__(self, bar, plugin)
        self.plugin = plugin

        self.box = gtk.VBox(False, 0)
        self.box.set_border_width(5)

        self.add(self.box)
        self.create_session_button()

    def create_session_button(self):
        if self.plugin.weather == {}:
          return
        if self.plugin.weather == None:
          return

        table = gtk.Table()
        self.box.pack_start(table, False, False)

        label = gtk.Label()
        label.set_alignment(0.98, 0)
        label.set_markup("<b><big><big><span color='#222'>"+self.plugin.weather['current_condition']+"</span></big></big></b>\n\n")
        label.set_justify(gtk.JUSTIFY_RIGHT)
        table.attach(label, 0, 1, 1, 2)

        label = gtk.Label()
        label.set_alignment(0.05, 0.90)
        label.set_markup("<b><big><big><big><big><big><span color='#222'>"+self.plugin.weather['current_temp']+'°'+self.plugin.weather['units_temperature']+'</span></big></big></big></big></big></b>')
        table.attach(label, 0, 1, 1, 2)

        label = gtk.Label()
        label.set_alignment(0.98, 0.90)
        label.set_markup("<span color='#222'>"\
                        +_('Wind : ')+self.plugin.weather['wind_direction']+"\n"\
                        +_('Speed : ')+self.plugin.weather['wind_speed']+' '+self.plugin.weather['units_speed']+"\n"\
                        +_('Humidity : ')+self.plugin.weather['atmosphere_humidity']+'%\n'\
                        +_('Barometer : ')+self.plugin.weather['atmosphere_pressure']+' '+self.plugin.weather['units_pressure']+"\n"\
                        +_('Visibility : ')+self.plugin.weather['atmosphere_visibility']+' '+self.plugin.weather['units_distance']+"\n"\
                        +"\n"\
                        +_('Sunrise : ')+self.plugin.weather['astronomy_sunrise']+"\n"\
                        +_('Sunset : ')+self.plugin.weather['astronomy_sunset']+"\n"\
                        +"</span>")
        label.set_justify(gtk.JUSTIFY_RIGHT)
        table.attach(label, 0, 1, 1, 2)


        image =  gtk.Image()
        pixbuf = Core.pixbuf_from_file('images/plugins/weatheryahoo/big/'+self.plugin.weather['current_code']+self.plugin.isday+'.png', -1, -1) # 250x180
        image.set_from_pixbuf(pixbuf)
        table.attach(image, 0, 1, 1, 2)

        # Tomorrow
        if int(self.plugin.settings['showtomorrow']) == 1:
          label = gtk.Label()
          label.set_alignment(0.98, 0)
          label.set_markup("\n<b><big><big><span color='#222'>"+self.plugin.weather['forecasts'][1]['condition']+"</span></big></big></b>\n\n" \
                        +"\n\n<span color='#222'><b><big>"+_('Day : ')+"<big><big><big>"+self.plugin.weather['forecasts'][1]['high']+'°'+self.plugin.weather['units_temperature']+"</big></big></big></big></b>\n"\
                        +"\n<b><big>"+_('Night : ')+"<big><big><big>"+self.plugin.weather['forecasts'][1]['low']+'°'+self.plugin.weather['units_temperature']+"</big></big></big></big></b></span>")
          label.set_justify(gtk.JUSTIFY_RIGHT)
          table.attach(label, 0, 1, 2, 3)

          image =  gtk.Image()
          pixbuf = Core.pixbuf_from_file('images/plugins/weatheryahoo/big/'+self.plugin.weather['forecasts'][1]['code']+'d.png', -1, -1) # 250x180
          image.set_from_pixbuf(pixbuf)
          table.attach(image, 0, 1, 2, 3)

        self.box.show_all()

    def restart(self):
        self.box.destroy()
        self.box = gtk.VBox(False, 0)
        self.box.set_border_width(5)

        self.add(self.box)

        self.resize(1, 1)
        self.box.set_size_request(-1, -1)
        self.create_session_button()

    def update_icon_status(self, icon):
        self.plugin.set_icon(icon)
