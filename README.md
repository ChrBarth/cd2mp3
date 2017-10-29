# cd2mp3

a commandline cd-ripper written in python replacing my good old perl-script from around 2005 :)

## usage:

Just run the script and it will rip the audio-cd inserted in /dev/cdrom into the current directory and convert the files to mp3 (256kb). It will also try to tag the files with the help of musicbrainz (https://musicbrainz.org/). Most settings can be changed from the command line. For a complete list of command-line options use *cd2mp3.py -h*.

## requirements:

* python3
* discid (pip3 install discid)
* musicbrainzngs (pip3 install musicbrainzngs)
* lame
* id3v2
