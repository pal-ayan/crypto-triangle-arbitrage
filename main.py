from datetime import datetime
from time import sleep

from log import log
from master import master
from find_path import path
from perform_arbitrage import arbitrage
import csv
import time

l = log()
l.log_info('***********START***********')

start_time = datetime.now()

m = master(l)
m.init_markets_df()

a = arbitrage(m)
temp_list = []


with open('final_path.txt', 'r') as the_file:
    reader = csv.reader(the_file)
    data = list(reader)
    for ls in data:
        temp_list.append(ls)


t_end = time.time() + 60 * 60
while time.time() < t_end:
    current_cycle_start = datetime.now()
    a.find(temp_list)
    current_cycle_end = datetime.now() - current_cycle_start
    l.log_info('current cycle completion took -> %s' % current_cycle_end)
    print('current cycle completion took -> %s' % current_cycle_end)

print(a.accumulation)

time_diff = datetime.now() - start_time
l.log_info('processing completion took -> %s' % time_diff)

m.join_threads()

time_diff = datetime.now() - start_time
l.log_info('***********END***********  ' + 'script completion took -> %s' % time_diff)