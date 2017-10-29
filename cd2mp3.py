#!/usr/bin/env python3

# cd ripper in python3
# rips audio cd to mp3-files into current directory

#TODO:
# * parse commandline arguments

# requires discid and musicbrainzngs for musicbrainz-support (instead of cddb)
# (pip3 install discid musicbrainzngs)
import discid
import musicbrainzngs
import subprocess
import glob
import os
import argparse

device      = '/dev/cdrom'
bitrate     = 256
use_cddb    = False
encoder     = 'lame'
do_encode   = True
do_rip      = False
remove_wav  = False
write_tags  = True
directory   = os.getcwd()

artist   = 'unknown'
title    = 'unknown'
year     = 0
genre    = 12

track    = []
tracknum = 0

parser = argparse.ArgumentParser(description="Rips audio cd to mp3 files")
parser.add_argument("-b", "--bitrate", type=int, help="specify bitrate")
parser.add_argument("-d", "--device", help="path to your cdrom-device")
parser.add_argument("-D", "--workdir", help="output directory")

parser.parse_args()

# changing to working directory:
if os.isdir(directory):
    os.chdir(directory)

# get discid:
try:
    disc = discid.read(device)
    tracknum = disc.last_track_num
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
    print("%d track(s)" % tracknum)
    for entry in tracklist:
        tracktitle = entry['recording']['title']
        track.append(tracktitle)
        print("%02d - %s" % (track.index(tracktitle)+1, tracktitle))

filepattern = artist + "-" + title
filepattern = filepattern.replace("'","")
filepattern = filepattern.replace("’","")
filepattern = filepattern.replace(" ","_")

if do_rip == True:
    # ripping the disc:
    proc = subprocess.run(["cdda2wav", "-B", "-H", "-D", device, filepattern],
                           stdout=subprocess.PIPE)
    if proc.returncode != 0:
        print("cdda2wav exited with code %d" % proc.returncode)
        exit(1)

trackno = 0
if do_encode == True:
    # converting to mp3:
    filelist = sorted(glob.glob(filepattern+"*.wav"))
    for wavfile in filelist:
        mp3file = wavfile.replace(".wav",".mp3")
        print(wavfile,"==>",mp3file)
        encproc = subprocess.run([encoder, "-b", str(bitrate), wavfile, mp3file],
                                  stdout=subprocess.PIPE)
        if encproc.returncode != 0:
            print("encoder exited with code %d" % proc.returncode)
            exit(1)
        if write_tags == True:
            print("Writing id3v2-tag for %s (%s)..." % (mp3file, track[trackno]))
            tagproc = subprocess.run(["id3v2", "-a", artist, "-A", title,
                                      "-t", track[trackno], mp3file],
                                      stdout=subprocess.PIPE)
        if remove_wav == True:
            # remove .wav file:
            os.remove(wavfile)
        trackno = trackno+1


