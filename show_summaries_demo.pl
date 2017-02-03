#! /usr/bin/perl -w

use CGI qw(param);
use strict;
use Cwd;

my $username = param("username");
my $threadid = param("threadid");
my $versus = param("versus");
my $choice = param("choice");
my $comments = param("comments");
my $time = localtime();

print "Content-type: text/html\n\n";

my $show_next_topic = 1; #boolean

my $data = "/var/www1/lst/live/writable/discosumo/postselection/annotations/comparisons_demo.txt";
#my $data = "/www/lst/live/writable/discosumo/postselection/annotations/comparisons.txt";

my %usernames = (
"A" => "F.",
"B" => "Judith",
"C" => "Niree Bakker",
"D" => "Lian Bouten",
);


sub print_header {
    open(HD,"</var/www1/lst/live/htdocs/discosumo/postselection/header.html") or print "error opening header.html: $!\n";
    while(my $line=<HD>) {
        if ($line =~ /<title/) {
            $line = "<title>Oeps, er is iets misgegaan</title>\n";
        }
        print $line;
    }
    print
    close(HD);
}

sub print_footer {
    open(FT,"</var/www1/lst/live/htdocs/discosumo/postselection/footer.html") or print "error opening footer.html: $!\n";
    while(<FT>) {
        print;
    }
    close(FT);       
}

if (not defined $threadid) {
    # coming from login screen
    if ($username !~ /[a-zA-Z]/) {
        $show_next_topic = 0;
        &print_header;

        print "<table width=\"80\%\" align=\"center\"><tr><td><h2>Oeps, er is iets fout gegaan</h2>
        <p>Je hebt geen naam geselecteerd ($username). Wil je dat alsnog doen?
        Klik <a href=\"#\" onclick=\"history.go(-1);return false;\">hier</a> 
        om terug te gaan.</p></td></tr></table><br><br>\n";

        &print_footer;
   } 
        
} else {
    # coming from previous topic
    if ($choice !~ /[0A-Z]/) {
        $show_next_topic = 0;
        &print_header;
        print "<table width=\"80\%\" align=\"center\"><tr><td><h2>Oeps, er is iets fout gegaan</h2>
        <p>Je hebt geen keuze gemaakt voor 1 van de twee samenvattingen (of 'Ik weet het niet' gekozen).<br>
        Choice: $choice<br>
        Versus: $versus<br>
        Klik <a href=\"#\" onclick=\"history.go(-1);\">hier</a> om terug te gaan naar het topic.</p></td></tr></table><br><br>\n";
        &print_footer;
    } elsif ($choice eq "NA" && length($comments) < 4) {
        $show_next_topic = 0;
        &print_header;
        print "<table width=\"80\%\" align=\"center\"><tr><td><h2>Oeps, er is iets fout gegaan</h2>
        <p>Je hebt 'Ik weet het niet' gekozen maar het opmerkingen-veld leeggelaten.
        Wil je in het opmerkingen-veld invullen waarom je geen keuze kon maken?<br>
        Klik <a href=\"#\" onclick=\"history.go(-1);\">hier</a> om terug te gaan naar het topic.</p></td></tr></table><br><br>\n";
        &print_footer;
    }    
}

if ($show_next_topic == 1) {
    #print "hoi";
    my $picked_file;
    my $nooffilesleftforuser=123;
	my $sampledir = "/var/www1/lst/live/htdocs/discosumo/postselection/sample_demo/";
	#my $sampledir = "/www/lst/live/htdocs/discosumo/postselection/sample_demo/";
	my $nofilesforuser = 0;
	
	if ($threadid =~ /[0-9a-zA-Z]/){        

		open(DATA, ">>$data") or printf "error opening %s for writing:  %s ; cwd=%s<br>\n", $data, $!, getcwd;
		print DATA "$time\t$username\t$threadid\t$versus\t$choice\t$comments\n" if ($threadid ne "");
		close(DATA);
    }
    my %files_done;
    #my %noofusers_per_file;
    open(DATA, "<$data") or printf "error opening %s for reading:  %s ; cwd=%s<br><br>\n", $data, $!, getcwd;
    while(<DATA>) {
    #    print;
        chomp;
        my ($time,$uname,$threadid,$versus,$choice,$comments) = split(/\t/);
        if (defined $threadid) {
            #my $f = $threadid.".html";
            #my $f = $threadid;
            
            $files_done{$uname}{$versus} = 1;
            
            #print "DONE: $versus<br>";

        } 
    }
    close(DATA);
    
    $nofilesforuser = scalar(keys %{$files_done{$username}});

    
    my @htmlfiles;
    opendir(DIR, $sampledir) or printf "$!\n$sampledir\n";
    while (my $file = readdir(DIR)) {
        next if ($file !~ /html/);
        #print $file;
        chomp($file);

        push(@htmlfiles,$file)
        
    }
    if (scalar(@htmlfiles) > 0) {
        
        my @filesnotdonebyuser;
        closedir(DIR);
        my $i=0;
        foreach my $htmlf (@htmlfiles) {
            $i++;
            #print "$i\t$htmlf ";
            my $file = "evaluation/for$username/$htmlf";
            #if (not defined($files_done{$username}{$file})) {
                #print "not done";
                push(@filesnotdonebyuser,$htmlf);
            #} else {
                #print "done";
            #}
            #print "<br>\n";
        }
    
        $nooffilesleftforuser = scalar(@filesnotdonebyuser);
        if ($nooffilesleftforuser > 0) {
            my $random_number = int(rand($nooffilesleftforuser));
            $picked_file = $filesnotdonebyuser[$random_number];
        }

    } 
	
	#print "<br>$sampledir/$picked_file";
    open(HTML,"<$sampledir/$picked_file") or print "error opening $picked_file for reading<br><br>\n";
    my @htmllines = <HTML>;
    foreach my $line (@htmllines) {
        if ($choice =~ /[0A-Z]/) {
            if ($line =~ /<table width="60%">/ ) {
                my $maker = "";
                if ($choice eq "A" && $versus =~ /2-vs-3/) {
                    $maker = "een mens";
                } elsif ($choice eq "A" && $versus =~ /3-vs-2/) {
                    $maker = "de computer";
                } elsif ($choice eq "B" && $versus =~ /2-vs-3/) {
                    $maker = "de computer";
                } elsif ($choice eq "B" && $versus =~ /3-vs-2/) {
                    $maker = "een mens";
                }
                $line .= "<tr><td colspan=\"3\"><center><h3>Je koos voor de samenvatting ($choice) die door $maker gemaakt is.</h3></center><br></td></tr>\n";
            }
        }
        if ($line =~ /<input type="hidden" name="threadid"/) {
            $line .= "<input type=\"hidden\" name=\"username\" value=\"$username\">\n";
        }
        print $line;
    }
    close(HTML)
    
}



