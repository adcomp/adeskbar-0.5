# -*- coding: utf-8 -*-

# python modules
import os
import sys
import traceback

# adeskbar modules
import adesk.core as Core

class Config:
    
    def __init__(self, cfg_file):
        self.cfg_file = cfg_file
        
        # tableau avec la config de la barre
        self.config = {}
        # tableau avec les lanceurs (cmd, icon, name)
        self.launcher = {}
        # liste des index pour la position dans la barre
        self.l_ind = []
        # tableau avec les drawers associés au launcer ( même index )
        self.drawer = {}
        
        ## default config
        self.config['fade_hidden'] = False
        self.config['icon_space'] = 10
        self.config['show_border'] = 1
        self.config['smooth_hide'] = 1
        self.config['bg_color'] = "#1A1A1A"
        self.config['bg_color_sub'] = "#EEEEEE"
        self.config['border_color_sub'] = "#7F7F7F"
        self.config['bar_size'] = 100
        self.config['rounded_corner'] = 15
        self.config['icon_size'] = 36
        self.config['hidden_size'] = 5
        self.config['opacity'] = 70
        self.config['border_color'] = "#313335"
        self.config['padding'] = 4
        self.config['zoom_factor'] = 1.2
        self.config['keep_below'] = False
        self.config['offset_pos'] = 4
        self.config['align'] = "center"
        self.config['timer'] = 1
        self.config['bg_gradient'] = True
        self.config['auto_hide'] = 2
        self.config['auto_raise'] = 1
        self.config['offset_align'] = 0
        self.config['position'] = "bottom"
        self.config['tooltips'] = True
        self.config['fixed_size'] = 100
        self.config['fixed_mode'] = True
        self.config['reserve_space'] = False

        ## new in v0.3.9
        self.config['bg_gradient_color'] ="#7F7F7F"
        ## new in v0.4
        self.config['bar_style'] = 0
        self.config['icons_effects'] = 3
        ## new in v0.5
        self.config['bg_gradient_alpha'] = 65535

    def read(self):
        Core.logINFO("read ..", 'config')
        
        home = os.environ['HOME']

        ## custom config
        if os.access("%s/.config/adeskbar/%s.cfg" % (home, self.cfg_file), os.F_OK|os.R_OK):
            Core.logINFO("config = %s/.config/adeskbar/%s.cfg" % (home, self.cfg_file), 'config')
            conf_path = "%s/.config/adeskbar/%s.cfg" % (home, self.cfg_file)

        ## read default config
        elif os.access("default.cfg", os.F_OK|os.R_OK):
            Core.logINFO("config = default.cfg", 'config')
            conf_path = 'default.cfg'

        ## no config ? exit !
        else:
            Core.logINFO("ERROR : can't read config !!!", 'config')
            #~ Core.show_msg("Sorry, but can't read config !!!")
            #~ sys.exit()
            return
            

        f = open(conf_path,'r')

        current_cat = None
        current_ind = None
        error_config = False

        for line in f:
            
            ## empty or comment ..
            if line == '\n' or line[0] == '#':
                continue
                
            try:
                line = line.strip('\n')
                line = line.strip()

                ## check if is a category
                if line[0] == '[':
                    current_cat = line[1:-1]

                    if '/' in current_cat:
                        tmp = current_cat.split('/')
                        current_cat = tmp[0]
                        current_ind = tmp[1]
                        
                        if current_cat == 'LAUNCHER':
                            self.launcher[current_ind] = {}
                            self.l_ind.append(current_ind)
                            
                    else:
                        current_ind = None
                        
                    continue

                if current_cat == 'CONFIG':
                    tmp = line.split('=', 1)
                    key = tmp[0].strip()
                    self.config[key] = tmp[1].strip()

                elif current_cat == 'LAUNCHER':
                    tmp = line.split('=', 1)
                    key = tmp[0].strip()
                    self.launcher[current_ind][key] = tmp[1].strip()

                elif current_cat == 'DRAWER':
                    (cmd, icon, desc) = line.split('##')
                    if not current_ind in self.drawer:
                        self.drawer[current_ind] = []
                    self.drawer[current_ind].append((cmd.strip(), icon.strip(), desc.strip()))

            except Exception, e:
                print 'Error while parsing self.config file ..'
                traceback.print_exc()
                error_config = True

        f.close()

        ## convert value : str -> int
        for key in ('padding','icon_size','offset_pos','offset_align',
                    'rounded_corner','hidden_size','opacity','timer', 
                    'icons_effects','bar_size','icon_space','auto_hide',
                    'bg_gradient_alpha','bar_style'):
            self.config[key] = int(float(self.config[key]))

        ## convert value : str -> True / False
        for key in ('auto_raise','smooth_hide', 'tooltips', 'reserve_space',
                    'show_border','fade_hidden', 'fixed_mode',
                    'keep_below','bg_gradient'):

            if self.config[key] in ('true','True','1','yes'):
                self.config[key] = True
            else:
                self.config[key] = False

        ## convert color hex->rgb
        self.config['bg_color_rgb'] = Core.hex2rgb(self.config['bg_color'])
        self.config['border_color_rgb'] = Core.hex2rgb(self.config['border_color'])
        self.config['bg_color_sub_rgb'] = Core.hex2rgb(self.config['bg_color_sub'])
        self.config['border_color_sub_rgb'] = Core.hex2rgb(self.config['border_color_sub'])
        self.config['bg_gradient_color_rgb'] = Core.hex2rgb(self.config['bg_gradient_color'])

        if self.config['hidden_size'] < 1:
            self.config['hidden_size'] = 1

        self.config['zoom_factor'] = float(self.config['zoom_factor'])
        self.config['fixed_size'] = float(self.config['fixed_size'])

        if error_config:
            ## FIXME!!
            pass
            #~ adesk.show_msg("Error while loading user self.config .. ( old self.config file ? )")

    def save(self):
        """ save config to file"""
        Core.logINFO("save ..", 'config')
        
        str_cfg = '## ADeskBar config\n\n'
        str_cfg += '[CONFIG]\n'

        for key in self.config:
            if '_rgb' in key:
                continue
            val = self.config[key]
            str_cfg += '    ' + key + ' = ' + str(val) + '\n'

        str_cfg += '\n'

        for ind in self.l_ind:

            str_cfg += '[LAUNCHER/%s]\n' % ind
            #~ if 'launcher' in self.launcher[ind]:
                #~ self.launcher[ind].pop('launcher')
            for key in self.launcher[ind]:
                str_cfg += '    %s = %s\n' % (key, self.launcher[ind][key])
            str_cfg += '\n'

        str_cfg += '\n'

        for ind in self.drawer:
            if not ind in self.launcher:
                continue
            str_cfg += '[DRAWER/%s]\n' % ind
            for drawer in self.drawer[ind]:
                str_cfg += "    %s ## %s ## %s\n" % (drawer[0], drawer[1], drawer[2])
            str_cfg += '\n'

        str_cfg += '\n'

        home = os.environ['HOME']
        if not os.path.exists("%s/.config/adeskbar" % home):
            os.makedirs("%s/.config/adeskbar" % home)

        if self.cfg_file == None or self.cfg_file == 'None':
            self.cfg_file = 'default'

        src = "%s/.config/adeskbar/%s.cfg" % (home, self.cfg_file)
        Core.logINFO("  -- %s" % src )

        configfile =  open(src, 'w')
        configfile.write(str_cfg)
        configfile.close()
