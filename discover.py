# File discovery goes here
import os
import pathlib
import config

file_extensions = [ 'avi', 'mkv', 'mp4', 'wmv', 'flv', 'm4v' ]

def searchForFiles(dir):
	rootPath = pathlib.Path(dir)
	for extension in file_extensions:
		for path in rootPath.rglob('*.%s'%extension):
			if filterMinimumSize(path):
				yield path

def filterMinimumSize(path):
	return path.stat().st_size >= config.MIN_FILE_SIZE
