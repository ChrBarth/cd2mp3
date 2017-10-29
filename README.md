# cd2mp3

a commandline cd-ripper written in python

## usage:

At the moment just run the script. It will try to get the discid and use it to fetch info from musicbrainz to tag the mp3-files. Later versions will allow you to specify a bitrate and some other options. If the path to your CD/DVD-drive is not "/dev/cdrom", you have to change that in the script.

## requirements:

* python3
* discid (pip3 install discid)
* musicbrainzngs (pip3 install musicbrainzngs)
* lame
* id3v2
