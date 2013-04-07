#!/bin/bash

can_stop="ip link set can0 down"
can_setup="ip link set can0 type can bitrate 100000 triple-sampling on"
can_start="ip link set can0 up"

logfile="/home/host/startup/log"

run_daemon="/home/host/daemon.sh"

echo ''
echo ''
echo 'Starting...'
echo 'Setting up CAN0' >$logfile
$can_stop >>$logfile
$can_setup >>$logfile
echo 'Starting CAN0' >>$logfile
$can_start >>$logfile

echo 'Running daemon for first time' >>$logfile
$run_daemon >>$logfile
echo 'Done with startup'
