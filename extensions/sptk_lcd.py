import sys
sys.path.append('/usr/share/inkscape/extensions')  # for pdb debugging
import inkex
from sptk_const import *

class SegmentLCD(inkex.Effect):

    def apply_opacity(self, node, on=True):
        style = node.get('style') 
        set = False
        cfgstr = 'opacity:%s'% (OPACITY_ON if on else OPACITY_OFF)
        if style:
            attribs = style.split(';')
            for i, v in enumerate(attribs):
                if v.startswith('opacity:'):
                    attribs[i] = cfgstr
                    set = True
                    break
            if not set:
                attribs.append( cfgstr )
            node.set('style', ';'.join(attribs))
        else:
            node.set('style', cfgstr )
 
    def toggle_opacity(self, node):
        style = node.get('style')
        set = False 
        if style:
            attribs = style.split(';')
            for i, v in enumerate(attribs):
                if v.startswith('opacity:'):
                    try:
                        setting = float(v[8:])
                        if setting > (OPACITY_ON + OPACITY_OFF)/2 :
                            # set off
                            attribs[i] = 'opacity:%s'% OPACITY_OFF
                        else:
                            # set on
                            attribs[i] = 'opacity:%s'% OPACITY_ON
                        set = True
                        break
                    except ValueError:
                        pass
            if not set:
                # set off
                attribs.append( 'opacity:%s'% OPACITY_OFF )
            node.set('style', ';'.join(attribs))
        else:
            node.set('style', 'opacity:%s'% OPACITY_OFF)
 
