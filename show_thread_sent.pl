#! /usr/bin/perl -w

use CGI qw(param);
use strict;
use Cwd;

my $forumtype = param("forumtype");
#my $forumtype = "viva";
my $username = param("username");
my $sex = param("sex");
my $age = param("age");
#my $username = "suzan";
my $email = param("email");
#my $email = "sverbern\@gmail.com";
my $sonaid = param("sonaid");

my $threadid = param("threadid");
my $selected = param("selected");
my $comments = param("comments");
my $time = localtime();

my $nrofratersperfile = 3;

print "Content-type: text/html\n\n";

my $show_next_topic = 1; #boolean

my $data = "/var/www1/lst/live/writable/discosumo/postselection/annotations/selected_posts_sents_nl.txt";
#my $data = "/www/lst/live/writable/discosumo/postselection/annotations/selected_posts_sents_nl.txt";


open(DATA, "<$data") or printf "error opening %s for reading:  %s ; cwd=%s<br><br>\n", $data, $!, getcwd;
my %emailmatch;
my %example_done;
if ($threadid eq "example") {
    $example_done{$username} =1;
}
while(<DATA>) {
#    print;
    chomp;
    my ($time,$uname,$age,$sex,$email,$sonaid,$threadid,$selected,$comments) = split(/\t/);
    $emailmatch{$uname} = $email;
    if ($threadid eq "example") {
    	$example_done{$uname} =1;
	}
}
close(DATA);

sub print_header {
    open(HD,"</var/www1/lst/live/htdocs/discosumo/postselection/header.html") or print "error opening header.html: $!\n";
    while(my $line=<HD>) {
        if ($line =~ /<title/) {
            $line = "<title>Oops, something went wrong</title>\n";
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
    if ($username !~ /[a-z0-9A-Z]/) {
        $show_next_topic = 0;
        &print_header;

        print "<table width=\"80\%\" align=\"center\"><tr><td><h2>Oops, something went wrong</h2>
        <p>Please fill in a name.
        Click <a href=\"#\" onclick=\"history.go(-1);return false;\">here</a> 
        to go back.</p></td></tr></table><br><br>\n";

        &print_footer;
   } elsif ($age !~ /[0-9]/ && not defined $emailmatch{$username} ) {
        $show_next_topic = 0;
        &print_header;

        print "<table width=\"80\%\" align=\"center\"><tr><td><h2>Oops, something went wrong</h2>
        <p>Please fill in your age.
        Click <a href=\"#\" onclick=\"history.go(-1);return false;\">here</a> 
        to go back.</p></td></tr></table><br><br>\n";

        &print_footer;
    } elsif ($sex !~ /ale/ && not defined $emailmatch{$username} ) {
        $show_next_topic = 0;
        &print_header;

        print "<table width=\"80\%\" align=\"center\"><tr><td><h2>Oops, something went wrong</h2>
        <p>Please fill in your gender.
        Click <a href=\"#\" onclick=\"history.go(-1);return false;\">here</a> 
        to go back.</p></td></tr></table><br><br>\n";

        &print_footer;
     }  elsif (defined $emailmatch{$username} && $emailmatch{$username} ne $email) {
        $show_next_topic = 0;
        &print_header;

        print "<table width=\"80\%\" align=\"center\"><tr><td><h2>Oops, something went wrong</h2>
        <p>The name you chose has been used before with a different e-mail address. Did you logged in before with this username ($username), please fill in the same e-mail address as previous time. Did you not logged in before, please choose a different username.
        Click <a href=\"#\" onclick=\"history.go(-1);return false;\">here</a> 
        to go back.</p></td></tr></table><br><br>\n";
        
        &print_footer;
    } else{
    open(DATA, ">>$data") or printf "error opening %s for writing:  %s ; cwd=%s<br>\n", $data, $!, getcwd;
    print DATA "$time\t$username\t$age\t$sex\t$email\t$sonaid\n";
    close(DATA);

    }
} else {
    # coming from previous topic
    if ($selected !~ /[0-9]/ && length($comments) < 4) {
        $show_next_topic = 0;
        &print_header;
        print "<table width=\"80\%\" align=\"center\"><tr><td><h2>Oops, something went wrong</h2>
        <p>You did not select any posts or sentences but kept the comments field empty. Please fill in why you did not select any posts or sentences for this thread.
        <br>
        Click <a href=\"#\" onclick=\"history.go(-1);return false;\">here</a> 
        to go back to the thread.</p></td></tr></table><br><br>\n";
        &print_footer;
    }    
}

if ($show_next_topic == 1) {
    my $picked_file = "example.html";
    my $nooffilesleftforuser = 1000;
    my $totalfilesleft = 1000;
	my $sampledir = "/var/www1/lst/live/htdocs/discosumo/postselection/sample_gistnl";
	#my $sampledir = "/www/lst/live/htdocs/discosumo/postselection/sample_gistnl";
	my $nofilesforuser = 0;
	
	if ($threadid =~ /[0-9a-zA-Z]/ or $example_done{$username}){        

		open(DATA, ">>$data") or printf "error opening %s for writing:  %s ; cwd=%s<br>\n", $data, $!, getcwd;
		print DATA "$time\t$username\t$age\t$sex\t$email\t$sonaid\t$threadid\t$selected\t$comments\n" if ($threadid ne "");
		close(DATA);

		my %files_done;
		#my %noofusers_per_file;
		my %users_per_file;
		open(DATA, "<$data") or printf "error opening %s for reading:  %s ; cwd=%s<br><br>\n", $data, $!, getcwd;
		while(<DATA>) {
		#    print;
			chomp;
			my ($time,$uname,$age,$sex,$email,$sonaid,$threadid,$selected,$comments) = split(/\t/);
			if (defined $threadid && $threadid ne "example") {
				my $f = $threadid.".sent.html";
				$files_done{$uname}{$f} = 1;
				#$noofusers_per_file{$f}++;
				$users_per_file{$f}{$uname} = 1;
			} 
		}
		close(DATA);
		
		$nofilesforuser = scalar(keys %{$files_done{$username}});


		my @htmlfiles;
		opendir(DIR, $sampledir) or printf "$!\n$sampledir\n";
		while (my $file = readdir(DIR)) {
			next if ($file !~ /sent\.html/ or $file =~ /example/);
			#print $file;
			chomp($file);
			my @users_per_file = keys %{$users_per_file{$file}};
			if (scalar(@users_per_file) < $nrofratersperfile) {
				push(@htmlfiles,$file)
			}
		}
		if (scalar(@htmlfiles) > 0) {
			
			my @filesnotdonebyuser;
			closedir(DIR);
			my $i=0;
			foreach my $htmlf (@htmlfiles) {
				$i++;
				#print "$i\t$htmlf ";
				if (not defined($files_done{$username}{$htmlf})) {
					#print "not done";
					push(@filesnotdonebyuser,$htmlf);
				}
				#print "<br>\n";
			}
		
			$nooffilesleftforuser = scalar(@filesnotdonebyuser);
			if ($nooffilesleftforuser > 0) {
				my $random_number = int(rand($nooffilesleftforuser));
				$picked_file = $filesnotdonebyuser[$random_number];
			}
			#print $nooffiles." ".$random_number." ".$picked_file."\n";
			#while (defined($files_done{$username}{$picked_file})) {

			#	$random_number = int(rand($nooffiles));
			#	$picked_file = $htmlfiles[$random_number];
			#}
		} else {
			$totalfilesleft = 0;
		}
	}
    open(HTML,"<$sampledir/$picked_file") or print "error opening $picked_file for reading<br><br>\n";
    my @htmllines = <HTML>;
    foreach my $line (@htmllines) {
        if ($line =~ /<body/) {
            $line .= "\n\n<div style=\"font-size:small;padding-left:2em;border-bottom-style:solid\">You are logged in as $username ($email). You completed $nofilesforuser threads. ";
            if ($totalfilesleft == 0) {
            	$line .= "All threads were summarized by sufficient participants so there is no work left. Thank you for your help! ";
                $line .= "If you completed at least 10 threads you will receive a gift certificate through email within a few days. ";
                $line .= "You can close this page. ";
                print $line;
                print "</div></body></html>\n";
                last; 
            } elsif ($nooffilesleftforuser == 0) {
                $line .= "Thank you very much! You completed all threads ";
                $line .= "You will receive a gift certificate through email within a few days. ";
                $line .= "You can close this page. ";
                print $line;
                print "</div></body></html>\n";
                last;            
            } elsif ($nofilesforuser%10 == 0 && $nofilesforuser >=10) {
                $line .= "Thank you very much! ";
                $line .= "You will receive a gift certificate through email within a few days. ";
                $line .= "You can close this page, of continue with more threads.";
                #print $line;
                #print "</div></body></html>\n";
                #last;
            } else {
                $line .= "You can quit at any time by closing this window, and return later for more threads. Use the same username when you return.";
            }
            $line .= "</div>\n";
        }
        if ($line =~ /<input type="hidden" name="threadid"/) {
            $line .= "<input type=\"hidden\" name=\"username\" value=\"$username\">\n";
            $line .= "<input type=\"hidden\" name=\"email\" value=\"$email\">\n";
            $line .= "<input type=\"hidden\" name=\"age\" value=\"$age\">\n";
            $line .= "<input type=\"hidden\" name=\"sex\" value=\"$sex\">\n";
            $line .= "<input type=\"hidden\" name=\"sonaid\" value=\"$sonaid\">\n";
        }
        print $line;
    }
    close(HTML)
    
}



