sectionConfig = config.section('hashtag')
public = sectionConfig.option('public', default = False).get()

def apply_script(protocol, connection, config):
	class hashtagConnection(connection):
		def on_login(self, name):
			if name is not None and '#' in name:
				connection.kick(self, "A hashtag (#) in a name is not allowed in this server", public)
			connection.on_login(self, name)
	return protocol, hashtagConnection