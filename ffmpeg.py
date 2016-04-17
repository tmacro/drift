# File conversion via ffmpeg goes here
import shlex
import subprocess
import config
import logging
moduleLogger = logging.getLogger('ffmpeg')

def buildFFmpegCommand(encodeVideo = True, encodeAudio = True):
	if encodeVideo:
		videoCodec = config.CODEC_VIDEO
		if videoCodec == 'h264':
			videoCodec = 'libx264'
	else:
		videoCodec = 'copy'

	if encodeAudio:
		audioCodec = config.CODEC_AUDIO
		if audioCodec == 'aac':
			audioCodec = 'aac'
	else:
		audioCodec = 'copy'

	base = 'ffmpeg -i %s '
	options = '-c:v %s -preset %s -crf %i -c:a %s -b:a %s '%(videoCodec, config.FFMPEG_PRESET, config.FFMPEG_CRF, audioCodec, config.AUDIO_BR)
	if config.CONFIG.get('FFMPEG_EXTRA_ARGS', False):
		options = options + config.FFMPEG_EXTRA_ARGS + ' '

	command = base + options + '%s'
	return command

def convertFile(input_path, output_path, encodeVideo = True, encodeAudio = True):
	rawCommand = buildFFmpegCommand(encodeVideo, encodeAudio)%(shlex.quote(input_path), output_path)
	args = shlex.split(rawCommand)
	moduleLogger.debug('converting with %s'%rawCommand)
	proc = subprocess.Popen(args, stderr=subprocess.PIPE)
	proc.wait()
	return proc

def probeFile(file_path):
	# Build and execute ffprobe command
	command = '''/usr/bin/sh -c "ffprobe -show_streams %s | grep -w 'codec_name\|codec_type'"'''%shlex.quote(file_path)
	proc = subprocess.run(shlex.split(command), stdout=subprocess.PIPE)
	# Cleanup output for processing
	streams = [ x.strip() for x in proc.stdout.decode().strip().split('\n') ]
	codecs = {}
	for x in range(len(streams)):
		key, value = streams[x].split('=')
		if key == 'codec_type':
			codecs[value] = streams[x-1].split('=')[1]

	return codecs
