import requests
import json

class CCPublic:
    def __init__(self):
        return None

    def ccticker(self):
        url = 'https://coincheck.com/api/ticker'
        self.ticker = requests.get(url).json() 
        for key, item in self.ticker.items():
            print("%-9s : %-10.9s " % (key, item))
    
    def cctransaction(self,offset=100):
        url = 'https://coincheck.com/api/trades'
        self.transaction = requests.get(url,params={"offset": offset,"pair":"btc_jpy"}).json() 
        print(self.transaction)

    def ccorder(self):
        url = 'https://coincheck.com/api/order_books'
        self.order = requests.get(url).json() 
        for key in self.order.keys():
            print(key, ":")
            for value in self.order[key]:
                print(value)
            print()

    def ccrate(self):
        url = 'https://coincheck.com/api/exchange/orders/rate'
        params = {'order_type': 'sell', 'pair': 'btc_jpy', 'amount': 1}
        self.rate = requests.get(url, params=params).json() 
        print(self.rate)
