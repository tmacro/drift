def readFromConfig(key, path = 'config.json', default = None): 	# Reads a value from the config file in json format
	try:														# Default will be returned if the given key does not exist
		with open(path) as configFile:							#	or if there is ANY error reading the config file
			config = json.load(configFile)
		return config.get(key, default)
	except Exception as e:
		moduleLogger.error('Error reading %s from config file %s'%(key, path))
		moduleLogger.exception(e)

	return default

def parseLogLevel(text, default = 30):
	text = text.lower()
	levelValues = {
	 'critical' : 50,
		'error' : 40,
	  'warning' : 30,
		 'info' : 20,
		'debug' : 10
	}
	return levelValues.get(text, default)
