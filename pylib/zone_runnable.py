#!/usr/bin/python

import sys
import os
sys.path.append('/home/host/pylib')

from sqlhelper import sqlhelper
from pid import PID

import time
import threading
import classes
import subprocess



# This is what a zone does, basically the loop through all the shit.
# Gather data, do PID response



class zoneThread(threading.Thread):
	
	dataGathered = False
	outputReceived = False
	zone = None;
	killSelf = False;	
	
	currentData = (0, 0, 0)
	
	temperature = PID(kp=0.8, ki=0.2, setpoint=80)
	humidity = PID(kp=0.8, ki=0.2, setpoint=25)
	co2 = PID(kp=0.8, ki=0.2, setpoint=1000)
	
	PIDs = [temperature, humidity, co2]
	
	def __init__(self, zone):
		threading.Thread.__init__(self)
		self.zone = zone
		# self.PID = PID(zone)
		
	def run(self):
		if( self.zone == None ):
			print 'Something went wrong, no zone attached to zone thread.\n'
			return
		
		
		
		while( not self.killSelf ):
			self.doPoll()
		

		return
		
	def setZone(self, zone):
		self.zone = zone
		
	def getZone(self):
		return self.zone
		
	def recordData(self, data):
		print 'Data Recorded:',data
		self.currentData = data
		
	def sendMessage(self, addr, one, two, three):
		cmd = ["cansend","can0","-i",str(addr),str(one),str(two),str(three)]
		with open(os.devnull, "w") as f:
			subprocess.Popen(cmd, stdout=f).wait()	
		return
	
	def sendRequest(self, addr):
		cmd = ['cansend', 'can0', '-i', str(addr), '-r']
		with open(os.devnull, "w") as f:
			subprocess.Popen(cmd, stdout=f).wait()	
		return
	
	
	
	def doPoll(self):
		for node in self.zone.getSensorNodes():
			self.sendRequest(node.getAddr())
			# Request approval
			timeout = 100
			i = 0
			while( (not self.dataGathered) and (i != timeout)  ):
				time.sleep(.1)
				i = i+1
				
			if( i == timeout ):
				print 'Timeout'
			else:
				print 'Data Gathered'
				self.dataGathered = False
		
		
		
		
								
		for node in self.zone.getOutputNodes():		
			# Get the data
			# print 'currentData:',self.currentData
			(temp, hum, co2) = self.currentData
			temp_val = self.temperature.doPID(temp)
			hum_val = self.humidity.doPID(hum)
			co2_val = self.co2.doPID(co2)
			
			self.sendMessage(node.getAddr(), temp_val, hum_val, co2_val)
			
			
			timeout = 100
			i = 0
			while( (not self.outputReceived) and (i != timeout) ):
				time.sleep(.1)
				i = i+1
				
			if( i == timeout ):
				print 'Timeout'
			else:				
				print 'Output received'
				self.dataGathered = False
				
		return
