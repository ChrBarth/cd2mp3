#!/usr/bin/env python3

# cd ripper in python
# rips audio cd to mp3-files into current directory

#TODO:
# * parse commandline arguments
# * cddb support
# * logging?


import subprocess

device   = '/dev/cdrom'
bitrate  = 256
use_cddb = False
encoder  = 'lame'

artist   = 'unknown'
album    = 'unknown'
year     = 0

titles   = []

def run_cmd(args):
    """ function that calls system commands
        returns the output """
    p = subprocess.Popen(args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True)
    output = p.communicate()
    return output[0]

# DEBUG:
#t = run_cmd(["ls","/media"])
#print(t

