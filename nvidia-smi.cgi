#!/usr/bin/perl
use strict;
use warnings;

use CGI qw/ :standard /;

for my $hostname (qw/ miner1 /) {
	print header,
	p(
		hr,
		h3($hostname),
		pre(`/usr/bin/ssh cpalmer\@$hostname "nvidia-smi"`)
	)
}
