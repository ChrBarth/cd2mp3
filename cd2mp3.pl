#!/usr/bin/perl -w
# Version 09.10.2016: Sonderzeichen aus MP3-Dateinamen entfernt (We're Only In It For The Money => Were Only In It For The Money)
# Version 18.06.2016: CD-Text Support!
# sudo apt-get install libdevice-cdio-perl
# aufgepeppte version ;) 20.02.2005

use strict;
use CDDB_get qw( get_cddb );
# für CD-Text:
use Device::Cdio;
use Device::Cdio::Device;

# Bei nicht-UTF-Metadaten:
# http://snipplr.com/view/4642/
# (String in UTF umwandeln)
# => ZZ Top - Degüello :)

my $artist="unknown artist";
my $album="unknown album";
my $bitrate=256;
my $year="0";
my $genre="12";   # "Other"
my $cdrom_device="/dev/cdrom";
my $interactive="NO";
my $use_cddb="NO";
my $use_cdtext="NO";
my @tracktitle;
my $encodeonly="NO";
my $encoder="lame";
my $workdir="$ENV{PWD}";
#my $encoder="lame --noasm sse";

sub help
{
 my $bname = $0;
 $bname =~ s#/.*/##;
 print <<EOT;
 usage: $bname OPTIONS ...
--a=[artist] (default: $artist)
--l=[album] (default: $album)
--b=[bitrate] (default: $bitrate)
--d=[cdrom-device] (default: $cdrom_device)
--y=[year] (default: $year)
--g=[genre] (default: $genre)
--cddb (default: disabled)
--cdtext (default: disabled, overrides --cddb)
--interactive (default: disabled)
--encodeonly (default: disabled)
--tagsonly (default: disabled)
--e=[encoder] (default: gogo)
--w=[workdir] (default: \$ENV{PWD})
--cdinfo=nur CDDB-Infos auf <STDOUT> ausgeben

see also:
perldoc $bname
EOT
 exit;
}
# argumente checken
if (not defined $ARGV[0])  {
 help();  }

foreach (@ARGV) {
        $artist=$_ if (s/--a=(.*)/$1/);
        $album=$_ if (s/--l=(.*)/$1/);
	$bitrate=$_ if (s/--b=(.*)/$1/);
	$cdrom_device=$_ if (s/--d=(.*)/$1/);
	$interactive="YES" if (/--interactive/);
	$use_cddb="YES" if (/--cddb/);
	$use_cdtext="YES" if (/--cdtext/);
	$encodeonly="YES" if (/--encodeonly/);
	$genre=$_ if (s/--g=//);
	$year=$_ if (s/--y=//);
	$encoder=$_ if (s/--e=//);
	if (s/--w=//)   {
			  $workdir = $_;
			  mkdir $workdir if (! -d $workdir) or die "Konnte $workdir nicht anlegen";
			  chdir $workdir;
			 }
	if (/--tagsonly/)   {
			     &add_tags_in_current_directory;
			     exit 0;
			    }
	if (/--cdinfo/)   {my %config;
			 $config{CD_DEVICE}="$cdrom_device";
			 my %cd=get_cddb(\%config);
			 unless(defined $cd{title}) {
			 			     die "no cddb entry found";  }
			 $artist=$cd{artist};
			 $album=$cd{title};
			 # DEBUG:
			 print "Artist: $artist\n";
			 print "Album:  $album\n";
			 print "Tracks:\n";
			 # END DEBUG
			 foreach (@{$cd{track}})    {
						     # DEBUG:
						     s/ü/ue/g;
						     s/Ü/Ue/g;
						     s/Ä/Ae/g;
						     s/ä/ae/g;
						     s/Ö/Oe/g;
						     s/ö/oe/g;
						     print "$_\n";
						     # END DEBUG
						     }
						     exit;
			 }
	                  
	}

# CDDB-info holen
if ($use_cddb eq "YES") {
			 my %config;
			 $config{CD_DEVICE}="$cdrom_device";
			 my %cd=get_cddb(\%config);
			 unless(defined $cd{title}) {
			 			     die "no cddb entry found";  }
			 $artist=$cd{artist};
			 $album=$cd{title};
			 # DEBUG:
			 print "Artist: $artist\n";
			 print "Album:  $album\n";
			 print "Tracks:\n";
			 # END DEBUG
			 foreach (@{$cd{track}})    {
			 			     push @tracktitle, $_;
						     # DEBUG:
						     #print "$_\n";
						     # END DEBUG
						     }
}
# Ende CDDB-Infos

# CD-Text auslesen
if ($use_cdtext eq "YES") {

	my $d = Device::Cdio::Device->new("/dev/cdrom");
	my $num_tracks = $d->get_num_tracks();
	my $first_track = $d->get_first_track();
	my $last_track = $d->get_last_track();
	my $text = $d->get_track_cdtext(0);

	@tracktitle = ();

	foreach my $field (sort keys %{$text}) { 
		if($field eq "PERFORMER") { $artist = $text->{$field}; }
		if($field eq "TITLE" ) { $album = $text->{$field}; }
	 }

	print "*** using CD-Text ***\n\n";
	print "$artist - $album\n\n";

	my $i;
	for ($i=$first_track->{track}; $i<= $last_track->{track}; $i++) {
		$text = $d->get_track_cdtext($i);
		foreach my $field (sort keys %{$text}) {
			if ($field eq "TITLE") { 
			my $songtitle = $text->{$field};
			$songtitle =~ s/(.*)\ \-\ $artist/$1/; #RHCP-The Getaway-Hack (TITLE=Songtitle - Red Hot Chili Peppers)
			push @tracktitle, $songtitle;
			}
		}
	}
}

if ( not $encodeonly eq "YES")   {
				# cd rippen
				print "Rippe CD nach $workdir...\n$artist : $album @ $bitrate kbps\n";
				my $filenamepattern = "$artist-$album";
				$filenamepattern =~ s#/##g;	# z.B. bei CD1/2 in Dateinamen
				my $rip_status = system("cdda2wav --gui -B -H -D $cdrom_device \"$filenamepattern\"");
				die "Fehler beim rippen: $!" unless $rip_status == 0;
}

# dateien umwandeln
my @wavfiles = <*.wav>;
my $tracknr = 1;
my $tt;

foreach my $wavfile (@wavfiles)
{
 # titel setzen
 if ($use_cddb eq "YES" || $use_cdtext eq "YES")  {
 			   my $tn = $tracknr - 1;
                           $tt = $tracktitle[$tn];   }
 else                     {
			   $tt = "untitled";   }

 # flac-Patch:
if ($encoder eq "flac") {
			  print "not supported yet... :(\n";
			  my $enc_status = system("$encoder -T artist=\"$artist\" -T album=\"$album\" -T title=\"$tt\" -T year=\"$year\" -T genre=\"$genre\" -T track=\"$tracknr\" '$wavfile'");
			  die "konnte flac-Datei nicht encoden: $!" unless $enc_status == 0;
			}
else			{
			  # mp3 encoden
			  my $mp3file = "$wavfile";
			  $mp3file =~ s/\.wav$/\.mp3/;
			  # Sonderzeichen aus $mp3file löschen (lame macht ansonsten Probleme):
			  $mp3file =~ s/\'//g;
			  $mp3file =~ s/\`//g;
			  $mp3file =~ s/\"//g;
			  ### DEBUG:
			  #print "$wavfile ==> $mp3file\n";
			  ### END DEBUG
			  my $enc_status = system("$encoder -b \"$bitrate\" \"$wavfile\" \"$mp3file\"");
			  die "Konnte $wavfile nicht encoden: $!" unless $enc_status == 0;
			  # tag setzen (mp3info)
			  my $tag_status = system("mp3info -a \"$artist\" -l \"$album\" -t \"$tt\" -n \"$tracknr\" -y \"$year\" -g \"$genre\" \'$mp3file\'");
			  die "Konnte tag für $mp3file nicht schreiben" unless ($tag_status==0);
			  }
 $tracknr++;
 # .wav löschen
 unlink("$wavfile") or die "Konnte $wavfile nicht löschen: $!";
}

# titel tags mit mp3info setzen wenn ohne --cddb
if ($use_cddb eq "NO" && $use_cdtext eq "NO")   {
				&add_tags_in_current_directory;
			    }
 # mp3s umbenennen
 my @mp3files = <*.mp3>;
 my $tn = 0;
 foreach my $mp3file (@mp3files )   {
 	                             my $newname = $mp3file;
				     my $ttitle = $tracktitle[$tn];
				     $newname =~ s/([0-9]+)(\.mp3)/$1-$ttitle$2/;
				     $newname =~ s#/##;			# bei einem "/" im Dateinamen gibts Probleme
				     rename("$mp3file","$newname") or die "Konnte $mp3file nicht in $newname umbenennen: $!";
				     $tn++;
				     }

# programm ordnungsgemäß beenden
exit 0;
### ENDE ###

#######################################################################################
# start funktionen
sub add_tags_in_current_directory   {
                                print "Titeleingabe:\n";
                                my @mp3files = <*.mp3>;
                                $tracknr=1;
                                foreach my $mp3file (@mp3files)  {
			                                 my $title;
		                                  	 print " $mp3file :";
			                                 if ($interactive eq "YES") {
				                                        chomp($title=<STDIN>);
						                                     }
	  	                                         else   {
				                                        my $pn=sprintf("%02d", $tracknr);
				                                        $title="titel$pn";
			                                     }
			                                      # id3 schreiben
			                                 my $tag_status = system("mp3info -g $genre -y $year -t \"$title\" \"$mp3file\"");
							 die "Konnte $mp3file nicht taggen: $?" unless $tag_status == 0;							 
							 $tracknr++;
							 }
return 0;							      
}							


### Dokumentation ###

=head1
cd2mp3 - CDs auf der Kommandozeile rippen


=cut

=pod

Dieses nette Skript rippt CDs und erzeugt MP3-Dateien. Verwendet werden die Programme gogo (MP3-Encoder, kann aber leicht geändert werden), cdda2wav (CD-Ripper) und mp3info (Tagger). Außerdem noch das Perl-Modul CDDB_get.
Da die CD erstmal komplett auf die Festplatte (standardmäßig ins aktuelle Verzeichnis) kopiert wird, sollte der Datenträger vorher auf genügend Kapazität geprüft werden. Die .wav-Dateien werden nach erfolgreichem Kodieren automatisch gelöscht.

=head2 Argumente:

=over 2

=item --a=[artist]

ID3: artist

=item --l=[album]

ID3: album

=item --b=[bitrate]

MP3-Bitrate

=item --d=[cdrom-device]

Pfad zum CD-Rom (z.B. /dev/cdrom)

=item --y=[year]

ID3: year

=item --g=[genre]

ID3: genre

Liste aller möglicher Genres:

C<mp3info -G>

=item --cddb

cddb benutzen um ID3-Tags zu erzeugen

=item --interactive

interaktiver Modus

=item --encodeonly

bereits erzeugte .wav Dateien im aktuellen Verzeichnis encoden.

=item --tagsonly

nur ID3-Tags schreiben (alle MP3-Dateien im aktuellen Verzeichnis).
CDDB funktioniert hier übrigens auch, so daß auch nachträglich ohne viel
Tipperei Tags geschrieben werden können.

=item --e=[encoder]

Anderen Encoder wählen. --e=flac erzeugt neuerdings auch flac-Dateien!

=item --w=[workdir]

In Verzeichnis [workdir] wechseln. Muss vor --tagsonly verwendet werden, wenn ID3-Tags nicht im PWD geschrieben werden sollen.
[workdir] wird neu angelegt, wenn es noch nicht existiert.

=back

=head2 Skripter:

=cut

=pod

Christoph Barth (ghostfacebarth@web.de)

=cut

