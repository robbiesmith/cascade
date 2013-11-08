#!/usr/bin/env perl
use strict;
use warnings;

use POSIX qw(strftime);
use Date::Parse;



my $pubtime = "Thu, 7 Nov 2013 10:31:41 +0000";
					$pubtime = str2time($pubtime);
					if($pubtime) {
						$pubtime = strftime("%a, %b %e %r", localtime($pubtime));
					} else {
						$pubtime="N/A";
					}
					print $pubtime;
					