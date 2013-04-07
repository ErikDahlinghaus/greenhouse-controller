
def server():

	settings = { 
			 'global': {
				'server.socket_host': '0.0.0.0',
				'server.socket_port': 8080,
				'server.socket_host': "",
				'server.socket_file': "",
				'server.socket_queue_size': 5,
				'server.protocol_version': "HTTP/1.0",
				'server.log_to_screen': True,
				'server.log_file': "",
				'server.reverse_dns': False,
				'server.thread_pool': 10,
				'server.environment': "development"
			 },
			 '/admin': {
				'session_authenticate_filter.on' :True
			 },
			 '/static': {
				'static_filter.on': True,
				'static_filter.dir': '/host/web/static'
			 },
			 '/images': {
				'static_filter.on': True,
				'static_filter.dir': '/host/web/images'
			 },
			 '/js': {
				'static_filter.on': True,
				'static_filter.dir': '/host/web/js'
			 }
		  }
	  
	return settings