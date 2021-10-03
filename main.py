from datetime import datetime
from time import sleep

from log import log
from master import master
from find_path import path
from test_arbitrage import arbitrage
import csv
import time

l = log()
l.log_info('***********START***********')

start_time = datetime.now()

m = master(l)
m.init_markets_df()

a = arbitrage(m)
temp_list = []


with open('txt/final_path.txt', 'r') as the_file:
    reader = csv.reader(the_file)
    data = list(reader)
    for ls in data:
        temp_list.append(ls)

while True:
    a.find(temp_list)


time_diff = datetime.now() - start_time
l.log_info('processing completion took -> %s' % time_diff)

m.join_threads()

time_diff = datetime.now() - start_time
l.log_info('***********END***********  ' + 'script completion took -> %s' % time_diff)