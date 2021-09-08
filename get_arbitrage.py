import numpy as np
from datetime import datetime
from order import order
from time import sleep

class arbitrage:

    def __init__(self, master):
        self.l = master.l
        self.m = master
        self.markets_df = master.markets_df
        self.t_markets_df = master.t_markets_df
        self.call = master.call
        self.slack = master.slack
        self.o = order(master)
        self.initial_quantity = {
            'USDT':0,
            'INR': 4000,
            'BTC': 0,
            'ETH': 0,
            'DAI': 0,
            'BUSD':0,
            'USDC': 0,
            'TUSD': 0,
        }
        self.accumulation = {
            'USDT': 0,
            'INR': 0,
            'BTC': 0,
            'ETH': 0,
            'DAI': 0,
            'BUSD': 0,
            'USDC': 0,
            'TUSD': 0,
        }
        self.market_pair_dict = {}
        self.market_quantity_dict = {}
        self.sell_market_symbol = None



    def find(self, set_paths):
        for ls in set_paths:
            base_currency = ls[0]
            base_quantity = self.initial_quantity[base_currency]
            if base_quantity == 0:
                continue
            ls_pairs = []
            ls_order_pairs = []
            ls_quantity = []
            for index, elem in enumerate(ls):
                if (index+1 < len(ls) and index - 1 >= 0):
                    prev_el = str(ls[index - 1])
                    curr_el = str(elem)
                    market = curr_el + prev_el
                    ls_pairs.append(market)
                    this_df = self.markets_df.loc[self.markets_df['coindcx_name'] == market]
                    self.market_pair_dict[market] = this_df['pair'].values[0]
                if index + 1 >= len(ls):
                    curr = elem
                    prev = ls[index -1]
                    next = ls[0]
                    market = curr + prev
                    ls_pairs.append(market)
                    this_df = self.markets_df.loc[self.markets_df['coindcx_name'] == market]
                    self.market_pair_dict[market] = this_df['pair'].values[0]
                    market = curr + next
                    ls_pairs.append(market)
                    this_df = self.markets_df.loc[self.markets_df['coindcx_name'] == market]
                    self.market_pair_dict[market] = this_df['pair'].values[0]

            final_quantity= 0
            initial_price = 0

            for index, pair in enumerate(ls_pairs):
                if (index + 1 < len(ls) and index - 1 >= 0):
                    p, q = self.get_quantity(ls_quantity[index-1], pair)
                    ls_quantity.append(q)
                    self.market_quantity_dict[pair] = q
                    continue
                if index + 1 >= len(ls):
                    qty = ls_quantity[-1] * float(self.call.get_latest_price(pair))
                    final_quantity = qty - 0.001 * qty
                    self.sell_market_symbol = pair
                else:
                    p, q = self.get_quantity(base_quantity, pair)
                    ls_quantity.append(q)
                    self.market_quantity_dict[pair] = q
                    initial_price = p
            initial_quantity = float(ls_quantity[0]) * initial_price
            initial_quantity = initial_quantity + 0.001 * initial_quantity
            if final_quantity > initial_quantity:

                self.place_orders()

                percent = ((final_quantity - initial_quantity) / initial_quantity) * 100
                #if percent > 0.1:
                """
                print(ls_pairs)
                print(ls_price)
                print(ls_quantity)
                """
                print('Initial ' + str(initial_quantity))
                print('Final ' + str(final_quantity))
                print('Arbitrage found for '+str(ls))
                print('Arbitrage gain percent = '+str(percent))
                accumulated_quantity = self.accumulation[base_currency]
                self.accumulation[base_currency] = accumulated_quantity + (final_quantity - initial_quantity)
            else:
                '''
                print('Arbitrage loss for ' + str(ls))
                print(ls_pairs)
                print(ls_price)
                print(ls_quantity)
                percent = ((final_quantity - initial_quantity) / initial_quantity) * 100
                print('Initial '+str(initial_quantity))
                print('Final ' + str(final_quantity))
                print('Arbitrage loss percent = ' + str(percent))
                '''
                continue

    def get_quantity(self, base_quantity, market):
        price = float(self.call.get_latest_price(market))
        df = self.t_markets_df[self.t_markets_df['symbol'] == market]
        step = df['step'].values[0]
        quantity_to_be_bought = base_quantity/price
        quantity_to_be_bought = step * np.floor(quantity_to_be_bought / step)
        while not self.validate_quantity(base_quantity, quantity_to_be_bought, price):
            quantity_to_be_bought = quantity_to_be_bought-step
        if quantity_to_be_bought < 0:
            raise Exception('quantity is negative for market = '+market)
        return float(price), quantity_to_be_bought

    def validate_quantity(self, base_quantity, quantity_to_be_bought, price):
        actual_base_quantity = quantity_to_be_bought * price
        actual_base_quantity_required = actual_base_quantity + (actual_base_quantity * 0.001)
        if actual_base_quantity_required >= base_quantity:
            return False
        else:
            return True

    def place_orders(self):
        prev_order = None
        for key in self.market_pair_dict:
            if key == self.sell_market_symbol:
                side = 'sell'
            else:
                side = 'buy'

            create = True
            order_id = None
            while True:
                if create:
                    order_id = self.o.place_order(side, self.market_pair_dict[key], key, self.market_quantity_dict[key], prev_order)
                    create=False
                sleep(1)
                status = self.get_order_status(order_id)
                if 'rejected' == status:
                    create = True
                    continue
                if 'filled' == status:
                    prev_order = order_id
                    break
        pass

    def get_order_status(self, order_id):
        if order_id is None:
            return 'rejected'
        df = self.call.get_order_status(order_id)
        status = df['status'].values[0]
        return status
