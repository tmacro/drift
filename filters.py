from pipewrench.pipeline import Filter
from pipewrench.errors import StopProcessingError
from pipewrench.screens import Screen
from pipewrench.fittings import PipeFitting
import locker
import tempfile
import shutil
from ffmpeg import probeFile, convertFile
import os
import config
import pathlib
# filters in Order
# take lock
# create temp directory
# copy to disk
# discover file attrs
# determine encoding options
# convert file
# gen destination path
# copy to destination
# remove original file
# release lock

class TakeLock(Filter):
	def Execute(self, msg):
		if config.CLUSTER_MODE:
			fileLock = locker.TakeLock(msg.origin_path)
			if fileLock:
				msg.fileLock = fileLock
				self.logger.debug('Taking lock for %s'%msg.origin_path)
				return msg
			raise StopProcessingError('Failed to take lock for %s'%msg.origin_path)
		else:
			return msg

class CreateTempDirectory(Filter):
	def Execute(self, msg):
		temp = tempfile.TemporaryDirectory()
		msg.tempDir = temp
		self.logger.debug('Created temp directory %s'%msg.tempDir.name)
		return msg

class CopyToDisk(Filter):
	def Execute(self, msg):
		self.logger.debug('Copying %s to %s'%(msg.origin_path, msg.tempDir.name))
		msg.tempInput = shutil.copy(str(msg.origin_path), msg.tempDir.name + '/input%s'%msg.origin_path.suffix)
		self.logger.debug(' Finished Copying %s to %s'%(msg.origin_path, msg.tempDir.name))
		return msg

class InspectFile(Filter):
	def Execute(self, msg):
		self.logger.debug('Inspecting %s for codec info'%msg.origin_path)
		info = probeFile(msg.tempInput)
		msg.originCodecVideo = info['video']
		msg.originCodecAudio = info['audio']
		self.logger.debug('Discovered vidoe: %s, audio: %s about %s'%(msg.originCodecVideo, msg.originCodecAudio, msg.origin_path))
		return msg

class SetupEncoding(Filter):
	def Execute(self, msg):
		msg.encodeVideo = True
		msg.encodeAudio = True

		if msg.originCodecVideo in config.ACCEPTABLE_CODECS:
			msg.encodeVideo = False



		if msg.originCodecAudio in config.ACCEPTABLE_CODECS:
			msg.encodeAudio = False
		self.logger.debug('Setup encoding - video: %s audio: %s for %s'%(msg.encodeVideo, msg.encodeAudio, msg.origin_path))
		return msg

class EncodeVideo(Filter):
	def Execute(self, msg):
		self.logger.debug('Coverting %s'%msg.origin_path)
		msg.tempOutput = msg.tempDir.name + '/output.' + config.FFMPEG_CONTAINER
		msg.return_code = convertFile(msg.tempInput, msg.tempOutput, msg.encodeVideo, msg.encodeAudio)
		self.logger.debug('Done Converting %s'%msg.origin_path)
		return msg

class CheckForOutput(Filter):
	def Execute(self, msg):
		self.logger.debug('Checking for encoded video...')
		if not os.path.isfile(msg.tempOutput):
			raise StopProcessingError('Encoded video not found for %s'%msg.origin_path)

		return msg

class DetermineDestination(Filter):
	def Execute(self, msg):
		base_path = msg.origin_path.relative_to(config.INPUT_DIR)
		msg.outputPath = pathlib.Path(config.OUTPUT_DIR).joinpath(base_path).with_suffix('.' + config.FFMPEG_CONTAINER)
		# base_path = '/' + msg.origin_path.stem  + '.'
		# msg.outputPath = pathlib.Path(config.OUTPUT_DIR  + base_path + config.FFMPEG_CONTAINER)
		self.logger.debug('%s will be copied to %s'%(msg.origin_path, msg.outputPath))
		return msg


class CreateDestDirectories(Filter):
	def Execute(self, msg):
		self.logger.debug('Creating dest directories for %s'%msg.origin_path)
		create_path = os.path.dirname(str(msg.outputPath.as_posix()))
		self.logger.debug('Creating directory: %s'%create_path)
		try:
			os.makedirs(create_path, exist_ok=True)
		except FileExistsError as e:
			self.logger.debug('Creating path threw an error :(')
			self.logger.exception(e)

		return msg

class CopyToDestination(Filter):
	def Execute(self, msg):
		self.logger.debug('Copying %s to destination'%msg.origin_path)
		shutil.copyfile(msg.tempOutput, str(msg.outputPath))
		self.logger.debug('Done copying %s'%msg.origin_path)
		return msg

class CleanupTempDir(Filter):
	def Execute(self, msg):
		msg.tempDir.cleanup()
		self.logger.debug('Cleaned up temp directory %s'%msg.tempDir.name)
		return msg

class RemoveOriginal(Filter):
	def Execute(self, msg):
		self.logger.debug('Deleting original file - %s'%msg.origin_path)
		os.remove(str(msg.origin_path))
		return msg

class ReleaseLock(Filter):
	def Execute(self, msg):
		if config.CLUSTER_MODE:
			self.logger.debug('Releasing lock for %s'%msg.origin_path)
			msg.fileLock.release()
			return msg
		else:
			return msg

class UnlockScreen(Screen):
	def Execute(self, msg):
		msg = self.target(msg)
		if msg.StopProcessing:
			if config.CLUSTER_MODE:
				self.logger.debug('Caught stop processing for %s releasing etcd lock'%msg.origin_path)
				lock = getattr(msg, 'fileLock', None)
				if lock:
					lock.release()
		return msg

class LockSafeFitting(PipeFitting):
	def convertFile(self, msg):
		unlock_screen = UnlockScreen(self.Invoke)
		return unlock_screen.Execute(msg)

	# def Invoke(self, msg):
	# 	return self.Execute(msg)
