#! /bin/bash

# Exit as soon as a command fail
set -e

PICAM_DIR=/home/pi/picam

$PICAM_DIR/picam-record.sh $1

LAST_RECORD=`ls -t $PICAM_DIR/archive | head -1`

# Check if LAST_RECORD is empty
if [ -z "$LAST_RECORD" ]
  then
    echo "[error] No record found in $PICAM_DIR/archive"
    exit 1
fi

# Convert the record
today=`date +%Y-%m-%d-%Hh`
destination="$PICAM_DIR/archive/Louange du $today.mp4"
ffmpeg -i $PICAM_DIR/archive/$LAST_RECORD -c:v copy -c:a copy -bsf:a aac_adtstoasc $destination

