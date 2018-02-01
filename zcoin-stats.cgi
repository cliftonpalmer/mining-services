#!/usr/bin/perl
use strict;
use warnings;

use HTML::Template;
use CGI qw/ :standard /;
use JSON;

# build wallet table data
# https://github.com/miningpoolhub/php-mpos/wiki/API-Reference
my $token = $ENV{MININGPOOLHUB_API_TOKEN};
my $json_balance =
	from_json(`curl -s "https://zcoin.miningpoolhub.com/index.php?page=api&action=getuserbalance&api_key=$token&id=307328"`);
my $json_ticker =
	from_json(`curl -s https://api.coinmarketcap.com/v1/ticker/zcoin/`);

my $symbol = $json_ticker->[0]->{symbol};
my $confirmed_balance = $json_balance->{getuserbalance}{data}{confirmed};
my $unconfirmed_balance = $json_balance->{getuserbalance}{data}{unconfirmed};
my $zcoin_price_usd = $json_ticker->[0]->{price_usd};

my @wallet_table = (
	{
		symbol => $symbol,
		confirmed_balance => $confirmed_balance,
		unconfirmed_balance => $unconfirmed_balance,
		price_usd => $zcoin_price_usd,
		balance_usd => sprintf('%.2f', $confirmed_balance * $zcoin_price_usd),
		uri => "https://zcoin.miningpoolhub.com/index.php?page=dashboard",
	}
);

# build table data from each miner host
my @miner_table = ();
for my $hostname (qw/ miner1 /) {
	my $nvidia_smi = `/usr/bin/ssh -o ConnectTimeout=5 cpalmer\@$hostname "nvidia-smi"`;
	my $systemctl_status = `/usr/bin/ssh -o ConnectTimeout=5 cpalmer\@$hostname "systemctl status zcoin-ccminer.service"`;
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
			<th>confirmed balance</th>
			<th>unconfirmed balance</th>
			<th>price per coin (USD)</th>
			<th>balance (USD)</th>
			<th>URI</th>
		</tr>
	<TMPL_LOOP name=wallet_table>
		<tr>
			<td><TMPL_VAR name=symbol /></td>
			<td><TMPL_VAR name=confirmed_balance /></td>
			<td><TMPL_VAR name=unconfirmed_balance /></td>
			<td>$<TMPL_VAR name=price_usd /></td>
			<td>$<TMPL_VAR name=balance_usd /></td>
			<td><a href="<TMPL_VAR name=uri />">MiningPoolHub</a></td>
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
