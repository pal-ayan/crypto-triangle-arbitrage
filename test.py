from datetime import datetime
from log import log
from master import master
from find_path import path
import copy


l = log()
l.log_info('***********START***********')

start_time = datetime.now()

m = master(l)
m.init_markets_df()

p = path(m)
p.get_path_two("USDT", [])
'''
for t in p.master_list:
    if len(t) >=3:
        print(t)


for key in p.market_pair_dict:
    print(p.market_pair_dict[key])
'''
p.construct_pair_list()
with open('final_path_test.txt', 'w') as the_file:
    for ls in p.master_ls_pairs:
        val = ','.join(ls)
        the_file.write(val + '\n')