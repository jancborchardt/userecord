#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-


import wx

import pygtk
pygtk.require("2.0")
import gobject
gobject.threads_init()
import pygst
pygst.require("0.10")
import gst

import signal
import subprocess
import os.path
import sys
import re

import pongo

class MainWindow(wx.Frame):

    def __init__(self, parent = None, id = -1, title = "Small Editor"):
        # Init
        wx.Frame.__init__(
            self, parent, id, title, size = (400,200),
            style = wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE
        )


        # StatusBar
        self.CreateStatusBar()

        # Filemenu
        filemenu = wx.Menu()

        # Filemenu - About
        menuitem = filemenu.Append(-1, "&About", "Information about this program")
        self.Bind(wx.EVT_MENU, self.OnAbout, menuitem) # Hier wird der Event-Handler angegeben

        # Filemenu - Separator
        filemenu.AppendSeparator()

        # Filemenu - Exit
        menuitem = filemenu.Append(-1, "E&xit", "Terminate the program")
        self.Bind(wx.EVT_MENU, self.OnExit, menuitem)
        self.Bind(wx.EVT_CLOSE, self.OnExit)

        # Menubar
        menubar = wx.MenuBar()
        menubar.Append(filemenu,"Options")
        self.SetMenuBar(menubar)
        
        # Start-Button
        self.startButton = wx.Button(self,-1, "Start")
        self.startButton.Bind(wx.EVT_BUTTON, self.StartButtonClick)

        # Show
        self.Show(True)
        


    def StartButtonClick(self, event):
        

        if self.startButton.Label == "Start":
            self.startButton.SetLabel("Save recording")

            pongo.main()

        else:
            self.startButton.SetLabel("Start")

            kill = True
            pongo.main(kill)


    def OnAbout(self,event):
        # sets new text
        #self.control.SetValue("New Text")
        self.control.Hide();
        # BoxSizer for proportional positioning
        
    def OnExit(self,event):
        # dialog to verify exit (including menuExit)
        dlg = wx.MessageDialog(self, "Want to exit? If you want to exit the programm, during the recording, you get a useless video-file in the pongo-folder.", "Exit", wx.YES_NO | wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_YES:
            self.Destroy() # frame
        dlg.Destroy()
        sys.exit()



app = wx.PySimpleApp()
frame = MainWindow()
app.MainLoop()