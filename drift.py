import config
import logging
import signal
from threading import Event
moduleLogger = logging.getLogger('drift')

from jobs import CreateJob, WorkerPool
from discover import BuildCoversionList
import time

EXIT = Event()
pool = WorkerPool()

def HandleShutdown():
	EXIT.set()
	pool.join()

pool.startProcessing()
oldList = set()
while not EXIT.isSet():
	fileList = BuildCoversionList(config.INPUT_DIR)
	newCount = 0
	for entry in fileList:
		if not entry in oldList:
			job = CreateJob(entry)
			pool.addJob(job)
			moduleLogger.debug('Added Job for %s'%entry)
			newCount += 1
	moduleLogger.info('%i new files added - %i in queue'%(newCount, pool.queueLength()))
	oldList = oldList.union(fileList)
	time.sleep(config.POLL_TIME)


# Search for fies in need of conversion




# Convert those files
