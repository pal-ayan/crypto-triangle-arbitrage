from datetime import datetime
from log import log
from master import master
from find_path import path
import sys

l = log()
l.log_info('***********START***********')

start_time = datetime.now()

m = master(l)
m.init_markets_df()

p = path(m)
#p.get_path(sys.argv[1], [])
p.get_path("USDT", [])


p.construct_pair_list()
with open('txt/final_path.txt', 'w') as the_file:
    for ls in p.master_ls_pairs:
        val = ','.join(ls)
        the_file.write(val + '\n')
#print(p.exclusive_market_list)
with open('txt/markets.txt', 'w') as the_file:
    for val in p.exclusive_market_list:
        the_file.write(val + '\n')