import numpy as np
from datetime import datetime
from order import order
from time import sleep

class arbitrage:

    def __init__(self, master):
        self.l = master.l
        self.m = master
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
        self.market_price_dict = {}
        self.sell_market_symbol = None



    def find(self, set_paths):
        for ls in set_paths:
            base_currency = ls[0]
            base_quantity = self.initial_quantity[base_currency]
            if base_quantity == 0:
                continue
            ls_pairs = []
            ls_quantity = []
            for index, elem in enumerate(ls):
                if (index+1 < len(ls) and index - 1 >= 0):
                    prev_el = str(ls[index - 1])
                    curr_el = str(elem)
                    market = curr_el + prev_el
                    ls_pairs.append(market)
                    this_df = self.t_markets_df.loc[self.t_markets_df['coindcx_name'] == market]
                    self.market_pair_dict[market] = this_df['pair'].values[0]
                if index + 1 >= len(ls):
                    curr = elem
                    prev = ls[index -1]
                    next = ls[0]
                    market = curr + prev
                    ls_pairs.append(market)
                    this_df = self.t_markets_df.loc[self.t_markets_df['coindcx_name'] == market]
                    self.market_pair_dict[market] = this_df['pair'].values[0]
                    market = curr + next
                    ls_pairs.append(market)
                    this_df = self.t_markets_df.loc[self.t_markets_df['coindcx_name'] == market]
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
                    price = float(self.call.get_current_price(pair))
                    qty = ls_quantity[-1] * price
                    final_quantity = qty - 0.001 * qty
                    self.sell_market_symbol = pair
                    self.market_price_dict[pair] = price
                    self.market_quantity_dict[pair] = self.market_quantity_dict[ls_pairs[-2]]
                else:
                    p, q = self.get_quantity(base_quantity, pair)
                    ls_quantity.append(q)
                    self.market_quantity_dict[pair] = q
                    initial_price = p
            initial_quantity = float(ls_quantity[0]) * initial_price
            initial_quantity = initial_quantity + 0.001 * initial_quantity
            if final_quantity > initial_quantity:
                assumed_percent = ((final_quantity - initial_quantity) / initial_quantity) * 100
                percentage = ((ls_total_price[-1] - ls_total_price[0])/ ls_total_price[0]) * 100
                print('Arbitrage found for '+str(ls))
                print('Arbitrage assumed percent = '+str(assumed_percent))
                print('Arbitrage actual percent = ' + str(percentage))
                accumulated_quantity = self.accumulation[base_currency]
                self.accumulation[base_currency] = accumulated_quantity + (final_quantity - initial_quantity)
            else:
                self.market_pair_dict.clear()
                self.market_quantity_dict.clear()
                self.market_price_dict.clear()
                self.sell_market_symbol = None

    def get_quantity(self, base_quantity, market):
        price = float(self.call.get_current_price(market))
        self.market_price_dict[market] = price
        df = self.t_markets_df[self.t_markets_df['symbol'] == market]
        step = df['step'].values[0]
        quantity_to_be_bought = base_quantity/price
        quantity_to_be_bought = step * np.floor(quantity_to_be_bought / step)
        while not self.validate_quantity(base_quantity, quantity_to_be_bought, price):
            quantity_to_be_bought = quantity_to_be_bought-step
        if quantity_to_be_bought < 0:
            raise Exception('quantity is negative for market = '+market)
        target_currency_precision = df['target_currency_precision'].values[0]
        return float(price), round(quantity_to_be_bought, target_currency_precision)

    def validate_quantity(self, base_quantity, quantity_to_be_bought, price):
        actual_base_quantity = quantity_to_be_bought * price
        actual_base_quantity_required = actual_base_quantity + (actual_base_quantity * 0.001)
        if actual_base_quantity_required >= base_quantity:
            return False
        else:
            return True
