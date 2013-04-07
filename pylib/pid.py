#!/usr/bin/python

import sys
sys.path.append('/home/host/pylib')
import subprocess
from sqlhelper import sqlhelper
import socket
import time
import ast

class simpleLimits(object):

	sql = None
	sock = None
	limits = None
	node_addr = None
	node_id = None
	zone_id = None
	sensor_node_id = None
	
	def __init__(self, node_addr):
		self.node_addr = node_addr
		self.sql = sqlhelper('host')
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.get_limits()
		self.node_id = self.sql.node_id_from_addr(node_addr)
		self.zone_id = self.sql.get_zone_from_node(node_addr)
		sensor_node_id = self.sql.sensor_node_from_zone(self.zone_id)
		
	def socket_connect(self):
		self.sock.connect(("localhost", 1337))
		return
		
	def socket_send(self, addr):
		self.sock.send(str(addr))
		return

	def socket_close(self):
		self.sock.close();
		return
	
	def get_limits(self):
		self.limits = self.sql.get_limits(self.node_addr)
		return

	def sendMessage(self, one, two, three):
		cmd = ["cansend","can0","-i",str(self.node_addr),str(one),str(two),str(three)]
		subprocess.Popen(cmd).wait()		
		return
		
	def check_limits(self):
		temp_h = float(self.limits[0])
		temp_l = float(self.limits[1])
		humidity_h = float(self.limits[2])
		humidity_l = float(self.limits[3])
		co2_h = int(self.limits[4])
		co2_l = int(self.limits[5])
		
		temp = 0
		humidity = 0
		co2 = 0

		
		last_temp = self.sql.get_last(self.zone_id, 1)
		last_humidity = self.sql.get_last(self.zone_id, 2)
		last_co2 = self.sql.get_last(self.zone_id, 3)
		
	
		if( not (temp_l < last_temp < temp_h) ):
			temp = 1
		# print 'Temps H %s, Cur %s, L %s, Pin %s' % (temp_h, last_temp, temp_l, temp)
			
		if( not (humidity_l < last_humidity < humidity_h) ):
			humidity = 1
		# print 'Humidity H %s, Cur %s, L %s, Pin %s' % (humidity_h, last_humidity, humidity_l, humidity)
		
		if( not (co2_l < last_co2 < co2_h) ):
			co2 = 1
		# print 'Co2 H %s, Cur %s, L %s, Pin %s' % (co2_h, last_co2, co2_l, co2)
			
		# print temp, humidity, co2
		
		self.sendMessage(temp, humidity, co2)
		return

		
#Make PID Class

class PID(object):

	kP = 0.0
	kI = 0.0
	kD = 0.0
	
	P = 0.0
	I = 0.0
	D = 0.0
	
	error = 0.0
	previousError = 0.0
	
	setpoint = 0.0
	
	integral = 0.0
	
	inverted = False
	
	lastTime = time.time()
	dt = time.time()
	
	
	def __init__(self, kp=1, ki=0, kd=0, setpoint=20, inverted=False):
		self.kP = kp
		self.kI = ki
		self.kD = kd
		self.setpoint = setpoint
		self.inverted = inverted
		return
		
	def doPID(self, measuredValue):
		print 'measuredValue:',measuredValue
		currentTime = time.time()
		self.dt = currentTime - self.lastTime
		if( self.dt > 60 ):
			self.lastTime = currentTime
			return
		self.error = self.setpoint - measuredValue
		self.P = self.error
		if( self.kI ):
			self.I = self.integral + self.error*self.dt
		if( self.kD ):
			self.D = (self.error-self.previousError) / self.dt
		self.previousError = self.error
		output = self.kP*self.P + self.kI*self.I + self.kD*self.D
		self.lastTime = currentTime
		print 'PID Output:',output
		if( self.inverted ):
			output = output * -1
		if( output > 1 ):
			state = 1
		else:
			state = 0
		return state
		
	def changeSetpoint(self, setpoint):
		self.setpoint = setpoint
		return
		
