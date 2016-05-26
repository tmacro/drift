# Job management goes here
from pipewrench.pipeline import Message
# from pipewrench.fittings import PipeFitting
from pipewrench.screens import Screen
from queue import Queue
import queue
from oset import oset as OrderedSet
import threading
from filters import *
import time
import config
import shlex
import logging
import select
moduleLogger = logging.getLogger('jobs')

class Job(Message):
	def __init__(self, **kwargs):
		self.origin_path = None
		super(Job, self).__init__(**kwargs)

	def __eq__(self, other):
		return other == self.origin_path

	def __hash__(self):
		return hash(self.origin_path)

class UniqueQueue(Queue):
	def _init(self, maxsize):
		self.queue = OrderedSet()
	def _put(self, item):
		self.queue.add(item)
	def _get(self):
		return self.queue.pop()
	def __contains__(self, item):
		with self.mutex:
			return item in self.queue

def CreateJob(filePath):
	return Job(origin_path=filePath)

class WorkerPool(object):
	def __init__(self):
		self.jobQueue = UniqueQueue()

		self.pipeline = LockSafeFitting()
		self.__assemblePipeline()

		self.__processing = threading.Event()

		self.workers = []
		for x in range(int(config.WORKERS)):
			self.workers.append(Worker(self.jobQueue, self.pipeline, self.__processing))

	def startProcessing(self):
		for worker in self.workers:
			worker.start()
		self.__processing.set()

	def stopProcessing(self):
		self.__processing.clear()

	def isProcessing(self):
		return self.__processing.isSet()

	def addJob(self, job):
		return self.jobQueue.put(job)

	def queueLength(self):
		return self.jobQueue.qsize()

	def join(self, timeout = 0):
		self.__processing.clear()
		for worker in self.workers:
			worker.join(timeout=0)

		return True

	def inQueue(self, job):
		return job in self.jobQueue

	def __assemblePipeline(self):
		self.pipeline.Register(TakeLock)
		self.pipeline.Register(CreateTempDirectory)
		self.pipeline.Register(CopyToDisk)
		self.pipeline.Register(InspectFile)
		self.pipeline.Register(SetupEncoding)
		self.pipeline.Register(EncodeVideo)
		self.pipeline.Register(CheckForOutput)
		self.pipeline.Register(DetermineDestination)
		self.pipeline.Register(CreateDestDirectories)
		self.pipeline.Register(CopyToDestination)
		self.pipeline.Register(CleanupTempDir)
		self.pipeline.Register(RemoveOriginal)
		self.pipeline.Register(ReleaseLock)

class Worker(threading.Thread):
	def __init__(self, jobQueue, pipeline, canProcess):
		self.queue = jobQueue
		self.pipeline = pipeline
		self.canProcess = canProcess
		self.__exit = threading.Event()
		super(Worker, self).__init__()

	def run(self):
		while not self.__exit.isSet():
			job = None
			if self.canProcess.isSet():
				try:
					job = self.queue.get(timeout=10)
				except queue.Empty:
					pass
			else:
				time.sleep(1)

			if job:
				self.pipeline.convertFile(job)

	def join(self, timeout=1):
		self.__exit.set()
		return super(Worker, self).join(timeout)


class ProcTailer(threading.Thread):
	def __init__(self, process, callBack = None):
		self.process = process
		self.callBack = callBack
		super(ProcTailer, self).__init__()
		self.daemon = True
		self.__exit = threading.Event()

	def run(self):
		while not self.__exit.isSet():
			ready = select.select((self.process.stderr,),(),(), 5)
			if len(ready[0]) == 1:
				for entry in self.process.stderr:
					line = str(entry)
					if 'Duration' in line:
					# output = self.process.stderr.read()
						moduleLogger.debug(line.strip())
					if self.callBack:
						self.callBack(line)

	def join(self, *args, **kwargs):
		self.__exit.set()
		return super(ProcTailer, self).join(*args, **kwargs)
