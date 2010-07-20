#!/usr/bin/env python
# Pongo, an inexpensive UI lab
# Originally by Andreas Nilsson: http://www.andreasn.se/blog/?p=96
# Requires python and istanbul: http://live.gnome.org/Istanbul

print """
- Default camera video position is bottom right.
  To change, use 'top' and 'left' as arguments.
- Disable camera with 'nocam'.
- If you are conducting a RTA (= retrospective thinking aloud),
  use 'shift' to set the camera video next to the one already there.
- For a custom filename use 'filename.ogv' as argument.
"""

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


def clean_shutdown(p):
    camsrc = p.get_by_name("camsrc")
    xsrc = p.get_by_name("xsrc")
    asrc = p.get_by_name("asrc")
    eos = gst.event_new_eos()

    camsrc.send_event(eos)
    xsrc.send_event(eos)
    asrc.send_event(eos)

    bus = p.get_bus()
    bus.poll(gst.MESSAGE_EOS | gst.MESSAGE_ERROR, -1)

def interrupt():
    loop.quit()

# This function takes Bash commands and returns them
# Taken from http://magazine.redhat.com/2008/02/07/python-for-bash-scripters-a-well-kept-secret/
def runBash(cmd):
    p = subprocess.Popen(cmd, shell = True, stdout = subprocess.PIPE)
    out = p.stdout.read().strip()
    return out


out_file = "pongo-"
count = 1
# Do not overwrite existing recordings
while(os.path.isfile(out_file + str(count) + ".ogv")):
    count = count + 1

out_file += str(count)
out_file += ".ogv"

# Automatically get screen dimensions
out_w = int(runBash("xdpyinfo | grep dimensions | cut -d' ' -f7 | cut -d'x' -f1"))
out_h = int(runBash("xdpyinfo | grep dimensions | cut -d' ' -f7 | cut -d'x' -f2"))

cam_w = 300
cam_h = 200
cam_opacity = 0.8
v4l_device = "/dev/video0"

cam = True
cam_x = out_w - cam_w
cam_y = out_h - cam_h

# Optional parameters for setting camera video position
# TODO: additional option for lower quality recording for slower machines
for arg in sys.argv:
    if arg == "nocam":
        cam = False
        cam_opacity = 0 # hack, TODO: deactivate cam directly
    if arg == "left":
        cam_x = 0
    if arg == "top":
        cam_y = 0
    if re.search(".ogv", arg):
        if(os.path.isfile(arg)):
            print "File %s already exists!" % arg
        else:
            out_file = arg

for arg in sys.argv:
    if arg == "shift":
        if cam_x == 0:
            cam_x += cam_w
        else:
            cam_x -= cam_w


p = gst.parse_launch("""videomixer name = mix ! ffmpegcolorspace ! queue ! theoraenc ! oggmux name = mux ! filesink location = %s
istximagesrc name = xsrc use-damage = false ! videorate ! video/x-raw-rgb,framerate = 10/1 ! ffmpegcolorspace ! videoscale method = 1 ! video/x-raw-yuv,width = %d,height = %d ! mix.sink_0
v4l2src name = camsrc device = %s ! ffmpegcolorspace ! videorate ! video/x-raw-yuv,framerate = 10/1,width = 320,height = 240 ! queue ! videoscale ! ffmpegcolorspace ! video/x-raw-yuv,height = %d,height = %d ! mix.sink_1
alsasrc name = asrc ! queue ! audioconvert ! vorbisenc ! mux.""" % \
    (out_file, out_w, out_h, v4l_device, cam_w, cam_h))

mix = p.get_by_name("mix")
cam_pad = mix.get_pad("sink_1")
cam_pad.set_property("xpos", cam_x)
cam_pad.set_property("ypos", cam_y)
cam_pad.set_property("alpha", cam_opacity)
cam_pad.set_property("zorder", 1)


p.set_state(gst.STATE_PLAYING)
print "Capturing to %s ..." % out_file

loop = gobject.MainLoop()
try:
  loop.run()
except KeyboardInterrupt:
  pass 

print "Stopping capture ..."
clean_shutdown(p)
p.set_state(gst.STATE_NULL)
print "Done. Saved as %s" % out_file
