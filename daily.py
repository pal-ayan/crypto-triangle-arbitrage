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
t_m_df = m.t_markets_df
final_set = set()
base_curr_set = t_m_df.base_currency_short_name.unique()
for base_curr in base_curr_set:
    #print('processing for '+base_curr)
    p.get_path(base_curr, [])
    for list in p.master_list:
        if len(list) > 3:
            final_set.add(list)

copy_final_set = copy.deepcopy(final_set)

for elm in final_set:
    begin_curr = elm[0]
    end_curr = elm[-1]
    df = t_m_df[(t_m_df['base_currency_short_name'] == begin_curr) & (t_m_df['target_currency_short_name'] == end_curr)]
    if len(df.index) == 1:
        #print(elm)
        continue
    else:
        copy_final_set.remove(elm)

with open('final_path.txt', 'w') as the_file:
    for ls in copy_final_set:
        val = ','.join(ls)
        the_file.write(val + '\n')



time_diff = datetime.now() - start_time
l.log_info('processing completion took -> %s' % time_diff)

m.join_threads()

time_diff = datetime.now() - start_time
l.log_info('***********END***********  ' + 'script completion took -> %s' % time_diff)