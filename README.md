# Pongo: an inexpensive UI lab

Andreas Nilsson wrote on http://www.andreasn.se/blog/?p=96

»Ever wish you had your own UI-lab, but can’t build one with all the expensive cameras, big boxes and one-way-mirrors in your house right now?

[enter Pongo]

It catches sound and video from your web cam, records your desktop and merges it together into a ogg file that’s ready to publish on the web.
Hope anyone finds it useful. We’re planning on a more proper UI and something that catches the key and mouse presses.

Big thanks to Daniel (http://www.dgsiegel.net) and Olivier (http://www.tester.ca), who helped me with some initial tests and Jan (http://noraisin.net/~jan/diary), who put together the final python code.«

---

It’s portable, small, fast and only requires Python and Istanbul: http://live.gnome.org/Istanbul
Start recording with »python pongo.py«, stop with Ctrl-c.

---

I picked up this project to learn Python and help push open usability.
As I am just starting out, I am always happy for any help.
You may also want to have a look at the wiki site which inspired this: http://live.gnome.org/UsabilityProject/Whiteboard/UsabilityTestingSuite

---

Current features:
– »catch sound and video from your web cam, record your desktop and merge it together into a ogg file«
– move camera video position with parameters
– scale output video to increase performance
– disable camera video (hackish b/c no priority)

Planned features:
– »proper UI«
    → something similar to Silverback: http://silverbackapp.com/
    → maybe built up on gtk-recordmydesktop: http://recordmydesktop.sourceforge.net/
    → video preview to see if everything is working
    → move camera video position freely
    → »a collection of previous sessions and ability to add some notes to them«
– something that displays keyboard and mouse presses, similar to https://launchpad.net/screenkey but in the background (only on the recording)
– background mode via application indicator or something similar
– separate recording and exporting
    → do not directly stitch screen and webcam video together
    → be able to export different qualities, layouts etc.
