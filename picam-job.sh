#! /bin/bash

#
# Wait on log: https://superuser.com/questions/270529/monitoring-a-file-until-a-string-is-found
#

# Exit as soon as a command fail
set -e

PICAM_DIR=/home/pi/picam
cd $PICAM_DIR

# Initialize log file
echo -n > logs.txt

./make_dirs.sh
./picam --alsadev hw:1,1 &>$PICAM_DIR/logs.txt & # Forked process
PICAM_PID=$!

# Wait a bit for picam to be ready
#sleep 5
( tail -f -n0 $PICAM_DIR/logs.txt & ) | timeout 5 grep -q "capeturing started"
exit_status=$?

# If we reached the timeout, $? contains 124, otherwise 0
if [[ $exit_status -eq 124 ]]; then
    echo "Didn't detect 'capturing started' on logs."
    echo "Failed to start picam"
    exit 1
fi

touch hooks/start_record
sleep 10
touch hooks/stop_record

ls archive

# Ensure we end child process
#trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT
kill -- -$PICAM_PID
