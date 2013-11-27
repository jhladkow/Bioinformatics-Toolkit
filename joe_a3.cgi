#!/usr/bin/perl
use strict;
use warnings;
use CGI qw/:standard/;


print "Content-type: text/html\n\n";

if (!param())  {				# Displays empty form when user first accesses web page
    print Beginning("Joe Hladkowicz - a3");	# Joe Hladkowicz - a3 will be title of page
    print Header();
    print form();
}

else {

    if (param())  {					# Begins program when user chooses submit
        my $FILENAME = param("uploadedPDB");  		# Stores name of uploaded file
        my $EMAILADDRESS = param("emailadr");		# Stores email address
    
	if ($FILENAME =~ /^[0-9][a-z0-9]{3}(\.pdb$)/i)  {				# Verifies uploaded file	
	    if ($EMAILADDRESS =~ /^[a-z][a-z0-9\._]+@[a-z]+(\.[a-z]+)+$/i) {		# Verifies email address
	
		my $EMAILMSG = "An email containing the output has been sent to $EMAILADDRESS";		# Stores message that is contained in output
    
		open MAIL, "|/usr/sbin/sendmail -t" or $EMAILMSG = "ERROR: Unable to locate email program - an email cannot be sent\n";		# Opens mail program, if it fails email message changes
		print MAIL "To: $EMAILADDRESS\n";			
		print MAIL "From: Assign3\n";
		print MAIL "Subject: Analysis of $FILENAME\n";
    
		my $FILE = upload("uploadedPDB");			# Stores the uploaded file as a scalar
		my @textfile = <$FILE>;					# Creates an array of the uploaded file
    
my %aminoacids = ("ALA" => "A",     					# Hash that stores amino acid 3 letter and 1 letter codes
                  "ASX" => "B",
                  "CYS" => "C",
                  "ASP" => "D",
                  "GLU" => "E",
                  "PHE" => "F",
                  "GLY" => "G",
                  "HIS" => "H",
                  "ILE" => "I",
                  "LYS" => "K",
                  "LEU" => "L",
                  "MET" => "M",
                  "ASN" => "N",
                  "PRO" => "P",
                  "GLN" => "Q",
                  "ARG" => "R",
                  "SER" => "S",
                  "THR" => "T",
                  "VAL" => "V",
                  "TRP" => "W",
                  "XAA" => "X",
                  "TYR" => "Y",
                  "GLX" => "Z");
    
	my @modres = grep /^MODRES/, @textfile;       		# Scans pdb file for MODRES lines                          
        
	if (scalar @modres >0) {                                    # If MODRES lines are in the file a message is displayed and emailed to the user saying this file cannot be processed            
            print ("File contains MODRES lines - Cannot be processed.<br\>");
            print "<a href = \"http://XXXXXXXXXXXX/joe_a3.cgi\">Back To Converter</a>";
	    print MAIL "File contains MODRES lines - Cannot be processed.\n";
	    print MAIL "http://XXXXXXXXXXXX/joe_a3.cgi";
	    close MAIL;
	}
        
	else {
        
	    my @filelines = grep /^SEQRES/, @textfile;      		# Stores all SEQRES lines in an array                               
	    my @header = grep /^HEADER/, @textfile;          		# Stores all HEADER lines in an array                       
	    chomp @header;                                      	                    
	    my $PDBid = substr $header[0], 62, -14;              	# Cuts pdb id out of HEADER                                 
	    my @title = grep /^TITLE/, @textfile;                	# Stores all TITLE lines in an array                                    
	    chomp @title;                                                   
	    my @cutTitle = "";                                                               
	    my $edit;
    
	    foreach my $titleline (@title) {                    	# Loops through all TITLE lines                                            
		my $editTitleLine = substr $titleline, 10,59;       	# Gets rid of non-title elements                         
		$edit = $editTitleLine;
		$edit =~ s/ *$//g;                                  	# Gets rid of trailing whitespace                
		push @cutTitle, $edit;                                	# Adds the editted title lines to an array                       
	    }
        
	    chomp @cutTitle;
	    my $jointitle = join "", @cutTitle;             		# joins editted TITLE lines together into a scalar                               
	    my $chainID = "";
	    my $chainLength = "";
	    my %chainIDS;						# Hash that will store chain ID as key, and chain sequence as value
        
	    foreach my $lines (@filelines) {                            # Loops through SEQRES lines             
		$chainID = substr $lines, 11,1;				# Stores chain ID
		$chainIDS{$chainID} = ("");				# Fills in all the keys with the chain ID's
	    }
        
	    my %aalength;						# Hash that wil store chain ID as key, and chain length as value
	    
	    foreach my $lines (@filelines) {                            # Loops through SEQRES lines           
		my $SEQchainID = substr $lines, 11,1;                   # Stores the chain ID            
		my $seqlength = substr $lines, 13,4;                    # Stores the chain length            
		$seqlength =~ s/^ +//g;                                 # If the length is less than 4 digits, beginning whitespace will be cut out         
		$aalength{$SEQchainID} = ("$seqlength");                # Fills in keys and values           
		my $editLines = substr $lines, 19,70;                   # Gets rid of anything that isnt an amino acid 3 letter code in the SEQRES lines           
		my @arrayThree = split / /, $editLines;                 # Adds all 3 letter codes as an individual element into an array            
		my $newseq = "";
            
            foreach my $three (@arrayThree) {                         	# Loops through all 3 letter codes                   
                foreach my $aathree (%aminoacids) {                     # Loops through all elements of the amino acid hash   
                    if ($aathree eq $three) {				# Converts all 3 letter codes into the 1 letter code via amino acid hash
                    $newseq = $newseq . $aminoacids{$aathree};          
                    }
                }
            }
        
	    foreach my $keys1 (keys %chainIDS) {                      	# Loops though all keys (chain ID) of chainIDS hash              
		if ($keys1 eq $SEQchainID) {                            # Adds all sequences with same chain ID as values            
		    $chainIDS{$keys1} = $chainIDS{$keys1} . $newseq;
		}
	    }
        }                                                            
        
	    print "<pre>";					# Needed for proper HTML formatting
	    print MAIL "\n";					# Needed for proper email formatting
	    foreach my $keys1 (sort keys %chainIDS) {    				# Loops through all keys (chain ID) of chainIDS hash                           
		my $len = $aalength{$keys1};            				# Stores the length into a scalar                            
		my $fulltitle = ">$PDBid:$keys1|$len aa|$jointitle";               	# Title line that includes PDB id, length, and title as per proper FASTA formatting
		my $fulledittitle = substr $fulltitle, 0,80;                        	# Limits the title line to 80 characters
		my $foremail = "$chainIDS{$keys1}";					# Makes a copy of stored sequence to allow for proper formatting of both HTML and email formatting
		$foremail =~ s/([ABCDEFGHIKLMNPQRSTVWXYZ]{50})/$1\n/g;			# Contains \n for email formatting
		$chainIDS{$keys1} =~ s/([ABCDEFGHIKLMNPQRSTVWXYZ]{50})/$1<br\>/g;	# Contains <br\> for HTML formatting
		print "$fulledittitle<br/>";						# Prints title line on HTML page
		print "$chainIDS{$keys1}<br/>";						# Prints chain sequence on HTML page
	    
print MAIL <<B;			# Prints title line and chain sequence to email
$fulledittitle
$foremail
B
	    }
	    print MAIL "http://XXXXXXXXXXXXXXXX/joe_a3.cgi";		# Prints a link to program in email
	    print "</pre>";
	    print "$EMAILMSG<br\>";			# Prints message on HTML page letting user know an email has been sent to them, or an error message if opening mail program was unsuccessful
	    print "<a href = \"http://XXXXXXXXXXXXXXX/joe_a3.cgi\">Back To Converter</a>";		# Prints link to program on HTML page
	}
	    close MAIL;
    }
	
	elsif ($EMAILADDRESS !~ /^[a-z][a-z0-9\._]+@[a-z]+(\.[a-z]+)+$/i) {		# If email address is not valid
	    
	    print Header();	
	    print "<font color='red'>ERROR - EMAIL ADDRESS NOT VALID (ex. user_name\@server.com)</font>";	# Error message with example email
	    print form($EMAILADDRESS);			# Will contain previous email address entered in regenerated form
	    
	}
    }
	elsif ($FILENAME !~ /^[0-9][a-z0-9]{3}(\.pdb$)/i) {			# If pdb file is not valid
	    if ($EMAILADDRESS =~ /^[a-z][a-z0-9\._]+@[a-z]+(\.[a-z]+)+$/i) {
		print Header();
		print "<font color='red'>ERROR - NOT A VALID FILE TYPE (ex. 1CTF.pdb)</font>";		# Error message with example file
		print form($EMAILADDRESS);
	    }
	    elsif ($EMAILADDRESS !~ /^[a-z][a-z0-9\._]+@[a-z]+(\.[a-z]+)+$/i) {
		print Header();
		print "<font color='red'>ERROR - NOT A VALID FILE TYPE (ex. 1CTF.pdb)</font></br>";			# Error messages for both invalid email and file
		print "<font color='red'>ERROR - EMAIL ADDRESS NOT VALID (ex. user_name\@server.com)</font>";
		print form($EMAILADDRESS);
	    }
	}    
    }
        
    else {
}
}
print validate();		# HTML validation link
print Ending();		



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


sub Header {					# Stores text output (header, purpose, instructions) that will be used on webpage
    return <<HH;
    <h2>
	<font color='red'>.pdb</font> to <font color='green'>FASTA</font> Converter<br/>
    </h2>
    <h4>
The purpose of this program is to output a protein sequence from a<br/>
given pdb file in FASTA format.<br/>
This program will work with either single, or multi-chain proteins, but not<br/>
for those that have undergone post-translational modification.<br/>
To use this program select a .pdb file that is currently on your computer<br/>
and enter a valid email address.<br/>
Output will be emailed as well as displayed on screen.<br/>
    </h4>
HH
}


sub Ending {			# Stores needed ending HTML code
    return <<END;
</body>
</html>
END
}


sub form {				# HTML form that will accept a file and a textbox for email organized into a table
    my $EMAILADDRESS = shift;
    return <<F;
     <form method="post" action="$0" enctype="multipart/form-data">
     <table border="0">
     <tr>
	<td>PDB FILE:</td><td><input type="file" name="uploadedPDB"/></td>
     </tr>
     <tr>
	<td>Email:</td><td><input type="text" name="emailadr" value="$EMAILADDRESS"/></td>
     </tr>
     <tr>
	<td></td><td><input type="submit"/>
     </table>
     </form>
     </td></tr>
F
}


sub validate {				# Stores HTML for validation
    return <<VALID;
        <p>
    	    <a href="http://validator.w3.org/check?uri=referer">
    		<img src="http://www.w3.org/Icons/valid-xhtml10" alt="Valid XHTML 1.0 Transitional" height="31" width="88" />
    	    </a>
  	</p>
VALID
}
