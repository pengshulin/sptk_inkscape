#!/usr/bin/env python
from sptk_lcd import *

class C(SegmentLCD):
    def effect(self):
        for id, node in self.selected.iteritems():
            self.toggle_opacity(node)

c = C()
c.affect()

