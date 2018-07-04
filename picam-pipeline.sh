#! /bin/bash

# Exit as soon as a command fail
set -e

# Check param
if [ $# -eq 0 ]
  then
    echo "[error] Need time argument. Usage: ./picam-pipeline <time>"
    exit 1
fi

PICAM_DIR=/home/pi/picam
SCRIPT_LOCATION="/home/pi/sharepoint-rest-upload"

echo "launch record script..."
$SCRIPT_LOCATION/picam-record.sh $1

echo "get last record..."
LAST_RECORD=`ls -t $PICAM_DIR/archive | head -1`

# Check if LAST_RECORD is empty
if [ -z "$LAST_RECORD" ]
  then
    echo "[error] No record found in $PICAM_DIR/archive"
    exit 1
fi

# Convert the record
echo "convert the record..."
today=`date +%Y-%m-%d-%H-%M-%S`
destination="$PICAM_DIR/archive/Louange-du-$today.mp4"
ffmpeg -y -i $PICAM_DIR/archive/$LAST_RECORD -c:v copy -c:a copy -bsf:a aac_adtstoasc $destination
echo "...done!"

echo "check presence of converted file..."
if [ ! -f $destination ]; then
    echo "[error] no converted file found at $destination"
    exit 1
fi

echo "launch upload script..."
python3 $SCRIPT_LOCATION/rest-upload.py $destination

echo "...delete files"
rm $destination $LAST_RECORD

echo "that was a long journey..."
echo "...I am done!"