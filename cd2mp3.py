#!/usr/bin/env python3

# cd ripper in python3
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
try:
    disc = discid.read(device)
except discid.DiscError:
    print("Disc error!")
    exit(1)

# set the musicbrainz useragent_
musicbrainzngs.set_useragent("cd2mp3","0.1",None)
# needs "includes=..." to get a non-empty tracklist:
try:
    result    = musicbrainzngs.get_releases_by_discid(disc.id,
                                                  includes=["artists", "recordings"])
except musicbrainzngs.ResponseError:
    print("No matches found on musicbrainz...")
else:
    # the above command returns a dict of more dicts,lists, even more dicts...
    release   = result['disc']['release-list'][0]
    artist    = release['artist-credit-phrase']
    title     = release['title']
    tracklist = release['medium-list'][0]['track-list']
    print("Artist: ",artist)
    print("Album:  ",title)
    for entry in tracklist:
        tracktitle = entry['recording']['title']
        track.append(tracktitle)
        print("%02d - %s" % (track.index(tracktitle)+1, tracktitle))

