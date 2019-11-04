import requests
import json
import time
import hmac
import hashlib


## Public API
# Ticker
URL = 'https://coincheck.com/api/ticker'
coincheck = requests.get(URL).json() 
for key, item in coincheck.items():
    print("%-9s : %-10.9s " % (key, item))

# All transactions
URL = 'https://coincheck.com/api/trades'
coincheck = requests.get(URL, params={"offset": 1}).json() 
print(coincheck)

# All orders
URL = 'https://coincheck.com/api/order_books'
coincheck = requests.get(URL).json() 
for key in coincheck.keys():
    print(key, ":")
    for value in coincheck[key]:
        print(value)
    print()

# Rate
URL = 'https://coincheck.com/api/exchange/orders/rate'
params = {'order_type': 'sell', 'pair': 'btc_jpy', 'amount': 0.1}
coincheck = requests.get(URL, params=params).json() 
print(coincheck)

params = {'order_type': 'buy', 'pair': 'btc_jpy', 'price': 280000}
coincheck = requests.get(URL, params=params).json() 
print(coincheck)


## Private API
