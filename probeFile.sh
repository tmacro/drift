#!/bin/sh

ffprobe -show_streams $1 | /usr/bin/grep -w 'codec_name\|codec_type'
