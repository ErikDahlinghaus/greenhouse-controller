#!/usr/bin/python

import sys
sys.path.append('../pylib')

from sqlhelper import sqlhelper
import socket
from classes import clientSocket


sql = sqlhelper('host')

sock_con = False

#Make this send socket data to daemon.py

socket = clientSocket(2000)
	

def bin(x, digits=0):
	oct2bin = ['000','001','010','011','100','101','110','111']
	binstring = [oct2bin[int(n)] for n in oct(x)]
	return ''.join(binstring).lstrip('0').zfill(digits)
	
def store_data():	

	temperature = get_temp()
	
	(humidity, humerror) = get_humidity()
	if( humerror != 0 ):
		humidity_error_mes(humerror);

		
	co2 = get_co2()
	
	if( float(temperature) > 125 ):
		print 'NODE[%s] -- Invalid Data, aborting...' % hex(node)
		return
		
	
	message.append(temperature)
	message.append(humidity)
	message.append(co2)
	
	sql.store_data(node, 'temperature', temperature)
	sql.store_data(node, 'humidity', humidity)
	sql.store_data(node, 'co2', co2)	
	
	print 'NODE[%s] -- Data stored' % hex(node)
	return
	

def output_mes():
	for item in bytes:
		message.append(str(item))
	print 'NODE[%s] -- PLUG1 [%s] | PLUG2 [%s] | PLUG3 [%s]' % (hex(node), bytes[0], bytes[1], bytes[2])
	return
	
def startup_mes():
	print 'NODE[%s] -- Starting up' % hex(node)
	return

def default_mes():
	print 'NODE[%s] -- An error has occured (DUMP: %s)' % (hex(node), [hex(b) for b in bytes])
	end("Random Error (DUMP: [%s] %s)" % (hex(node), [hex(b) for b in bytes]))
	
def humidity_error_mes(error):
	print 'NODE['+hex(node)+'] -- Humidity Error: '+str(error)
	end("Humidity Error (%s)" % str(error))

def get_temp():
	value = bytes[0]
	value = value << 8
	value = value + bytes[1]
	value = value * .0625
	value = (value * 1.80) + 32
	value = "%.2f" % value
	print 'NODE[%s] -- Temperature is %s degrees F' % (hex(node), value)
	return value
	
def get_humidity():
	error = (bytes[2]>>6)
	value = (bytes[2]<<2)
	value = (value>>2)
	value = value << 8
	value = value + bytes[3]
	div = float(2**14 - 2)
	value = (float(value) / div)
	value = value * 100
	value = "%.2f" % value
	print 'NODE['+hex(node)+'] -- Humidity is '+value+'% RH'
	return (value, error)
	
def get_co2():
	value = bytes[4]
	value = value << 8
	value = value + bytes[5]
	print 'NODE[%s] -- CO2 concentration is %s PPM' % (hex(node), value)
	return value
	
def end(string=None):
	socket.send(message)
	socket.disconnect()
	sql.close_connection()
	sys.exit(string)
		

socket.connect()
		
# Init
bytes = []
node = int(sys.argv[1], 16)
request_type = int(sys.argv[2], 16)
for i in range(3,len(sys.argv)):
	bytes.append(int(sys.argv[i], 16))
message = []
message.append(node)
message.append(request_type)
	
# Switch DICT
{
	1 : store_data,
	2 : output_mes,
	255 : startup_mes,
}.get(request_type, default_mes)()


end()
