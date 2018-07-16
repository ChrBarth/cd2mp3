# cd2mp3

a commandline cd-ripper written in python replacing my good old perl-script from around 2005 :) Now working with Ubuntu 18.04 (Bionic Beaver).

## usage:

Just run the script and it will rip the audio-cd inserted in /dev/cdrom into the current directory and convert the files to mp3 (256kb). It will also try to tag the files with the help of musicbrainz (https://musicbrainz.org/). If musicbrainz doesn't find any info on the disc, cd-info is used as a fallback (reads cd-text). Most settings can be changed from the command line. For a complete list of command-line options use *cd2mp3.py -h*.

## requirements:

* python3
* libdiscid (sudo apt install python3-libdiscid)
* musicbrainzngs (sudo apt install python3-musicbrainzngs)
* cdda2wav
* lame
* id3v2
* cd-info (sudo apt install libcdio-utils)

## changelog:

* 2018-07-16: Ubuntu 18.04-Version - "Ordinary Corrupt Human Love"-Edition :) Now using libdiscid instead of discid and additionally requires cd-info for cd-text reading if musicbrainz does not find anything.
