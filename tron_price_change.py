from datetime import datetime
from time import sleep

from log import log
from master import master

l = log()
l.log_info('***********START***********')

start_time = datetime.now()
prev_price = 0
m = master(l)
while True:
    curr_price, timestamp = m.call.get_current_price_with_timestamp('BTCUSDT')
    #change = (curr_price - prev_price)/curr_price * 100
    #prev_price = curr_price
    print('At current time '+str(datetime.now())+' Price of BTCUSDT '+str(curr_price)+' for timestamp on response '+str(timestamp))
    sleep(1)