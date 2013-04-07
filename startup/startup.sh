#!/bin/bash

can_stop="ip link set can0 down"
can_setup="ip link set can0 type can bitrate 100000 triple-sampling on"
can_start="ip link set can0 up"

logfile="log"

run_daemon="../daemon.sh"

echo ''
echo ''
echo 'Starting...'
echo 'Setting up CAN0'
$can_stop
$can_setup
echo 'Starting CAN0'
$can_start

echo 'Running daemon for first time'
$run_daemon
echo 'Done with startup'
