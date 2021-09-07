import numpy as np
from datetime import datetime

class arbitrage:

    def __init__(self, master):
        self.l = master.l
        self.m = master
        self.markets_df = master.markets_df
        self.t_markets_df = master.t_markets_df
        self.call = master.call
        self.slack = master.slack
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



    def find(self, set_paths):
        #df = self.call.get_ticker()
        for ls in set_paths:
            base_currency = ls[0]
            base_quantity = self.initial_quantity[base_currency]
            if base_quantity == 0:
                continue
            ls_pairs = []
            ls_price = []
            ls_quantity = []
            for index, elem in enumerate(ls):
                if (index+1 < len(ls) and index - 1 >= 0):
                    prev_el = str(ls[index - 1])
                    curr_el = str(elem)
                    market = curr_el + prev_el
                    #new_df = df.loc[df['market'] == market]
                    #price = new_df['last_price'].values[0]
                    #ls_price.append(price)
                    ls_pairs.append(market)
                if index + 1 >= len(ls):
                    curr = elem
                    prev = ls[index -1]
                    next = ls[0]
                    market = curr + prev
                    #new_df = df.loc[df['market'] == market]
                    #price = new_df['last_price'].values[0]
                    #ls_price.append(price)
                    ls_pairs.append(market)
                    market = curr + next
                    #new_df = df.loc[df['market'] == market]
                    #price = new_df['last_price'].values[0]
                    #ls_price.append(price)
                    ls_pairs.append(market)
            #print(ls_pairs)
            #print(ls_price)

            final_quantity= 0
            initial_price = 0
            #current_cycle_start = datetime.now()
            for index, pair in enumerate(ls_pairs):
                if (index + 1 < len(ls) and index - 1 >= 0):
                    p, q = self.get_quantity(ls_quantity[index-1], pair)
                    ls_quantity.append(q)
                    continue
                if index + 1 >= len(ls):
                    qty = ls_quantity[-1] * float(self.call.get_latest_price(pair))
                    final_quantity = qty - 0.001 * qty
                else:
                    p, q = self.get_quantity(base_quantity, pair)
                    ls_quantity.append(q)
                    initial_price = p
            '''
            current_cycle_end = datetime.now() - current_cycle_start
            self.l.log_info('current inner cycle completion took -> %s' % current_cycle_end)
            print('current inner cycle completion took -> %s' % current_cycle_end)
            '''
            #print(ls_quantity)
            initial_quantity = float(ls_quantity[0]) * initial_price
            initial_quantity = initial_quantity + 0.001 * initial_quantity
            if final_quantity > initial_quantity:
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

