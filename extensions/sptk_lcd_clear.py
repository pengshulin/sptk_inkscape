#!/usr/bin/env python
from sptk_lcd import *

class C(SegmentLCD):
    def effect(self):
        for id, node in self.selected.iteritems():
            self.apply_opacity(node, False)

c = C()
c.affect()
