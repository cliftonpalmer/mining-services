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
		balance_usd => sprintf('%.2f', $gbx_wallet_balance * $gbx_ticker->[0]->{price_usd}),
		uri => "https://us1.gobyte.network/?address=$gbx_wallet",
	}
);

# build table data from each miner host
my @miner_table = ();
for my $hostname (qw/ miner1 /) {
	my $nvidia_smi = `/usr/bin/ssh -o ConnectTimeout=5 cpalmer\@$hostname "nvidia-smi"`;
	my $systemctl_status = `/usr/bin/ssh -o ConnectTimeout=5 cpalmer\@$hostname "systemctl status gobyte-ccminer.service"`;
	push @miner_table, {
		hostname => $hostname,
		nvidia_smi => $nvidia_smi,
		systemctl_status => $systemctl_status,
	};
}

# set up template
my $template = HTML::Template->new(
	filehandle => *DATA,
	die_on_bad_params => 0,
);
$template->param( date_utc => `date -u` );
$template->param( wallet_table => \@wallet_table );
$template->param( miner_table => \@miner_table );

print header, $template->output

__DATA__
<html>
<head>
<style>
body {
	background-color: lightgray;
}
</style>
</head>
<body>
	<!--- UTC is helpful for knowing payouts and stuff -->
	<p>
	<TMPL_VAR name=date_utc />
	</p>

	<hr>

	<!--- wallet info -->
	<p>
	<table border=1 cellpadding="5" width="100%">
		<tr>
			<th>symbol</th>
			<th>wallet</th>
			<th>balance</th>
			<th>price per coin (USD)</th>
			<th>balance (USD)</th>
		</tr>
	<TMPL_LOOP name=wallet_table>
		<tr>
			<td><TMPL_VAR name=symbol /></td>
			<td><a href="<TMPL_VAR name=uri />" target="_blank"><TMPL_VAR name=wallet /></a></td>
			<td><TMPL_VAR name=balance /></td>
			<td>$<TMPL_VAR name=price_usd /></td>
			<td>$<TMPL_VAR name=balance_usd /></td>
		</tr>
	</TMPL_LOOP>
	</table>
	</p>

	<hr>

	<!--- miner info -->
	<p>
	<table border=1 cellpadding="5" width="100%">
	<TMPL_LOOP name=miner_table>
		<tr><td><b><TMPL_VAR name=hostname /></b></td></tr>
		<tr><td><pre><TMPL_VAR name=nvidia_smi /></pre></td></tr>
		<tr><td><pre><TMPL_VAR name=systemctl_status /></pre></td></tr>
	</TMPL_LOOP>
	</table>
	</p>
</body>
</html>
