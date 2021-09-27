#!/bin/bash
filename="/home/murphy/Documents/repository/crypto-triangle-arbitrage/markets.txt"
while read -r line; do
	name="$line"
    	#echo "Name read from file - $name"
    	/home/murphy/.local/bin/pipenv run python /home/murphy/Documents/repository/crypto-triangle-arbitrage/scrape_website.py $name &
	    echo $! > "/home/murphy/Documents/repository/crypto-triangle-arbitrage/processes/${name}_process.txt"
done < "$filename"