#!/bin/bash

search_dir="/home/murphy/Documents/repository/crypto-triangle-arbitrage/processes"

for filename in "$search_dir"/*
do
  echo "$filename"
  while read -r line; do
	  name="$line"
    	  echo "Name read from file - $name"
    	  ps cax | grep $name > /dev/null
        if [ $? -eq 0 ]; then
          echo "Process is running."
          kill -9 $name
        else
          echo "Process is not running."
        fi
  done < "$filename"
done

kill -9 $(ps aux | grep crypto-triangle-arbitrage/chromedriver/chromedriver | awk '{print $2}')
kill -9 $(ps aux | grep AppleWebKit | awk '{print $2}')

rm /home/murphy/Documents/repository/crypto-triangle-arbitrage/processes/*
rm /home/murphy/Documents/repository/crypto-triangle-arbitrage/latest_price/*