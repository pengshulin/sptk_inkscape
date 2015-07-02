#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from sptk_lcd import *
import os, sys
import pprint, copy
import wx
import gettext
from sptk_lcd_snapshot_ui import SnapshotDialog


class UiDialog(SnapshotDialog):
    index = None

    def OnAdd(self, event):
        name = self.text_name.GetValue().strip()
        for i in self.parent.snapshots:
            if i['name'] == name:
                dlg = wx.MessageDialog(self, 'name exists', '',
                               wx.OK | wx.ICON_INFORMATION )
                dlg.ShowModal()
                dlg.Destroy()
                return
        self.parent.snapshots.append( {'name':name, 'flags':self.parent.current_snapshot} )
        ctrl = self.list_history.GetListCtrl()
        ctrl.InsertStringItem(len(self.parent.snapshots)-1, name)
        ctrl.Select(len(self.parent.snapshots)-1)
        event.Skip()

    def load_selected(self):
        nodes = self.parent.snapshots[self.index]['flags']
        for seg in self.parent.segments:
            id = self.parent.segments[seg]
            on = bool(seg in nodes)
            self.parent.apply_opacity(self.parent.getElementById(id), on)

    def OnLoad(self, event):
        self.load_selected()
        self.end()
        event.Skip()

    def OnDclick(self, event):
        self.load_selected()
        self.end()
        event.Skip()

    def end(self):
        self.parent.save_snapshots()
        #self.app.Exit()
        self.app.ExitMainLoop()

    def OnClose(self,event):
        self.end()
        event.Skip()

    def OnSelect(self,event):
        ctl = self.list_history.GetListCtrl()
        self.index = ctl.GetFirstSelected()
        try:
            name = self.parent.snapshots[self.index]['name']
            self.text_name.SetValue( name )
        except:
            pass
        event.Skip()

    def OnDelete(self,event):
        if not self.parent.snapshots:
            return 
        self.parent.snapshots.pop(self.index)
        if len(self.parent.snapshots):
            if self.index > len(self.parent.snapshots)-1:
                self.list_history.GetListCtrl().Select(len(self.parent.snapshots)-1)
        else:
            self.list_history.GetListCtrl().DeleteAllItems()
        event.Skip()

    def OnUp(self,event):
        if self.index:
            orig = self.parent.snapshots.pop(self.index)
            self.index = self.index - 1
            self.parent.snapshots.insert(self.index, orig)
        event.Skip()

    def OnDown(self,event):
        if self.index < len(self.parent.snapshots)-1:
            orig = self.parent.snapshots.pop(self.index)
            self.index = self.index + 1
            self.parent.snapshots.insert(self.index, orig)
        event.Skip()

    def OnDone(self,event):
        self.end()
        event.Skip()

    def OnBeginEdit(self,event):
        event.Skip()

    def OnEndEdit(self,event):
        # old name
        oldname = self.parent.snapshots[self.index]['name']
        # new name 
        ctrl = self.list_history.GetListCtrl()
        newname = ctrl.GetItemText(self.index).strip()
        print oldname, '->', newname
        if newname != oldname:
            # check if it exists
            existing_list = [i['name'] for i in self.parent.snapshots]
            existing_list.remove(oldname)
            if newname in existing_list:
                dlg = wx.MessageDialog(self, 'name exists', '',
                                       wx.OK | wx.ICON_INFORMATION )
                dlg.ShowModal()
                dlg.Destroy()
                # set back
                ctrl.SetStringItem(self.index, 0, oldname)
            else:
                # update list
                self.parent.snapshots[self.index]['name'] = newname 
        event.Skip()




class C(SegmentLCD):

    def effect(self):
        self.segments = {}
        self.snapshots = []
        self.load_filename()
        sys.path.append( self.dir )
        if not self.check_dir():
            self.create_dir()
        self.load_segments()
        if not self.segments:
            self.rescan_segments_defination()
            if not self.segments:
                inkex.debug('WARNING: no segment defined')
                return
            else:
                self.save_segments()
        self.scan_current_snapshot()
        self.load_snapshots()
        # begin ui
        gettext.install("app") # replace with the appropriate catalog name
        self.app = wx.PySimpleApp(0)
        wx.InitAllImageHandlers()
        self.dialog_snapshot = UiDialog(None, wx.ID_ANY, "")
        self.app.SetTopWindow(self.dialog_snapshot)
        self.dialog_snapshot.list_history.Bind(wx.EVT_BUTTON, self.dialog_snapshot.OnDelete, self.dialog_snapshot.list_history.GetDelButton())
        self.dialog_snapshot.list_history.Bind(wx.EVT_BUTTON, self.dialog_snapshot.OnUp, self.dialog_snapshot.list_history.GetUpButton())
        self.dialog_snapshot.list_history.Bind(wx.EVT_BUTTON, self.dialog_snapshot.OnDown, self.dialog_snapshot.list_history.GetDownButton())
        self.dialog_snapshot.list_history.Bind(wx.EVT_LIST_ITEM_SELECTED, self.dialog_snapshot.OnSelect, self.dialog_snapshot.list_history.GetListCtrl())
        self.dialog_snapshot.list_history.GetListCtrl().Bind(wx.EVT_LEFT_DCLICK, self.dialog_snapshot.OnDclick)
        self.dialog_snapshot.list_history.GetListCtrl().Bind(wx.EVT_LIST_BEGIN_LABEL_EDIT, self.dialog_snapshot.OnBeginEdit)
        self.dialog_snapshot.list_history.GetListCtrl().Bind(wx.EVT_LIST_END_LABEL_EDIT, self.dialog_snapshot.OnEndEdit)
        self.dialog_snapshot.parent = self
        if self.snapshots:
            ctl = self.dialog_snapshot.list_history
            ctl.SetStrings([i['name'] for i in self.snapshots])
            ctl.GetListCtrl().Select(len(self.snapshots)-1)
        self.dialog_snapshot.Show()
        self.dialog_snapshot.app = self.app
        self.app.MainLoop()
    
    def load_filename(self):
        installed = False
        try:
            filename = os.path.basename( self.document.xpath('/svg:svg/@sptk_filename',\
                                                 namespaces=inkex.NSS)[0] )
            installed = True
        except:
            try:
                filename = os.path.basename(\
                                self.xpathSingle('/svg:svg/@sodipodi:docname'))
            except:
                filename = 'untitled'

        if not installed:
            try:
                node = self.xpathSingle('/svg:svg')
                node.attrib['sptk_filename'] = filename
            except:
                pass
            
        dirname = os.path.basename(filename).replace(' ', '_').replace('.', '_')
        self.dir = os.path.join(LCD_DIR, dirname)
        self.segment_filename = os.path.join(self.dir, "sptk_lcd_segment.py")
        self.snapshot_filename = os.path.join(self.dir, "sptk_lcd_snapshot_data.py")

    def check_dir(self):
        return os.path.isdir(self.dir)

    def create_dir(self):
        if not os.path.isdir(DIR):
            os.mkdir(DIR) 
        if not os.path.isdir(LCD_DIR):
            os.mkdir(LCD_DIR) 
        if not os.path.isdir(self.dir):
            os.mkdir(self.dir) 

    def load_segments(self):
        try:
            import sptk_lcd_segment as data
            self.segments = copy.deepcopy(data.segments)
            del data
        except:
            self.segments = {}
           
    def save_segments(self):
        f = open(self.segment_filename, 'w+')
        f.write('# coding:utf-8\n')
        f.write('segments = \\\n')
        pprint.pprint( self.segments, f )
        f.write('\n')
        f.close()

    def load_snapshots(self):
        try:
            import sptk_lcd_snapshot_data as data
            self.snapshots = copy.deepcopy(data.snapshots)
            del data
        except:
            self.snapshots = []
 
    def save_snapshots(self):
        f = open(self.snapshot_filename, 'w+')
        f.write('# coding:utf-8\n')
        f.write('snapshots = \\\n')
        pprint.pprint( self.snapshots, f )
        f.write('\n')
        f.close()

    def rescan_segments_defination(self):
        self.segments = {}
        for id in self.doc_ids:
            node = self.getElementById(id)
            key = '{%s}label'% inkex.NSS['inkscape']
            try:
                label = node.attrib[key]
            except KeyError:
                label = None
            if label is None:
                continue
            for attrib in label.split(' '):  # I prefer attribs with space seperated
                try:
                    k, v = attrib.split('=')  # eg: name=icon_hold
                    if (k == 'name') and v:
                        self.segments[v] = id
                        break
                except ValueError:
                    continue

   
    def scan_current_snapshot(self):
        result = []
        for name in self.segments:
            id = self.segments[name]
            node = self.getElementById(id)
            style = node.get('style')
            set = True
            if style:
                attribs = style.split(';')
                for i, v in enumerate(attribs):
                    if v.startswith('opacity:'):
                        try:
                            setting = float(v[8:])
                            if setting < (OPACITY_ON + OPACITY_OFF)/2 :
                                set = False
                        except ValueError:
                            pass
                        break
            if set:
                result.append( name )
        if result:
            self.current_snapshot = result
            return True
        else:
            return False




c = C()
c.affect()

