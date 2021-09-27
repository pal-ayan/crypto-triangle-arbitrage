class path:

    def __init__(self, master):
        self.l = master.l
        self.m = master
        self.markets_df = master.markets_df
        self.t_markets_df = master.t_markets_df
        self.call = master.call
        self.slack = master.slack
        self.master_list = set()
        self.market_pair_dict = {}
        self.master_ls_pairs = set()
        self.excluded_currency_list = ['USDC', 'TUSD']
        self.exclusive_market_list = set()



    def get_path(self, currency, ls_current_path):
        t_m_df = self.t_markets_df
        #base_df = t_m_df[t_m_df['base_currency_short_name'] == currency and t_m_df['ecode'] == 'B']
        base_df = t_m_df.loc[(t_m_df['base_currency_short_name'] == currency) & (t_m_df['ecode'] == 'B')]
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
            elif len(ls_current_path) >= 3:
                if self.can_return_to_root(ret, ls_current_path[-1]):
                    self.master_list.add(tuple(ls_current_path))
        #print(ls_current_path)
        self.master_list.add(tuple(ls_current_path))


    def can_return_to_root(self, currency, root):
        base_df = self.t_markets_df.loc[(self.t_markets_df['base_currency_short_name'] == currency) & (self.t_markets_df['ecode'] == 'B')]
        for idx in base_df.index:
            target_currency = base_df['target_currency_short_name'][idx]
            if root == target_currency:
                return True
        return False

    def construct_pair_list(self):
        for ls in self.master_list:
            if len(ls) >= 3:
                ls_pairs = []
                for index, elem in enumerate(ls):
                    if (index+1 < len(ls) and index - 1 >= 0):
                        prev_el = str(ls[index - 1])
                        curr_el = str(elem)
                        market = curr_el + prev_el
                        ls_pairs.append(market)
                    if index + 1 >= len(ls):
                        curr = elem
                        prev = ls[index -1]
                        next = ls[0]
                        market = curr + prev
                        ls_pairs.append(market)
                        market = curr + next
                        ls_pairs.append(market)

                #print(ls_pairs)
                if not self.has_excluded_currency(ls_pairs):
                    compatible = True
                    for ls in ls_pairs:
                        if not self.has_market_order(ls):
                            compatible = False
                            break
                        self.exclusive_market_list.add(ls)
                    if compatible:
                        self.master_ls_pairs.add(tuple(ls_pairs))


    def has_excluded_currency(self, ls):
        for elm in ls:
            for excluded_currency in self.excluded_currency_list:
                if excluded_currency in elm:
                    return True
        return False

    def has_market_order(self, market):
        df = self.t_markets_df[self.t_markets_df['coindcx_name'] == market]
        sub_df = df['order_types']
        if "market_order" in sub_df.tolist()[0]:
            return True


