#!/usr/bin/perl
use strict;
use warnings;

use CGI qw/ :standard /;
use JSON;

print header;

# print what I've earned so far
my $gbx_wallet = 'GcypgZPyMVWWFv9kG9uCmWPG1ZeZSyE7Z7';
my $gbx_wallet_balance =
	`curl http://gobyte.ezmine.io/ext/getbalance/$gbx_wallet`;

# get price in USD
my $gbx_ticker =
	from_json(`curl https://api.coinmarketcap.com/v1/ticker/gobyte/`);
my $gbx_price_usd = $gbx_ticker->[0]->{price_usd};
my $gbx_wallet_balance_usd =
	sprintf '%.2f', $gbx_wallet_balance * $gbx_price_usd;

print p(
	h3("Earned so far:"),
	br("$gbx_wallet: $gbx_wallet_balance GBX"),
	br("$gbx_wallet: $gbx_wallet_balance_usd USD"),
);

# print nvidia-smi data from each miner
for my $hostname (qw/ miner1 /) {
	print p(
		hr,
		h3($hostname),
		pre(`/usr/bin/ssh cpalmer\@$hostname "nvidia-smi"`)
	)
}
