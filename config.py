import json
import sys
import utils
import logging

BUILT_IN_DEFAULTS = { # These can be overridden in the config file. They are just here so that you don't HAVE to define them and the module still works
			"VERSION": "DEV_BUILD",
			"APP_NAME" : "UNKNOWN",
			"LOGFILE" : None,
			"LOGLVL" : "DEBUG",
			"LOGFMT" : '%(asctime)s %(name)s %(levelname)s: %(message)s',
			"DATEFMT" : '%d-%m-%y %I:%M:%S %p',
			"DEBUGGING" : False,
}


def setupLogging():
	try:
		if not LOGFILE:
			LOGFILE = None
	except Exception as e:
		LOGFILE = None

	args = {
		'level':LOGLVL,
		'format':LOGFMT,
		'datefmt':DATEFMT,
	}
	if LOGFILE:
		args['filename'] = LOGFILE
	else:
		args['stream'] = sys.stderr

	logging.basicConfig(**args)
	logging.info('Starting %s: version %s'%(APP_NAME, VERSION))

def loadConfig(file = 'config.json'):
	with open(file) as configFile:
		loadedConfig = json.load(configFile)

	config = {**BUILT_IN_DEFAULTS, **loadedConfig} # Merge loaded config with the defaults

	config['LOGLVL'] = utils.parseLogLevel(config['LOGLVL']) # Parse the loglvl
	if config['LOGLVL'] <= 10:
		config['DEBUGGING'] = True

	configModule = sys.modules[__name__]	# This is pretty hacky but it works...

	# Set the config values to their respective keys
	for key, value in config.items():
		configModule.__dict__[key] = value	# Dirty Hacks

	return config # Return the config for good measure

CONFIG = loadConfig()
setupLogging()
if DEBUGGING:
	logging.info("Debugging Enabled")
