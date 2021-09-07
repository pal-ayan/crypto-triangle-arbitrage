from datetime import datetime
from time import sleep

from log import log
from master import master
from find_path import path
from get_arbitrage import arbitrage
import csv
import time

l = log()
l.log_info('***********START***********')

start_time = datetime.now()
prev_price = 0
m = master(l)
while True:
    curr_price = float(m.call.get_current_price('TRXINR'))
    change = (curr_price - prev_price)/curr_price * 100
    prev_price = curr_price
    print('Current Price '+str(curr_price)+ ' change since last '+str(change))
    sleep(5)

