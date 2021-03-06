#!/usr/bin/perl
use strict;
use warnings;

use HTML::Template;
use CGI qw/ :standard /;
use JSON;

my $coin = param('coin');
$coin = 'ethereum' unless $coin;

# build wallet table data
# https://github.com/miningpoolhub/php-mpos/wiki/API-Reference
my $token = $ENV{MININGPOOLHUB_API_TOKEN};
my $json_dashboard =
	from_json(`curl -s "https://$coin.miningpoolhub.com/index.php?page=api&action=getdashboarddata&api_key=$token&id=307328"`);
my $json_ticker =
	from_json(`curl -s https://api.coinmarketcap.com/v1/ticker/$coin/`);

my $symbol = $json_ticker->[0]->{symbol};
my $confirmed_balance = $json_dashboard->{getdashboarddata}{data}{balance}{confirmed};
my $unconfirmed_balance = $json_dashboard->{getdashboarddata}{data}{balance}{unconfirmed};
my $earned_last_24h = $json_dashboard->{getdashboarddata}{data}{recent_credits_24hours}{amount};

my $coin_price_usd = $json_ticker->[0]->{price_usd};

my @wallet_table = (
	{
		symbol => $symbol,
		confirmed_balance => $confirmed_balance,
		unconfirmed_balance => $unconfirmed_balance,
		price_usd => $coin_price_usd,
		confirmed_balance_usd => sprintf('%.2f', $confirmed_balance * $coin_price_usd),
		unconfirmed_balance_usd => sprintf('%.2f', $unconfirmed_balance * $coin_price_usd),
		earned_last_24h => $earned_last_24h,
		earned_last_24h_usd  => sprintf('%.2f', $earned_last_24h * $coin_price_usd),
		uri => "https://$coin.miningpoolhub.com/index.php?page=dashboard",
		earning_monthly_usd => sprintf('%.2f', $earned_last_24h * $coin_price_usd * 30),
		earning_yearly_usd => sprintf('%.2f', $earned_last_24h * $coin_price_usd * 365.25),
	}
);

# build table data from each miner host
my %miner_tables = ();
for my $hostname (qw/ miner1 miner2 /) {
	my $data = `/usr/bin/ssh -o ConnectTimeout=5 cpalmer\@$hostname "ps -u miner -o stat,args | grep ^Z && echo 'Driver crashed' || nvidia-smi"`;
	push @{$miner_tables{nvidia}}, {
		hostname => $hostname,
		data     => $data
	};
	$data = `/usr/bin/ssh -o ConnectTimeout=5 cpalmer\@$hostname "~/bin/geth-stats"`;
	push @{$miner_tables{gethd}}, {
		hostname => $hostname,
		data     => $data
	};
	$data = `/usr/bin/ssh -o ConnectTimeout=5 cpalmer\@$hostname "systemctl status multi-algo; echo; systemctl status $coin"`;
	push @{$miner_tables{systemctl}}, {
		hostname => $hostname,
		data     => $data
	};
	$data = `/usr/bin/ssh -o ConnectTimeout=5 cpalmer\@$hostname "df -h"`;
	push @{$miner_tables{df}}, {
		hostname => $hostname,
		data     => $data
	};
}

# set up template
my $template = HTML::Template->new(
	filehandle => *DATA,
	die_on_bad_params => 0,
);
$template->param( date_utc => `date -u` );
$template->param( blockchain_uri => 'https://etherscan.io/address/0xd1bb2d62804f4e298f5260a5d03fea99504e9290' );
$template->param( wallet_table => \@wallet_table );
while (my ($name, $data) = each %miner_tables) {
	$template->param( $name => $data );
}


print header( -type => 'text/html', -charset => 'utf-8' ), $template->output

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
	<TMPL_VAR name=date_utc /> | <a href="<TMPL_VAR name=blockchain_uri />"><TMPL_VAR name=blockchain_uri /></a>
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
			<th>confirmed balance (USD)</th>
			<th>unconfirmed balance (USD)</th>
			<th>URI</th>
			<th>Earned last 24 hours</th>
			<th>Earned last 24 hours (USD)</th>
			<th>Earning monthly (USD)</th>
			<th>Earning yearly (USD)</th>
		</tr>
	<TMPL_LOOP name=wallet_table>
		<tr>
			<td><TMPL_VAR name=symbol /></td>
			<td><TMPL_VAR name=confirmed_balance /></td>
			<td><TMPL_VAR name=unconfirmed_balance /></td>
			<td>$<TMPL_VAR name=price_usd /></td>
			<td>$<TMPL_VAR name=confirmed_balance_usd /></td>
			<td>$<TMPL_VAR name=unconfirmed_balance_usd /></td>
			<td><a href="<TMPL_VAR name=uri />" target="_blank">MiningPoolHub</a></td>
			<td><TMPL_VAR name=earned_last_24h /></td>
			<td>$<TMPL_VAR name=earned_last_24h_usd /></td>
			<td>$<TMPL_VAR name=earning_monthly_usd /></td>
			<td>$<TMPL_VAR name=earning_yearly_usd /></td>
		</tr>
	</TMPL_LOOP>
	</table>
	</p>

	<hr>

	<!--- miner info -->
	<p>
		<table border=1 cellpadding="5" width="100%">
		<TMPL_LOOP name=systemctl>
			<tr><td><b><TMPL_VAR name=hostname /></b></td></tr>
			<tr><td><pre><TMPL_VAR name=data /></pre></td></tr>
		</TMPL_LOOP>
		</table>

		<table border=1 cellpadding="5" width="100%">
		<TMPL_LOOP name=nvidia>
			<tr><td><b><TMPL_VAR name=hostname /></b></td></tr>
			<tr><td><pre><TMPL_VAR name=data /></pre></td></tr>
		</TMPL_LOOP>
		</table>

		<table border=1 cellpadding="5" width="100%">
		<TMPL_LOOP name=gethd>
			<tr><td><b><TMPL_VAR name=hostname /></b></td></tr>
			<tr><td><pre><TMPL_VAR name=data /></pre></td></tr>
		</TMPL_LOOP>
		</table>

		<table border=1 cellpadding="5" width="100%">
		<TMPL_LOOP name=df>
			<tr><td><b><TMPL_VAR name=hostname /></b></td></tr>
			<tr><td><pre><TMPL_VAR name=data /></pre></td></tr>
		</TMPL_LOOP>
		</table>
	</p>
</body>
</html>
