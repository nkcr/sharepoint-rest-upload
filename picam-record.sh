#! /bin/bash

#
# This script starts picam and record for a given time
# Take in param the number of seconds
# Usage: ./picam-jobs 10
#
# Wait on log: https://superuser.com/questions/270529/monitoring-a-file-until-a-string-is-found
#

# Exit as soon as a command fail
set -e

# Check param
if [ $# -eq 0 ]
  then
    echo "[error] Need time argument. Usage: ./picam-job <time>"
    exit 1
fi

PICAM_DIR=/home/pi/picam
cd $PICAM_DIR

# Initialize log file
echo -n > logs.txt

echo "make dirs..."
./make_dirs.sh
echo "start picam..."
./picam --alsadev hw:1,0 &>$PICAM_DIR/logs.txt & # Forked process
PICAM_PID=$!

# Wait a bit for picam to be ready
#sleep 5
echo "wait for picam to be ready..."
( tail -f $PICAM_DIR/logs.txt & ) | timeout 5  grep -q "capturing started" || # Prevent timeout from exiting
exit_status=$?

# If we reached the timeout, $? contains 124, otherwise 0
if [[ $exit_status -eq 124 ]]; then
    echo "[error] Didn't detect 'capturing started' on logs..."
    echo "[error] Failed to start picam..."
    echo "stop child processes..."
    #trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT
    pkill -P $$
    echo "...done!"
    exit 1
fi

echo "start recording..."
touch hooks/start_record
sleep $1
echo "stop recording..."
touch hooks/stop_record

ls archive

# Ensure we end child process
echo "stop child processes..."
#trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT
pkill -P $$
echo "...done!"
