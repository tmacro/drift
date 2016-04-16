import etcd
import config
import os
import subprocess
import shlex
import threading
import queue
import select
import logging
moduleLogger = logging.getLogger('drift')

file_extensions = [ 'avi', 'mkv', 'mp4', 'wmv', 'flv' ]

client = etcd.Client(host=config.ETCD_HOST, port=2379)

# Search for fies in need of conversion
def searchForFiles(dir):
	discovered_files = []
	for root, dirs, files in os.walk(dir):
		for entry in files:
			for extension in file_extensions:
				if entry.endswith(extension):
					discovered_files.append(root+ '/' + entry)

	return discovered_files

def buildFFmpegCommand(encodeVideo = True, encodeAudio = True):
	if encodeVideo:
		videoCodec = config.CODEC_VIDEO
	else:
		videoCodec = 'copy'

	if encodeAudio:
		audioCodec = config.CODEC_AUDIO
	else:
		audioCodec = 'copy'

	base = 'ffmpeg -i %s '
	options = '-c:v %s -c:a %s -preset %s -crf %i '%(videoCodec, audioCodec, config.FFMPEG_PRESET, config.FFMPEG_CRF)
	if config.CONFIG.get('FFMPEG_EXTRA_ARGS', False):
		options = options + config.FFMPEG_EXTRA_ARGS + ' '

	command = base + options + '%s'

# Convert those files
def convertFile(input_path, output_path):
	args = slex.split(buildFFmpegCommand()%(input_path, output_path))
	proc = subprocess.Popen(args, stderr=subprocess.PIPE)

class Job(threading.Thread):
	def __init__(self):

	def __genDestinationPath(self):

	def __genFFmpegCommand(self):
		

class Worker(threading.Thread):
	def __init__(self, jobQueue):
		self.queue = jobQueue
		self.__exit = threading.Event()
		super(Worker, self)__init__():

	def run(self):
		while not self.__exit.isSet():
			try:
				input_path, output_path = self.queue.get(timeout=5)
				self.__proc = convertFile(input_path, output_path)
			except queue.Empty:
				self.__proc = None
				pass

			if self.__proc:
				try:
					self.__proc.wait(timeout=5)
				except subprocess.TimeoutExpired:
					pass


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
				output = self.process.stderr.read()
				moduleLogger.debug(output)
				if self.callBack:
					self.callBack(output)
