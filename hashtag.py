from piqueserver.config import config
sectionConfig = config.section('hashtag')
publicConfig = sectionConfig.option('public', default = False)

def apply_script(protocol, connection, config):
	class hashtagConnection(connection):
		def on_login(self, name):
			if name is not None and '#' in name:
				connection.kick(self, "A hashtag (#) in a name is not allowed in this server", publicConfig.get())
			connection.on_login(self, name)
	return protocol, hashtagConnection