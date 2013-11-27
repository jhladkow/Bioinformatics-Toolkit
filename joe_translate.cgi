#!/usr/bin/perl
use strict;
use warnings;
use CGI qw/:standard/;
use Bio::Seq;


print "Content-type: text/html\n\n";

if (!param())  {				# Displays empty form when user first accesses web page
    print Beginning("DNA Translator");	
    print Header();
    print form();
    print "<a href = \"http://XXXXXXXXXXXXXXXXXXXXXX//joe_a4.html\">Home</a>";
}

else {
    if (param())  {
	my $text = param("sequence");					## Stores user input
	my $insertedSeq = $text;
	my $dropDown = param("choice");					## Stores selected reading frame
	$insertedSeq =~ s/\r\n/\n/g;
	my @seqLines = split /\n/, $insertedSeq;			## Splits user input into an array of lines
	my $header = shift @seqLines;					## First line is stored as header
	my $join = join "", @seqLines;					## Rest of array is joined together
	
	if ($header =~ /^>[^ ].+/i)  {					## Header validation
	    if ($join =~ /^[acgt]+$/i)  {				## Sequence validation
		my $dna = $join;
		$dna =~ s/([ACGT]{60})/$1<br\>/g;			## Proper formatting - 60 characters per line
		my $revSeq = reverse "$join";
		my $editHeader = $header;
		$editHeader =~ s/>//;					## Removes > in header
		my $forwardSeq = Bio::Seq->new(-seq => "$join");	## Makes inputted sequence an object
		my $reverseSeq = $forwardSeq->revcom;			## Makes a reverse sequence object
		
		if ($dropDown eq "All") {				## If user selects all reading frames	
		    print "<pre>";
		    print "<title>Translation - ALL frames</title>";
		    print "<h2>$editHeader</h2><br/><br/>";
		    print "DNA Sequence:<br/>$dna<br/><br/>";
	    
		    foreach (0..2) {
			my $forwardProt = $forwardSeq->translate(undef,undef,$_);		## Translates DNA sequence
			my $editSeq = $forwardProt->seq;
			$editSeq =~ s/([ABCDEFGHIKLMNPQRSTVWXYZ*]{60})/$1<br\>/g;		## Proper formatting
			print "Forward Reading frame $_:<br/>";
			print "$editSeq<br/><br/>";
		    }
		    
		    foreach (0..2) {
			my $reverseProt = $reverseSeq->translate(undef,undef,$_);
			my $editRevSeq = $reverseProt->seq;
			$editRevSeq =~ s/([ABCDEFGHIKLMNPQRSTVWXYZ*]{60})/$1<br\>/g;
			print "Reverse Reading frame $_:<br/>";
			print "$editRevSeq<br/><br/>";
		    }
		    print "</pre>";
		    print "<a href = \"http://XXXXXXXXXXXXXXXXXXXXXX//joe_translate.cgi\">Back To Translator</a><br/>";
		    print "<a href = \"XXXXXXXXXXXXXXXXXXXXXX//joe_a4.html\">Home</a>";
		}
	
		if ($dropDown eq "Forward") {
		    print "<pre>";
		    print "<title>Translation - FORWARD frames</title>";
		    print "<h2>$editHeader</h2><br/><br/>";
		    print "DNA Sequence:<br/>$dna<br/><br/>";
		    
		    foreach (0..2) {
			my $forwardProt = $forwardSeq->translate(undef,undef,$_);
			my $editSeq = $forwardProt->seq;
			$editSeq =~ s/([ABCDEFGHIKLMNPQRSTVWXYZ*]{60})/$1<br\>/g;
			print "Forward Reading frame $_:<br/>";
			print "$editSeq<br/><br/>";
		    }
		    print "</pre>";
		    print "<a href = \"http://XXXXXXXXXXXXXXXXXXXXXX//joe_translate.cgi\">Back To Translator</a><br/>";
		    print "<a href = \"http://XXXXXXXXXXXXXXXXXXXXXX//joe_a4.html\">Home</a>";
		}
	
		if ($dropDown eq "Reverse") {
		    print "<pre>";
		    print "<title>Translation - REVERSE frames</title>";
		    print "<h2>$editHeader</h2><br/><br/>";
		    print "DNA Sequence:<br/>$dna<br/><br/>";
		    
		    foreach (0..2) {
			my $reverseProt = $reverseSeq->translate(undef,undef,$_);
			my $editRevSeq = $reverseProt->seq;
			$editRevSeq =~ s/([ABCDEFGHIKLMNPQRSTVWXYZ*]{60})/$1<br\>/g;
			print "Reverse Reading frame $_:<br/>";
			print "$editRevSeq<br/><br/>";
		    }
		    print "</pre>";
		    print "<a href = \"http://zXXXXXXXXXXXXXXXXXXXXXX//joe_translate.cgi\">Back To Translator</a><br/>";
		    print "<a href = \"http://XXXXXXXXXXXXXXXXXXXXXX//joe_a4.html\">Home</a>";
		}
	    }
	
	    elsif ($join !~ /^[acgt]+$/i)  {		## If inputted sequence is invalid
		print Header();
		print "<font color='red'>ERROR - Invalid Sequence (Acceptable characters are A, G, C, T)</font>";
		print form($dropDown,$text);
		print "<a href = \"http://XXXXXXXXXXXXXXXXXXXXXX//joe_a4.html\">Home</a>";
	    }
	}
	elsif ($header !~ /^>[^ ].+&/i)  {		## If header is invalid
	    if ($join =~ /^[acgt]+$/i)  {		## If sequence is valid
		print Header();
		print "<font color='red'>ERROR - Invalid Header (Must begin with > followed immediately by a character)</font>";		# Error message with example file
		print form($dropDown,$text);
		print "<a href = \"http://XXXXXXXXXXXXXXXXXXXXXX//joe_a4.html\">Home</a>";
	    }
	    elsif ($join !~ /^[acgt]+$/i)  {		## If sequence is invalid
		print Header();
		print "<font color='red'>ERROR - Invalid Header (Must begin with > followed immediately by a character)</font></br>";
		print "<font color='red'>ERROR - Invalid Sequence (Acceptable characters are A, G, C, T)</font>";		# Error message with example file
		print form($dropDown,$text);
		print "<a href = \"http://XXXXXXXXXXXXXXXXXXXXXX//joe_a4.html\">Home</a>";
	    }
	}    
    }
}
print ending();

#########################   Sub Routines   #########################

sub Beginning {						
    my $title = $_[0];
    return <<BEG;
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <title>$title</title>
    </head>
    <body>
BEG
}


sub Header {					
    return <<HH;
    <h2>
	<font color='red'>DNA Translator</font>
    </h2>
    <h4>
    This program will produce translation results of a valid DNA sequence.</br>
    Paste in a valid DNA sequence and select which readings frames you wish to view.
    </h4>

HH
}


sub Ending {			
    return <<END;
</body>
</html>
END
}


sub form {				
    my $formpage = "";
    my $choice = shift;
    my $text = shift;
    my $forward = "Forward";
    my $reverse = "Reverse";
    my $all = "All";
    $formpage .= <<F;
     <form method="post" action="$0" enctype="multipart/form-data">
     <table border="0">
     <tr>
     <td>
     Reading Frames:
     </td><td>
     <select name="choice"/>
     
F
my @choice = ($all, $forward, $reverse);
foreach (@choice) {
    my $opt = "";
    $opt = " selected='selected'" if ($choice eq "$_");
    $formpage .= "<option $opt>$_</option>";
}

$formpage .= <<F;
</td></tr><tr align="top">
	</select>
	</br><td>
	Sequence:</br></td><td><textarea rows='20' cols='60' name="sequence">$text</textarea>
     </td></tr><tr><td>
	</br>
	<input type="submit" value="TRANSLATE"/>
	</td></tr>
     </form>
     <tr><td>
F
    return $formpage;
}
