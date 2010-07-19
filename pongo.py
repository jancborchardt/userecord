#!/usr/bin/env python
# Pongo, an inexpensive UI lab
# Originally by Andreas Nilsson: http://www.andreasn.se/blog/?p=96
# Requires python and istanbul: http://live.gnome.org/Istanbul

import pygtk
pygtk.require("2.0")
import gobject
gobject.threads_init()
import pygst
pygst.require("0.10")
import gst

import signal

def clean_shutdown(p):
    camsrc=p.get_by_name("camsrc")
    xsrc=p.get_by_name("xsrc")
    asrc=p.get_by_name("asrc")
    eos=gst.event_new_eos()

    camsrc.send_event(eos)
    xsrc.send_event(eos)
    asrc.send_event(eos)

    bus = p.get_bus()
    bus.poll(gst.MESSAGE_EOS | gst.MESSAGE_ERROR, -1)

def interrupt():
    loop.quit()
    
out_file="final.ogv"

out_w=1024
out_h=768

cam_w=300
cam_h=200
cam_opacity=0.8

v4l_device="/dev/video0"

p=gst.parse_launch("""videomixer name=mix ! ffmpegcolorspace ! queue ! theoraenc ! oggmux name=mux ! filesink location=%s
istximagesrc name=xsrc use-damage=false ! videorate ! video/x-raw-rgb,framerate=10/1 ! ffmpegcolorspace ! videoscale method=1 ! video/x-raw-yuv,width=%d,height=%d ! mix.sink_0
v4l2src name=camsrc device=%s ! ffmpegcolorspace ! videorate ! video/x-raw-yuv,framerate=10/1,width=320,height=240 ! queue ! videoscale ! ffmpegcolorspace ! video/x-raw-yuv,height=%d,height=%d ! mix.sink_1
alsasrc name=asrc ! queue ! audioconvert ! vorbisenc ! mux.""" % \
    (out_file, out_w, out_h, v4l_device, cam_w, cam_h))

mix=p.get_by_name("mix")
cam_pad = mix.get_pad("sink_1")
cam_pad.set_property("xpos", out_w-cam_w)
cam_pad.set_property("ypos", out_h-cam_h)
cam_pad.set_property("alpha", cam_opacity)
cam_pad.set_property("zorder", 1)

p.set_state(gst.STATE_PLAYING)
print "Capturing..."

loop = gobject.MainLoop()
try:
  loop.run()
except KeyboardInterrupt:
  pass 

print "Stopping capture..."
clean_shutdown(p)
p.set_state(gst.STATE_NULL)
print "Done"
