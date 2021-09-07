class path:

    def __init__(self, master):
        self.l = master.l
        self.m = master
        self.markets_df = master.markets_df
        self.t_markets_df = master.t_markets_df
        self.call = master.call
        self.slack = master.slack
        self.master_list = set()


    def get_path(self, currency, ls_current_path):
        t_m_df = self.t_markets_df
        base_df = t_m_df[t_m_df['base_currency_short_name'] == currency]
        ls_current_path.append(currency)
        if len(base_df.index) == 0:
            #print('no data found for base currency '+currency)
            return None
        for idx in base_df.index:
            target_currency = base_df['target_currency_short_name'][idx]
            #base_currency = base_df['base_currency_short_name'][idx]
            ret = self.get_path(target_currency, ls_current_path)
            if ret is None:
                ls_current_path.remove(target_currency)
        #print(ls_current_path)
        self.master_list.add(tuple(ls_current_path))