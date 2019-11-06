
interval_sampling=1.0
length_sampling=10

import os
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from publicAPI import CCPublic as CCPublic
from privateAPI import CCPrivate as CCPrivate

ccpublic = CCPublic()

path_key = 'C:/Users/atiro/Documents/tsa'
access_key = open(os.path.join(path_key,'access_key.txt')).read()
secret_key = open(os.path.join(path_key,'secret_key.txt')).read()
ccprivate = CCPrivate(access_key, secret_key)

# Request ticker
ticker=ccpublic.f_ticker()

# Request rate
rate=ccpublic.f_rate()

# Timer
df_rate=pd.DataFrame(columns=['time','rate'])
starttime=int(np.ceil(time.time()))
while True:
  time.sleep(interval_sampling - ((time.time() - starttime) % interval_sampling))
  timestamp=int(time.time())
  if time.time()-starttime>length_sampling:
    break
  rate=float(ccpublic.f_rate()['rate'])
  #ticker=ccpublic.f_ticker()
  print(str(timestamp)+' '+str(rate))
  #print(ticker)
  df_rate.loc[len(df_rate)+1,:]=np.array([timestamp,rate])
  #time.sleep(1.0 - ((time.time() - starttime) % 1.0))

p=df_rate.plot(x='time',y='rate')
plt.show()


# Order sell
path_orders = '/api/exchange/orders'
params = {
    "pair": "btc_jpy",
    "order_type": "sell",
    "rate": 1000000,
    "amount": 0.01,
}
result = ccprivate.post(path_orders, params)
print(result)

# Order buy

# List orders
path_orders_opens = '/api/exchange/orders/opens'
result = ccprivate.get(path_orders_opens)
print(result)

# Cancel orders
path_orders_cancel = '/api/exchange/orders/2027429119'
result = ccprivate.delete(path_orders_cancel)
print(result)