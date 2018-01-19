#!/usr/bin/perl
use strict;
use warnings;

use HTML::Template;
use CGI qw/ :standard /;
use JSON;

# build wallet table data
my $gbx_wallet = 'GcypgZPyMVWWFv9kG9uCmWPG1ZeZSyE7Z7';
my $gbx_wallet_balance =
	`curl -s http://gobyte.ezmine.io/ext/getbalance/$gbx_wallet`;
my $gbx_ticker =
	from_json(`curl -s https://api.coinmarketcap.com/v1/ticker/gobyte/`);

my @wallet_table = (
	{
		symbol => $gbx_ticker->[0]->{symbol},
		wallet => $gbx_wallet,
		balance => $gbx_wallet_balance,
		price_usd => $gbx_ticker->[0]->{price_usd},
		balance_usd => sprintf '%.2f', 
			$gbx_wallet_balance * $gbx_ticker->[0]->{price_usd},
	}
);

# build table data from each miner host
my @miner_table = ();
for my $hostname (qw/ miner1 /) {
	my $nvidia_smi = `/usr/bin/ssh cpalmer\@$hostname "nvidia-smi"`;
	push @miner_table, {
		hostname => $hostname,
		nvidia_smi => $nvidia_smi,
	};
}

# set up template
my $template = HTML::Template->new(
	filehandle => *DATA,
	die_on_bad_params => 0,
);
$template->param( wallet_table => \@wallet_table );
$template->param( miner_table => \@miner_table );

print header, $template->output

__DATA__
<html>
<head>
</head>
<body>
	<!--- wallet info -->
	<table border=1>
		<th>
			<td>symbol</td>
			<td>wallet</td>
			<td>balance</td>
			<td>price per coin (USD)</td>
			<td>balance (USD)</td>
		</th>
	<TMPL_LOOP name=wallet_table>
		<tr>
			<td><TMPL_VAR name=symbol /></td>
			<td><TMPL_VAR name=wallet /></td>
			<td><TMPL_VAR name=balance /></td>
			<td><TMPL_VAR name=price_usd /></td>
			<td><TMPL_VAR name=balance_usd /></td>
		</tr>
	</TMPL_LOOP>
	</table>

	<!--- miner info -->
	<table border=1>
	<TMPL_LOOP name=miner_table>
		<tr><td><b><TMPL_VAR name=hostname /></b></td></tr>
		<tr><td><pre><TMPL_VAR name=nvidia_smi /></pre></td></tr>
	</TMPL_LOOP>
	</table>
</body>
</html>
