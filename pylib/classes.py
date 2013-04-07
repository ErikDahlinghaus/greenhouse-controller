#!/usr/bin/python

import sys
# sys.path.append('/home/host/pylib')

from sqlhelper import sqlhelper
import subprocess
import socket
import time
import threading
import ast

node_types = { 'sensor' : 1, 'output' : 2 }
data_types = { 'temperature' : 1, 'humidity' : 2, 'co2' : 3 }
zones = { 'Seedling' : 1, }

class Zone(object):
	
	id = None
	name = None
	sensor_nodes = []
	output_nodes = []
	
	def __init__(self, id, name):
		self.id = id
		self.name = name
		
	def getID(self):
		return self.id
	
	def getName(self):
		return self.name
		
	def getSensorNodes(self):
		return self.sensor_nodes
		
	def getOutputNodes(self):
		return self.output_nodes
		
	def getAllNodes(self):
		allNodes = self.sensor_nodes + self.output_nodes
		return allNodes
	
	def addSensorNode(self, node):
		self.sensor_nodes.append(node)
	
	def addOutputNode(self, node):
		self.output_nodes.append(node)
		
class Node(object):
	id = None
	name = None
	addr = None
	type = None
	PID = None
	
	def __init__(self, id, name, type, addr, PID=None):
		self.id = id
		self.name = name
		self.type = type
		self.addr = addr
		self.PID = PID
		
	def getID(self):
		return self.id
	
	def getName(self):
		return self.name
		
	def getType(self):
		return self.type
		
	def getAddr(self):
		return self.addr

class clientSocket(object):

	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	port = 1337
	
	def __init__(self, port):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.port = port
		self.sock.settimeout(1)
		print 'Client Socket...'

	def connect(self):
		self.sock.connect(("localhost", self.port))
		return

	def read(self):
		try:
			(clientsocket, address) = self.sock.accept()
			message = clientsocket.recv(512)
			message = ast.literal_eval(message)
			clientsocket.close()
			return tuple(message[0])
		except socket.timeout:
			return
		
	def send(self, *mes):
		self.sock.send(str(mes))
		return

	def disconnect(self):
		self.sock.shutdown(socket.SHUT_RDWR)
		self.sock.close()
		return
				
class serverSocket(object):
	
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	port = 1337
	
	def __init__(self, port):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.port = port
		self.sock.settimeout(1)
		print 'Server Socket...'

	def connect(self):
		self.sock.bind(("localhost", self.port))
		self.sock.listen(5)
		return

	def read(self):
		try:
			(clientsocket, address) = self.sock.accept()
			message = clientsocket.recv(512)
			if( message ):
				message = ast.literal_eval(message)
				clientsocket.close()
				return tuple(message[0])
			else:
				return
		except socket.timeout:
			return
		
	def send(self, *mes):
		self.sock.send(str(mes))
		return

	def disconnect(self):
		self.sock.shutdown(socket.SHUT_RDWR)
		self.sock.close()
		return


	
class socketListener(threading.Thread):
	
	socket = serverSocket(2000)
	messages = []
	killSelf = False
	
	def __init__(self):
		threading.Thread.__init__(self)
		self.socket.connect()	
		
	def run(self):
		while( not self.killSelf ):
			message = self.socket.read()
			# print 'Socket recieved:',message
			if( message ):
				self.messages.append(message)
				
		self.end()
		return
	
	def getMessages(self):
		temp = self.messages
		self.messages = []
		return temp
	
	def end(self):
		self.socket.disconnect()
		return
	
	
	
	
	
	
	
	
	
	
