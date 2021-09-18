import os
import time


class order:

    def __init__(self, m):
        self.m = m
        self.l = m.l
        self._call = m.call
        self.markets_df = m.t_markets_df

    def store_order(self, pair, df, prev_order_id):
        substitution_dict = df.to_dict(orient='records')[0]
        substitution_dict['pair'] = pair
        s = pair.split("-")[1]
        substitution_dict['base_currency'] = s.split("_")[1]
        substitution_dict['target_currency'] = s.split("_")[0]
        substitution_dict['total_price'] = substitution_dict['price_per_unit'] * substitution_dict['total_quantity']
        substitution_dict['related'] = prev_order_id
        statement = '''
            insert into orders (
                order_id,
                pair,
                market,
                base_currency,
                target_currency,
                price,
                units,
                total_price,
                created_time,
                updated_time,
                side,
                order_type,
                status,
                related
            ) values (
                '%(id)s',
                '%(pair)s',
                '%(market)s',
                '%(base_currency)s',
                '%(target_currency)s',
                %(price_per_unit)s,
                %(total_quantity)s,
                %(total_price)s,
                %(created_at)s,
                %(updated_at)s,
                '%(side)s',
                '%(order_type)s',
                '%(status)s',
                '%(related)s'
            )
        ''' % substitution_dict
        self.m.execute_sql(statement.strip(), True)

    def _get_current_price(self, market):
        df = self._call.get_ticker()
        index = df[df['market'] == market].index
        return df['last_price'][index].values[0]

    def get_order_type(self, market):
        df = self.markets_df[self.markets_df['coindcx_name'] == market]
        sub_df = df['order_types']
        return sub_df.tolist()[0]

    def place_order(self, side, pair, market, quantity, current_price=None, prev_order_id=None):
        self.l.log_info(pair + " - " + str(quantity) + " - " + str(current_price))
        order_type = "limit_order"
        df = self._call.create_order(side, order_type, market, current_price, quantity)
        order_id = df['id'][0]
        self.l.log_debug("placed order " + order_id)
        self.store_order(pair, df, prev_order_id)

        return order_id

    def update_order_status(self, orderid):
        df = self._call.get_order_status(orderid)
        idx = df.index[0]
        status = df['status'][idx]
        order_id = df['id'][idx]
        created_at = df['created_at'][idx]
        current_time = int(round(time.time() * 1000))

        if 'open' == status or 'init' == status:
            self.l.log_warn("order " + order_id + " is still open")
            if current_time - created_at >= 300000:
                self.m.slack.post_message("order " + order_id + " is open for more than 5 minutes")

        if 'rejected' == status:
            self.l.log_warn("order " + order_id + " is rejected")
            statement = "delete from orders where order_id = '" + order_id + "'"
            self.m.execute_sql(statement.strip(), True)

        fee_amount = df['fee_amount'][idx]
        updated_at = df['updated_at'][idx]
        avg_price = df['avg_price'][idx]
        total_quantity = df['total_quantity'][idx]
        total_price = avg_price * total_quantity

        if 'filled' == status:
            final_price = total_price + fee_amount
            subs_dict = {
                "fee_amount": fee_amount,
                "updated_time": updated_at,
                "status": "'" + status + "'",
                "order_id": "'" + order_id + "'",
                "total_price": total_price,
                "price": avg_price,
                "final_price": final_price
            }
            statement = '''
                update orders
                set 
                fee_amount = %(fee_amount)s,
                updated_time = %(updated_time)s,
                status = %(status)s,
                final_price = %(final_price)s,
                price = %(price)s,
                total_price = %(total_price)s
                where order_id = %(order_id)s
            ''' % subs_dict
            self.m.execute_sql(statement.strip(), True)

            self.l.log_info("order " + order_id + " is filled")
        return total_price, total_quantity, status

    def get_open_orders(self):
        ls_ret = []
        statement = '''
            select order_id
            from orders
            where
            status = 'open'
        '''
        results = self.m.execute_sql(statement.strip())
        for result in results:
            ls_ret.append(result[0])
        return ls_ret
