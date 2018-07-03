#! /bin/bash

# Picam must be running
# add in `/etc/rc.local`:
# ```
# /home/pi/picam/picam --alsadev hw:1,0 &
# exit 0
# ```

PICAM_DIR=/home/pi/picam

# Start picam
$PICAM_DIR/make_dirs.sh
nohup $PICAM_DIR/picam --alsadev hw:1,0 &>$PICAM_DIR/logs.txt &

# Start recording:
touch $PICAM_DIR/hooks/start_record