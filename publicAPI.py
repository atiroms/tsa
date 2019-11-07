import requests
import json

class CCPublic:
    def __init__(self):
        return None

    def f_ticker(self):
        url = 'https://coincheck.com/api/ticker'
        try:
            self.ticker = requests.get(url).json()
        except:
            self.ticker = False

        #for key, item in self.ticker.items():
        #    print("%-9s : %-10.9s " % (key, item))
        #print(self.ticker)
        return self.ticker

    def f_transaction(self,offset=100):
        url = 'https://coincheck.com/api/trades'
        self.transaction = requests.get(url,params={"offset": offset,"pair":"btc_jpy"}).json() 
        print(self.transaction)

    def f_order(self):
        url = 'https://coincheck.com/api/order_books'
        try:
            self.order = requests.get(url).json()
        except:
            self.order = False
        #for key in self.order.keys():
        #    print(key, ":")
        #    for value in self.order[key]:
        #        print(value)
        #    print()
        return(self.order)

    def f_rate(self,amount=1):
        url = 'https://coincheck.com/api/exchange/orders/rate'
        params = {'order_type': 'sell', 'pair': 'btc_jpy', 'amount': amount}
        self.rate = requests.get(url, params=params).json() 
        #print(self.rate)
        return self.rate
