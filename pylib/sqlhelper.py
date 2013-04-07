import MySQLdb as mdb
import sys
import os

from datetime import tzinfo, timedelta, datetime
import time

	
class EST(tzinfo):
	def utcoffset(self,dt):
		return timedelta(hours=-5)
	def tzname(self,dt):
		return "EST"
	def dst(self,dt):
		return timedelta(0)
		
class UTC(tzinfo):
	def utcoffset(self,dt):
		return timedelta(0)
	def tzname(self,dt):
		return "UTC"
	def dst(self,dt):
		return timedelta(0)
		
		
# Make this work...
class sqlhelper(object):

	data_types = { 'temperature': 1, 'humidity': 2, 'co2': 3 }
	
	con = None
	cur = None
	
	node_types = None
	sensor_node_addrs = None
	output_node_addrs = None		
	
	timezone = EST()

	
	def __init__(self, db):
		self.start_connection(db)

	def start_connection(self, db):
		try:
			self.con = mdb.connect('localhost', 
'root', 'blickity', db)
			self.cur = self.con.cursor()
			self.get_info()
			
		except mdb.Error, e:
			print "Error %d: %s" % (e.args[0],e.args[1])
			sys.exit(1)			
			
	def close_connection(self):
		if( self.con ):
			self.con.close()
		self.con = None
		self.cur = None
		
	def execute(self, execString, argList=None):
		tryAgain = True
		data = None
		while( tryAgain ):
			try:
				self.cur.execute(execString, argList)
				data = self.cur.fetchall()
				tryAgain = False
			except mdb.OperationalError, e:
				if( e[0] == 2006 ):
					print 'We caught the exception 2006'
					self.close_connection()
					self.start_connection('host')
					tryAgain = True
				else:
					print 'We caught the exception',e[0]
		return data
			
	def get_info(self):
		execString = ("SELECT * FROM data_types")
		self.data_types = self.execute(execString)
		
		execString = ("SELECT * FROM node_types")
		self.node_types = self.execute(execString)
		
		execString = ("SELECT addr FROM nodes WHERE node_type='1'")
		data = self.execute(execString)
		self.sensor_node_addrs = [line[0] for line in data]
		
		execString = ("SELECT addr FROM nodes WHERE node_type='2'")
		data = self.execute(execString)
		self.output_node_addrs = [line[0] for line in data] 

	def get_data(self, zone=1, node=1, type=None, time_interval=30):
		if( type == None ):
			return 0
		
		execString = ("SELECT `data`.ts "
						",data_types.data_type_name "
						", `data`.value "
						"FROM "
						"`data` "
						"INNER JOIN data_types "
						"ON `data`.data_type = data_types.id "
						"INNER JOIN nodes "
						"ON `data`.node = nodes.id "
						"INNER JOIN zones "
						"ON nodes.zone = zones.id "
						"INNER JOIN node_types " 
						"ON nodes.node_type = node_types.id "
						"WHERE "
						"data_types.data_type_name = %s "
						"AND zones.id = %s "
						"AND nodes.id = %s "
						"AND ts>=DATE_SUB(NOW(), INTERVAL %s MINUTE) "
						"ORDER BY "
						"`data`.ts DESC")
		argList = (type, zone, node, time_interval)
		data = self.execute(execString)
				
		output = []
		
		for line in data:
			utc = line[0]
			time = utc.replace(tzinfo=self.timezone)
			time = time + time.tzinfo.utcoffset(time)
			output += (time.strftime("%b %d %I:%M:%S %p %Z"), line[1], line[2]),

		return(output)
		
	def get_data_typeid(self, zone=1, node=1, type=1, time_interval=30):
		if( type == None ):
			return 0
				
		execString = ("SELECT `data`.ts "
						# ",data_types.data_type_name "
						", `data`.value "
						"FROM "
						"`data` "
						# "INNER JOIN data_types "
						# "ON `data`.data_type = data_types.id "
						# "INNER JOIN nodes "
						# "ON `data`.node = nodes.id "
						# "INNER JOIN zones "
						# "ON nodes.zone = zones.id "
						# "INNER JOIN node_types " 
						# "ON nodes.node_type = node_types.id "
						"WHERE "
						"data.data_type = %s "
						# "AND zones.id = %s "
						# "AND nodes.id = %s "
						# "AND `data`.zone = %s "
						"AND `data`.node = %s "
						"AND ts>=DATE_SUB(NOW(), INTERVAL %s MINUTE) "
						"ORDER BY "
						"`data`.ts DESC ")
		argList = (type, node, time_interval) # zone,
		
		data = self.execute(execString, argList)		

			
		output = []
		
		for line in data:
			utc = line[0]
			time = utc.replace(tzinfo=self.timezone)
			time = time + time.tzinfo.utcoffset(time)
			output += (time.strftime("%b %d %I:%M:%S %p %Z"), line[1]), # , line[2]

		return(output)
		
	def get_all_data(self, zone=1, node=1, time_interval=30):
	
		print ''
		print ''
		millis = int(round(time.time() * 1000))
		print 'Doing SQL queries...'
	
		temp = self.get_data_typeid(type=1,time_interval=time_interval)
		print '\tDone with temps\t\t%d MS' % (int(round(time.time() * 1000))-millis)
		humid = self.get_data_typeid(type=2,time_interval=time_interval)
		print '\tDone with humidity\t%d MS' % (int(round(time.time() * 1000))-millis)
		co2 = self.get_data_typeid(type=3,time_interval=time_interval)
		print '\tDone with co2\t\t%d MS' % (int(round(time.time() * 1000))-millis)
		
		print 'Done doing SQL queries'
		
		print 'Grabbing data from SQL queries...'
		timestamp = [ts for ts, value in temp]
		print '\tDone grabbing times\t%d MS' % (int(round(time.time() * 1000))-millis)
		temps = ["%.2f"%float(value) for ts, value in temp]
		print '\tDone grabbing temps\t%d MS' % (int(round(time.time() * 1000))-millis)
		humids = ["%.2f"%float(value) for ts, value in humid]
		print '\tDone grabbing humidity\t%d MS' % (int(round(time.time() * 1000))-millis)
		co2s = ["%d"%int(value) for ts, value in co2]
		print '\tDone grabbing co2\t%d MS' % (int(round(time.time() * 1000))-millis)
		print 'Zipping...'
		data = zip(timestamp, temps, humids, co2s)
		runtime = (int(round(time.time() * 1000))-millis)
		print 'Done zipping, finished\t\t%d MS' % runtime
		print ''
		print ''
		
		return (data, runtime)
		
		
		
	def get_last(self, node=1, type=None):
		if( type == None ):
			return 0
		
		execString = ("SELECT `data`.value "
						"FROM "
						"`data` "
						"INNER JOIN data_types "
						"ON `data`.data_type = data_types.id "
						"INNER JOIN nodes "
						"ON `data`.node = nodes.id "
						"INNER JOIN zones "
						"ON nodes.zone = zones.id "
						"INNER JOIN node_types " 
						"ON nodes.node_type = node_types.id "
						"WHERE "
						"data.data_type = %s "
#						"AND zones.id = %s "
						"AND nodes.id = %s "
						# "AND ts>=DATE_SUB(NOW(), INTERVAL 15 MINUTE) "
						"ORDER BY "
						"`data`.ts DESC")
		argList = (type, node)
		self.cur.execute(execString, argList)
		data = self.cur.fetchone()
		
		if( data == None ):
			return(0)
		
		return(data[0])
		
	def get_limits(self, node_addr):
		execString = ("SELECT zones.temp_h "
						", zones.temp_l "
						", zones.humidity_h "
						", zones.humidity_l "
						", zones.co2_h "
						", zones.co2_l "
						"FROM "
						"zones "
						"INNER JOIN nodes "
						"ON zones.id = nodes.zone "
						"WHERE "
						"nodes.addr = %s")
		argList = (node_addr)
		self.cur.execute(execString, argList)
		data = self.cur.fetchall()
		data = data[0]
		return(data)
		
	def node_id_from_addr(self, node_addr):
		execString = ("SELECT id FROM nodes WHERE addr = %s")
		argList = (node_addr)
		self.cur.execute(execString, argList)
		node_id = self.cur.fetchall()
		node_id = int(node_id[0][0])
		return node_id
		
	def sensor_node_from_zone(self, zone_id):
		execString = ("SELECT id FROM nodes WHERE zone = %s AND node_type = 1")
		argList = (zone_id)
		self.cur.execute(execString, argList)
		node_id = self.cur.fetchall()
		node_id = int(node_id[0][0])
		return node_id
		
	def get_zone_from_node(self, node_addr):
		execString = ("SELECT zone FROM nodes WHERE addr = %s")
		argList = (node_addr)
		self.cur.execute(execString, argList)
		node_id = self.cur.fetchall()
		node_id = int(node_id[0][0])
		return node_id
		
	def store_data(self, node_addr, type, data):
		type_num = [int(item[0]) for item in self.data_types if item[1] == type]
		type_num = type_num[0]
		
		node = self.node_id_from_addr(node_addr)
		
		execString = ("INSERT INTO data (`node`,`data_type`,`value`) "
						"VALUES (%s, %s, %s)")			
		argList = (node,type_num,data)
		self.cur.execute(execString, argList)
		self.con.commit()
