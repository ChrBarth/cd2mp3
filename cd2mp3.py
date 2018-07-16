#!/usr/bin/env python3

# cd ripper in python3
# rips audio cd to mp3-files into current directory

#TODO:
# get year from musicbrainz
# maybe do the tagging while encoding with lame (so we would not need id3v2 any more)

# requires libdiscid and musicbrainzngs for musicbrainz-support (instead of cddb)
# and cd-info as a fallback (reads cd-text)
# (sudo apt install python3-libdiscid python3-musicbrainzngs libcdio-utils)

# discid: Ubuntu 16.04:
#import discid

# libdiscid: Ubuntu 18.04:
import libdiscid
import musicbrainzngs
import subprocess
import glob
import os
import argparse
import re

device      = '/dev/cdrom'
bitrate     = 256
encoder     = 'lame'
do_encode   = True
do_rip      = True
remove_wav  = True
write_tags  = True
directory   = os.getcwd()
cur_dir     = directory

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
parser.add_argument("--norip", action="store_true", help="Don't rip the cd (just encode wav-files)")
parser.add_argument("--notags", action="store_true", help="Don't write id3-tags")
parser.add_argument("--nodelete", action="store_true", help="Don't delete wav files after encoding")
parser.add_argument("-y", "--year", help="id3-tag: year")
parser.add_argument("-a", "--artist", help="id3-tag: artist")
parser.add_argument("-A", "--album", help="id3-tag: album title")
parser.add_argument("-g", "--genre", type=int, help="id3-tag: genre (integer) - see id3v2 -L")
parser.add_argument("-e", "--encoder", help="use other encoder than lame")
args = parser.parse_args()

if args.bitrate != None:
    bitrate = args.bitrate
if args.device != None:
    device = args.device
if args.workdir != None:
    directory = args.workdir
if args.norip:
    do_rip = False
if args.notags:
    write_tags = False
if args.nodelete:
    remove_wav = False
if args.year != None:
    year = args.year
if args.artist != None:
    artist = args.artist
if args.album != None:
    title = args.album
if args.genre != None:
    genre = args.genre
if args.encoder != None:
    encoder = args.encoder
    
# changing to working directory:
if os.path.isdir(directory):
    os.chdir(directory)

# get discid:
try:
    disc = libdiscid.read(device)
    tracknum = disc.last_track
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
    print("No matches found on musicbrainz... Trying cd-info:")
    cmd = ["cd-info", "-C", device, "--no-header", "--no-disc-mode"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    for line in proc.stdout.readlines():
        #find all "\tTITLE: (TITLE)" lines:
        pattern = re.compile("^\tTITLE: (.*)\n")
        m = re.match(pattern, line.decode("utf-8"))
        if m:
            track.append(m.group(1))
            print("Added track {}".format(m.group(1)))
        else:
            # do we have an artist?
            # this does obviously not work with samplers,
            # since everytime a matching line is found,
            # the artist-variable will be overwritten...
            pattern = re.compile("^\tPERFORMER: (.*)\n")
            m = re.match(pattern, line.decode("utf-8"))
            if m:
                artist = m.group(1)
    if len(track)>0:
        # if we found any info, remove first entry
        # since it is the album title:
        title = track.pop(0)
        print("Album: {} - {}".format(artist, title))

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
        if write_tags == True and len(track)>0:
            print("Writing id3v2-tag for %s (%s)..." % (mp3file, track[trackno]))
            tagproc = subprocess.run(["id3v2", "-a", artist, "-A", title,
                                      "-t", track[trackno], "-y", str(year),
                                      "-T", str(trackno+1), "-g", str(genre), mp3file],
                                      stdout=subprocess.PIPE)
        if remove_wav == True:
            # remove .wav file:
            os.remove(wavfile)
        trackno = trackno+1

os.chdir(cur_dir)
