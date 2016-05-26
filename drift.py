import config
import logging
import signal
from threading import Event
moduleLogger = logging.getLogger('drift')

from jobs import CreateJob, WorkerPool
from discover import searchForFiles
import time

EXIT = Event()
pool = WorkerPool()

def HandleShutdown():
	EXIT.set()
	pool.join()

signal.signal(signal.SIGTERM, HandleShutdown) # Setup signal handling
pool.startProcessing()
oldList = set()
while not EXIT.isSet():
	newCount = 0
	for entry in searchForFiles(config.INPUT_DIR):
		job = CreateJob(entry)
		if not pool.inQueue(job):
			pool.addJob(job)
			moduleLogger.debug('Added Job for %s'%entry)
			newCount += 1
	moduleLogger.info('%i new files added - %i in queue'%(newCount, pool.queueLength()))
	time.sleep(float(config.POLL_TIME))


# Search for fies in need of conversion




# Convert those files
