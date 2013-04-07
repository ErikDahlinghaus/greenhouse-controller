import cherrypy
import os

import sys
sys.path.append('../pylib')
from sqlhelper import sqlhelper
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader('templates'))
sql = sqlhelper('host')

		
info = { 'title' : 'Our Room',
		}
		
links = { 
			'rawdata' : {
				'title' : 'Raw Data',
				'href' : '/'
			},
			'newpage' : {
				'title' : 'New Page',
				'href' : '/newpage'
			},
		}

class Root(object):

	def index(self, time='1'):
		if (time.isdigit() == False):
			time=1
		tmpl = env.get_template('index.html')
		
		(data, runtime) = sql.get_all_data(time_interval=time)
		
		return tmpl.render(info=info, links=links, data=data, time=time, runtime=runtime)
	index.exposed = True

	def default(self, *args):
		return "Extra path info: %s" % repr(args)
	default.exposed = True
		
		
		
		
		
class Newpage(object):
		
	def index(self, **kwargs):
	
		if cherrypy.request.method == 'POST':
			self.editTitle(kwargs)
	
	
		tmpl = env.get_template('newpage.html')
		return tmpl.render(info=info, links=links)
	index.exposed = True
		

	def default(self, *args):
		return "Extra path info: %s" % repr(args)
	default.exposed = True

		
	def editTitle(self, args):
		links['newpage']['title'] = str(args['title'])
		return
		







def quickstart(config=None):
	cherrypy.config.update(config)
	
	if hasattr(cherrypy.engine, "signal_handler"):
		cherrypy.engine.signal_handler.subscribe()
	if hasattr(cherrypy.engine, "console_control_handler"):
		cherrypy.engine.console_control_handler.subscribe()
		
		
	cherrypy.engine.start()
	cherrypy.engine.block()


staticsetting = { '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': '/host/web/static'}}

cherrypy.tree.mount(Root(), "/", config=staticsetting)
cherrypy.tree.mount(Newpage(), "/newpage", config=staticsetting)
		
		
# cherrypy.root = Root()
# cherrypy.root.newpage = Newpage()
	 
	 
# cherrypy.config.update({'server.socket_host': '0.0.0.0',
                            # 'server.socket_port': 8080, })					
# cherrypy.config.update({'/images': {'tools.staticdir.on': True,
        # 'tools.staticdir.dir': '/host/web/images'}})
# cherrypy.config.update({'/js': {'tools.staticdir.on': True,
        # 'tools.staticdir.dir': '/host/web/js'}})
# cherrypy.config.update({'/static': {'tools.staticdir.on': True,
        # 'tools.staticdir.dir': '/host/web/static'}})
# cherrypy.config.update({'engine.autoreload_on': True})

settings = { 
         'global': {
			'server.socket_host': '0.0.0.0',
            'server.socket_port': 8080
         },
         # '/static': {
            # 'tools.staticdir.on': True,
            # 'tools.staticdir.dir': '/host/web/static'
		 # },
         # '/images': {
            # 'tools.staticdir.on': True,
            # 'tools.staticdir.dir': '/host/web/images'
         # },
      }
	  

	  		
quickstart(settings)
# cherrypy.quickstart(rootpage, '/')
