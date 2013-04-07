#!/usr/bin/python

import sys
sys.path.append('./pylib')

from sqlhelper import sqlhelper

import subprocess

import time
import ast

from classes import Node, Zone, node_types, clientSocket, serverSocket, socketListener
from zone_runnable import zoneThread

messageTypes = { 'sensor' : 1, 'output' : 2, 'startup' : 255, }


# Do some stuff
messages = []

# Figure out which zones exists
# populate the nodes into zones
# Redo anything that needs to be redone (remake the zones dictionaries)

nodeOne = Node(id=1, name='Node 1 - Sensor', type=node_types['sensor'], addr=240)
nodeTwo = Node(id=2, name='Node 2 - Output', type=node_types['output'], addr=112)

zoneOne = Zone(id=1, name='Seedling')
zoneOne.addSensorNode(nodeOne)
zoneOne.addOutputNode(nodeTwo)

zones = [ zoneOne, ]

zoneThreads = []







def startZoneThread(zone):
	thread = zoneThread(zone)
	thread.setZone(zone)
	zoneThreads.append( (zone.getName(), thread) )
	thread.start()
	return thread

	
	
	
	
	
def getThreadFromAddr(nodeAddr):
	for name, thread in zoneThreads:
		zone = thread.getZone()
		for node in zone.getAllNodes():
			if( nodeAddr == node.getAddr() ):
				workingThread = thread
				return workingThread
	return None
	
	
	
	
	
	
def routeMessage(message):
	# route message
	# message = message
	# print 'Message looks like:',message
	items = []
	nodeAddr = message[0]
	messageType = message[1]
	for i in range(2,len(message)):
		items.append(ast.literal_eval(str(message[i])))
				
		
	if( messageType == messageTypes['startup'] ):
		print 'Node['+nodeAddr+'] -- Target starting up'
		return True
	
	elif( messageType == messageTypes['output'] ):
		workingThread = getThreadFromAddr(nodeAddr)
		workingThread.outputReceived = True
		# Probably send some other data here
		workingThread = None
		return True
		
	elif( messageType == messageTypes['sensor'] ):
		workingThread = getThreadFromAddr(nodeAddr)
		workingThread.recordData(tuple(items))
		workingThread.dataGathered = True
		# Probably send some other data here
		workingThread = None
		return True
				
	else:
		return False
	
	
	
	






# For each zone, launch a zone_runnable, which scans the nodes for data, and then changes the output nodes
# each zone runnable has it's own PID (which is persistant, maybe in a persistant DB?) which holds the i and d running tallies and stuff.


try:

	socListener = socketListener()
	socListener.start()
	# print socListen.isAlive()

	for zone in zones:
		startZoneThread(zone)

	while( True ):
	
		# print 'At beginning of loop'
	
		# Message routing
		_messages = socListener.getMessages()
		# print 'Temp messages:',_messages
		if( _messages ):
			for mes in _messages:
				messages.append(mes)
		if( messages ):
			i = 0
			for message in messages:
				# Do something with messages
				# print i, message
				i = i+1				
				
				if( routeMessage(message) ):
					messages.remove(message)
	
		
		
		
		# Check to make sure threads are still running (works)
		# print 'Checking threads'
		for name, thread in zoneThreads:
			# print name, thread.isAlive()
			if( not thread.isAlive() ):
				print 'Restarting', name
				zone = thread.zone
				zoneThreads.remove((name, thread))
				thread = startZoneThread(zone)
			else:
				# print name, 'is running'
				pass
				
		if( not socListener.isAlive() ):
			print 'Restarting socket listener'
			socListener.start()
				
		# print 'Done checking threads'
		
		time.sleep(3)

	
	
	
except KeyboardInterrupt:
	print '-( ...Exiting...'
	socListener.killSelf = True
	for name, thread in zoneThreads:
		thread.killSelf = True
	




