#!/usr/bin/perl
use strict;
use warnings;
use CGI qw/:standard/;
use lib '/home/XXXXXXXXXXXXXXXXXXXXXX//src/ensembl/modules';
use Bio::EnsEMBL::Registry;
use Bio::Graphics;
use Bio::SeqFeature::Generic;
use Bio::EnsEMBL::Gene;
use Bio::EnsEMBL::Slice;


print "Content-type: text/html\n\n";

if (!param()) {				
    print Beginning("Gene Viewer");	
    print Header();
    print form();
    print "<a href = \"http://XXXXXXXXXXXXXXXXXXXXXX//joe_a4.html\">Home</a>";
}

else {
    if (param()) {
	my $chromosome = param("choice");			## Stores chromosome choice
	my $startPos = param("startpos");			## Stores starting position
	my $endPos = param("endpos");				## Stores ending position
	my $length = $endPos - $startPos;			## Stores difference between positions
	
	my $registry = 'Bio::EnsEMBL::Registry';		## Necessary to access ensembl database
	   $registry->load_registry_from_db(
	    -host => 'ensembldb.ensembl.org',
	    -user => 'anonymous'
	    );
	
	my $slice_adaptor = $registry->get_adaptor('Bos taurus', 'Core', 'Slice');		## Creates slice adaptor for bos taurus
	my $chrom = $slice_adaptor->fetch_by_region('chromosome', $chromosome);			## Fetches user selected chromosome
	my $chromLen = $chrom->length();						## Gets length of chromosome
	my @errors;
	
	if ($startPos !~ /^[0-9-]+$/) {						## VALIDATION
	    push @errors, "ERROR - Starting position must be a number";
	}
	if ($endPos !~ /^[0-9-]+$/) {
	    push @errors, "ERROR - Ending position must be a number";
	}
	if ($startPos < 0 || $startPos > $chromLen) {
	    push @errors, "ERROR - Start position value is not contained within this chromosome";
	}
	if ($endPos > $chromLen || $endPos < 0) {
	    push @errors, "ERROR - End position value is not contained within this chromosome";
	}
	if (($length < 1000) && ($startPos =~ /^[0-9-]+$/) && ($endPos =~ /^[0-9-]+$/)) {		## This error will only display if integers are added
	    push @errors, "ERROR - Positions must be separated by at least 1000 kb";
	}
	if ($length > 10000000) {
	    push @errors, "ERROR - Positions must be within 10,000,000 kb of each other";
	}
	if (($endPos < $startPos) && ($startPos =~ /^[0-9-]+$/) && ($endPos =~ /^[0-9-]+$/)) {		
	    push @errors, "ERROR - Start position value must be less than end position value";
	}
	
	if (scalar @errors == 0) {		## If validation is successful
	    my $slice = $slice_adaptor->fetch_by_region('chromosome', $chromosome, $startPos, $endPos);			## Fetches user selected splice site
	    my $gene_ref = $slice->get_all_Genes();					## Reference to all fetched genes
	    my @genes_in_slice = @$gene_ref;					## Fetched gene refereces stored in array
	    print "<pre>";
	    print "<title>$chromosome : $startPos-$endPos</title>";
	    print "<h2>Showing region $startPos to $endPos from Bos Taurus (Cow) chromosome $chromosome</h2></br>";
	    print "<table border = '1'>";
	    print "<tr><td>Gene Id</td><td>Start</td><td>End</td><td>Strand</td><td>Length</td><td>Description</td><td>External Name</td><td>Gene Type</td><td>Status</td></tr>";
	
	    foreach my $gene (@genes_in_slice) {			## Loops through all genes
	        print "<tr>";
		my $ID = $gene->stable_id();				## Gets gene ID
		my $beg = $gene->seq_region_start();			## Gets gene start position
		my $ending = $gene->seq_region_end();			## Gets gene ending position
		my $len = $gene->length();				## Gets gene length
		my $strand = $gene->strand();				## Gets gene strand
		    if ($strand == 1) {	
		        $strand = '+';				## Changes strand 1 to +
		    }
		    else {
		        $strand = '-';				## Changes strand 0 to -
		    }
		my $desc = $gene->description();		## Gets gene description
		    if ($desc =~ /^[ ]*$/) {
		        $desc = "N/A";				## Fills in an empty descriptions with N/A
		    }
		my $external = $gene->external_name();		## Gets gene external name
		    if ($external =~ /^[ ]*$/) {
		        $external = "N/A";			## Fills in empty external names with N/A
		    }
		my $type = $gene->biotype();			## Gets gene type
		my $status = $gene->status();			## Gets gene status
	    
		print "<td><a href= 'http://uswest.ensembl.org/Bos_taurus/Gene/Summary?db=core;g=$ID' target='_blank'> $ID</a></td>";
		print "<td>$beg</td><td>$ending</td><td>$strand</td><td>$len</td><td>$desc</td><td>$external</td><td>$type</td><td>$status</td></tr>";   ## prints table
	  
	    
	    }
	
	print "</table></pre>";
	
	my $panel = Bio::Graphics::Panel->new(-length => $length, -width => 800, -pad_left=>100, -pad_right=>200,	## Creates panel of graphic display	
					      -start=>$startPos, -end=>$endPos);
	my $scale = Bio::SeqFeature::Generic->new(-start => $startPos, -end => $endPos);				## Creates scale for graphic display
	$panel->add_track($scale, -glyph => 'arrow', -tick => 2, -fgcolor => 'black', -double => 1);			
	my $color;
	
	foreach my $gene (@genes_in_slice)  {				## retrieves necessary info 
	    my $name = $gene->stable_id();
	    my $start = $gene->seq_region_start();
	    my $end = $gene->seq_region_end();
	    my $type = $gene->biotype();
	    my $strand = $gene->strand();
	    
	    if ($type =~ /^protein_coding$/) {				# If gene is protein coding it will be displayed in red
		$color = "red";
	    }
	    else {
		$color = "black";					## All other genes will appear black
	    }
	  
	    my $combined = "$name ($start - $end)";
	    my $track = $panel->add_track(-glyph => 'transcript2', -stranded => 1, -label => 1, -fontcolor => "$color",
					  -bgcolor => 'blue', -description => $type);
	    my $feature = Bio::SeqFeature::Generic->new(-display_name => $combined, -start => $start, -end => $end, -strand => $strand);
	    $track->add_feature($feature);
	    
	}
	
	open FH, ">genes.png" or die $!;
	print FH $panel->png;
	close FH;
	print "<img src='genes.png'/>";
	print "</br>";
	print "<a href = \"http://XXXXXXXXXXXXXXXXXXXXXX//joe_viewgenes.cgi\">Back To Gene Viewer</a><br/>";
	print "<a href = \"http://XXXXXXXXXXXXXXXXXXXXXX//joe_a4.html\">Home</a>";
	}
	
	elsif (scalar @errors > 0) {		## If validation fails
	    print Header();
	    foreach (@errors) {
		print "<font color='red'>$_</font></br>";
	    }
	    print form($chromosome,$startPos,$endPos);
	    print "<a href = \"http://XXXXXXXXXXXXXXXXXXXXXX//joe_a4.html\">Home</a>";
	}
    }
}

print ending();




#########################   Sub Routines   #########################

sub Beginning {						# Stores needed beginning HTML code, also allowing for title creation
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


sub Header {					# Stores text output (header, purpose) that will be used on webpage
    return <<HH;
    <h2>
	<font color='red'>Gene Viewer (Bos Taurus)</font>
    </h2>
    <h4>
    This program will access the ensembl database and retrieve all genes within a selected region of a chromosome.</br>
    Select a chromosome, and enter a starting and ending position.</br>
    Positions must not be within 1000 kb or greater than 10,000,000 kb of each other.</br>
    Positions must be integers, and entered without commas.</br></br>
    Examples of good viewing regions:</br>
    1 - 500,000 on chromosome 1</br>
    900,000 - 1,800,000 on chromosome 3</br>
    1,000,000 - 1,500,000 on chromosome 7</br>
    </h4>

HH
}


sub Ending {			# Stores needed ending HTML code
    return <<END;
</body>
</html>
END
}


sub form {				
    my $formpage = "";
    my $choice = shift;
    my $startPos = shift;
    my $endPos = shift;
    $formpage .= <<F;
     <form method="post" action="$0" enctype="multipart/form-data">
     <table border="0">
     <tr>
     <td>Chromosome:</td><td><select name="choice"/>
F
my @choice = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16,
	      17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 'X', 'MT');
foreach (@choice) {
    my $opt = "";
    $opt = " selected='selected'" if ($choice eq "$_");
    $formpage .= "<option $opt>$_</option>";
}
$formpage .= <<F;
    </select>
    </td>
    </tr>
    <tr>
    <td>Start Position:</td><td><input type="text" name="startpos" value="$startPos"/></td>
    </tr>
    <tr>
    <td>End Position:</td><td><input type="text" name="endpos" value="$endPos"/></td>
    </tr>
    <tr><td></td><td><input type="submit" value="VIEW"/></td></tr>
     </table>
     </form>
F
    return $formpage;
}
