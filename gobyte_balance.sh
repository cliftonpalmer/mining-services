#!/bin/bash

curl -s 'https://us1.gobyte.network/site/wallet_results?address=GcypgZPyMVWWFv9kG9uCmWPG1ZeZSyE7Z7' | 
	grep -o 'Total Earned.* GBX' | 
	grep -o '[.0-9]* GBX' | 
	awk '{print $1}'
