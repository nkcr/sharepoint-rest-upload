#! /bin/bash

# Picam must be running
# add in `/etc/rc.local`:
# ```
# /home/pi/picam/picam --alsadev hw:1,0 &
# exit 0
# ```

PICAM_DIR=/home/pi/picam

# Start recording:
touch 