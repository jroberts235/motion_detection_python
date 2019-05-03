#!/usr/bin/env python

import os
import cv2
import sys
import threading
import subprocess
from datetime import datetime

# The two main parameters that affect movement detection sensitivity
# are BLUR_SIZE and NOISE_CUTOFF. Both have little direct effect on
# CPU usage. In theory a smaller BLUR_SIZE should use less CPU, but
# for the range of values that are effective the difference is
# negligible. The default values are effective with on most light
# conditions with the cameras I have tested. At these levels the
# detectory can easily trigger on eye blinks, yet not trigger if the
# subject remains still without blinking. These levels will likely be
# useless outdoors.
BLUR_SIZE = 3
NOISE_CUTOFF = 40
# Ah, but the third main parameter that affects movement detection
# sensitivity is the time between frames. I like about 10 frames per
# second. Even 4 FPS is fine.
FRAMES_PER_SECOND = 10

cam = cv2.VideoCapture(1)
## 320*240 = 76800 pixels
#cam.set(3, 320)
#cam.set(4, 240)
## 640*480 = 307200 pixels
#cam.set(3,640)
#cam.set(4,480)
## 1024*768 = HD
cam.set(3,1024)
cam.set(4,768)

window_name = "delta view"
cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)
window_name_now = "now view"
cv2.namedWindow(window_name_now, cv2.WINDOW_AUTOSIZE)


# calculate Region Of Interest
def crop(r, im):
    return im[int(r[1]):int(r[1]+r[3]), int(r[0]):int(r[0]+r[2])]

# Convert to GreyScale and apply Gausian Blur
def transform(image):
    image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    image = cv2.blur(image, (BLUR_SIZE, BLUR_SIZE))
    return image

def trigger():
    # Make a lazy man's asyncronous http call
    subprocess.Popen(['curl http://localhost:5000/trigger &> /dev/null'], shell=True)
    # Make a BLOCKING call (advantage is that it won't send multiple trigger req during the controller's sleep value)
    #os.system('curl http://localhost:5000/trigger')

# Stabilize the detector by letting the camera warm up and
# seeding the first frames.

frame_now = cam.read()[1]
frame_now = cam.read()[1]

# Select ROI
showCrosshair = False
fromCenter = False

# Create a new window when selcting ROI
#roi = cv2.selectROI("ROI view", frame_now, fromCenter, showCrosshair)
# Use the Now widow for ROI selection
roi = cv2.selectROI("now view", frame_now, fromCenter, showCrosshair)
# Hardcoded value
#roi = (323, 119, 354, 277)

# Print out the ROI so that it can be hard coded later
print('ROI Selected: {}'.format(roi))

frame_now = transform(frame_now)
frame_prior = frame_now

delta_count_last = 1


while True:
    frame_delta = cv2.absdiff(crop(roi, frame_prior), crop(roi, frame_now))
    frame_delta = cv2.threshold(frame_delta, NOISE_CUTOFF, 255, 3)[1]
    delta_count = cv2.countNonZero(frame_delta)

    # Visual detection statistics output.
    # Normalize improves brightness and contrast.
    # Mirror view makes self display more intuitive.
    cv2.normalize(frame_delta, frame_delta, 0, 255, cv2.NORM_MINMAX)
    frame_delta = cv2.flip(frame_delta, 1)

    # OSD of Delta
    #cv2.putText(frame_delta, "DELTA: %d" % (delta_count),
    #        (5, 15), cv2.FONT_HERSHEY_PLAIN, 0.8, (255, 255, 255))

    # Show Delta window
    cv2.imshow(window_name, frame_delta)

    frame_delta = cv2.threshold(frame_delta, 92, 255, 0)[1]
    dst = cv2.flip(crop(roi, frame_now), 1)
    dst = cv2.addWeighted(dst, 1.0, frame_delta, 0.9, 0)

    # Show Now window
    cv2.imshow(window_name_now, dst)

    # Stdout output.
    # Only output when there is new movement or when movement stops.
    # Time codes are in epoch time format.
    if (delta_count_last == 0 and delta_count != 0):
        trigger()
        sys.stdout.write('MOVEMENT {}\n'.format(datetime.now().strftime('%H:%M:%S')))
        sys.stdout.flush()
    elif delta_count_last != 0 and delta_count == 0:
        sys.stdout.write('STILL    {}\n'.format(datetime.now().strftime('%H:%M:%S')))
        sys.stdout.flush()
    delta_count_last = delta_count

    # Advance the frames.
    frame_prior = frame_now
    frame_now = cam.read()[1]
    frame_now = transform(frame_now)

    # Wait up to 10ms for a key press. Quit if the key is either ESC or 'q'.
    key = cv2.waitKey(10)
    if key == 0x1b or key == ord('q'):
        cv2.destroyWindow(window_name)
        break

# vim: set ft=python fileencoding=utf-8 sr et ts=4 sw=4 : See help 'modeline'
