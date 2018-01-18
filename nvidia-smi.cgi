#!/usr/bin/perl
use strict;
use warnings;

use CGI qw/ :standard /;

print header, pre(`/usr/bin/ssh cpalmer\@miner1 "nvidia-smi"`);
