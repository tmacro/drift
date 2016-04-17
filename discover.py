# File discovery goes here
import os
file_extensions = [ 'avi', 'mkv', 'mp4', 'wmv', 'flv' ]

def searchForFiles(dir):
	discovered_files = []
	for root, dirs, files in os.walk(dir):
		for entry in files:
			for extension in file_extensions:
				if entry.endswith('.' + extension):
					discovered_files.append(root+ '/' + entry)

	return sanitizePaths(discovered_files)

def BuildCoversionList(directory):
	if os.path.isdir(directory):
		return searchForFiles(directory)
	return []

def sanitizePaths(paths):
	sanitized = []
	for path in paths:
		p  = os.path.abspath(path)
		sanitized.append(p)
	return sanitized
