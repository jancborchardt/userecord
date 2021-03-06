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
- Reduce output file resolution with the width in pixels as argument.
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


def main(action = None):
    if action is None:
        # Recording name
        out_file = "recording-"
        count = 1
        while(os.path.isfile(out_file + str(count) + ".ogv")):
            count = count + 1
        
        global out_file
        out_file += str(count)
        out_file += ".ogv"

        for arg in sys.argv:
            if re.search(".ogv", arg):
                if(os.path.isfile(arg)):
                    print "File %s already exists!" % arg
                else:
                    out_file = arg


        # Screen dimensions
        out_w = int(runBash("xdpyinfo | grep dimensions | cut -d' ' -f7 | cut -d'x' -f1"))
        out_h = int(runBash("xdpyinfo | grep dimensions | cut -d' ' -f7 | cut -d'x' -f2"))

        for arg in sys.argv:
            if arg.isdigit():
                if int(arg) > out_w:
                    print "Can not scale video up!"
                else:
                    arg = int(arg)
                    out_h = out_h * arg / out_w
                    out_w = arg


        # Camera video
        cam = True
        cam_w = 320
        cam_h = 240
        # TODO: Implement camera video scaling as well
        # v4l2src seems to have problems with other values
        #cam_w = round(out_w / 4)
        #cam_h = round(cam_w * 3/4)
        cam_opacity = 0.8
        v4l_device = "/dev/video0"
        cam_x = out_w - cam_w
        cam_y = out_h - cam_h

        for arg in sys.argv:
            if arg == "left":
                cam_x = 0
            elif arg == "top":
                cam_y = 0
            elif arg == "nocam":
                cam = False
                cam_opacity = 0 # hack, TODO: deactivate cam directly

        for arg in sys.argv:
            if arg == "shift":
                if cam_x == 0:
                    cam_x += cam_w
                else:
                    cam_x -= cam_w

        global p
        # Do it!
        p = gst.parse_launch("""videomixer name = mix ! ffmpegcolorspace ! queue ! theoraenc ! oggmux name = mux ! filesink location = %s
        istximagesrc name = xsrc use-damage = false ! videorate ! video/x-raw-rgb,framerate = 10/1 ! ffmpegcolorspace ! videoscale method = 1 ! video/x-raw-yuv,width = %d,height = %d ! mix.sink_0
        v4l2src name = camsrc device = %s ! ffmpegcolorspace ! videorate ! video/x-raw-yuv, framerate = 10/1, width = %d, height = %d ! queue ! videoscale ! ffmpegcolorspace ! video/x-raw-yuv,height = %d,height = %d ! mix.sink_1
        alsasrc name = asrc ! queue ! audioconvert ! vorbisenc ! mux.""" % \
            (out_file, out_w, out_h, v4l_device, cam_w, cam_h, cam_w, cam_h))

        mix = p.get_by_name("mix")
        cam_pad = mix.get_pad("sink_1")
        cam_pad.set_property("xpos", cam_x)
        cam_pad.set_property("ypos", cam_y)
        cam_pad.set_property("alpha", cam_opacity)
        cam_pad.set_property("zorder", 1)


        p.set_state(gst.STATE_PLAYING)
        print "Capturing %sx%s video to %s ..." % (out_w, out_h, out_file)

        loop = gobject.MainLoop()
        try:
          loop.run()
        except KeyboardInterrupt:
          pass 
    else:
        print "Stopping capture ..."
        clean_shutdown(p)
        p.set_state(gst.STATE_NULL)
        print "Successfully saved as %s" % out_file

        

    
    
if __name__ == "__main__":
    main()
