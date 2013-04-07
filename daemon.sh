#!/bin/bash

can_network_start="screen -DmS can2db /home/host/can2db/can2db can0,1:1"
web_server_start="screen -DmS website /home/host/web/startweb.sh"
info_gather_start="screen -DmS info python /home/host/daemon.py"


can2db_proc="can2db"
website_proc="website"
info_proc="info"

function daemon {

	# Make sure the can dumping program is running
	if screen -ls | grep $can2db_proc >/dev/null
			then
				echo 'can2db is running'
			else
				echo 'Starting can2db'
				$can_network_start &
	fi
	
	
	# Make sure website is running (temp)
	if screen -ls | grep $website_proc >/dev/null
			then
				echo 'website is running'
			else
				echo 'Starting website'
				$web_server_start &
	fi
	
	# Make sure gathering is happening
	if screen -ls | grep $info_proc >/dev/null
			then
				echo 'gathering is happening'
			else
				echo 'Starting gathering'
				$info_gather_start &
	fi

}

daemon


