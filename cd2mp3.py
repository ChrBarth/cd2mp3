#!/usr/bin/env python3

# cd ripper in python
# rips audio cd to mp3-files into current directory

#TODO:
# * parse commandline arguments
# * logging?

# requires discid and musicbrainzngs for musicbrainz-support (instead of cddb)
# (pip3 install discid musicbrainzngs)
import discid
import musicbrainzngs
import subprocess

device   = '/dev/cdrom'
bitrate  = 256
use_cddb = False
encoder  = 'lame'

artist   = 'unknown'
title    = 'unknown'
year     = 0

track    = []

def run_cmd(args):
    """ function that calls system commands
        returns the output """
    p = subprocess.Popen(args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True)
    output = p.communicate()
    return output[0]

# get discid:
disc = discid.read(device)
# set the musicbrainz useragent_
musicbrainzngs.set_useragent("cd2mp3","0.1",None)
# needs "includes=..." to get a non-empty tracklist:
result    = musicbrainzngs.get_releases_by_discid(disc.id, includes=["artists", "recordings"])
release   = result['disc']['release-list'][0]
artist    = release['artist-credit-phrase']
title     = release['title']
tracklist = release['medium-list'][0]['track-list']
for entry in tracklist:
    track.append(entry['recording']['title'])
    print("appending %s" % (entry['recording']['title']))

