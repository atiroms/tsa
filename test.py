path_github='D:/atiroms/GitHub/tsa'

import os
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
os.chdir(path_github)
from publicAPI import CCPublic as CCPublic
from privateAPI import CCPrivate as CCPrivate
from acquire import Acquire as Acquire
from prepare import Prepare as Prepare
from analyze import Analyze as Analyze

#path_src='C:/Users/NICT_WS/Dropbox/tsa/20191107_161734'
#path_src='C:/Users/atiro/Dropbox/tsa/20191107_161734'
path_src='D:/atiroms/Dropbox/tsa/20191110_120804'

prepare=Prepare(path_src=path_src)
array_rate=prepare.read_rate()
analyze=Analyze()
array_range=analyze.predict_range(array_rate,100)
#array_rp=analyze.moving_average_multi(array_rate)
#array_average,r_cor,p_cor=analyze.moving_average(array_rate)

######
interval_sampling=1.0
length_sampling=1200

range_save=1000
int_save=10

#(x_train,y_train),(x_test,y_test)=prepare.dataset_band(n_sequence=6,n_resample=10,range_rate=1000,
#                                                       calc_diff=True,scale='standard')
(x_train,y_train),(x_test,y_test)=prepare.dataset_rate(n_sequence=60,n_resample=1,
                                                       calc_diff=True,scale='standard',threshold=0.5)

analyze=Analyze()
analyze.prep_model(x_train,y_train)
analyze.fit_model(x_train,y_train,n_epoch=100,n_patience=10)
a=analyze.predict(x_test,y_test)
#analyze.predict(x_train,y_train)


fig=plt.figure()
ax=fig.add_subplot(1,1,1)
ax.plot(np.arange(100),a[:100,0])
ax.plot(np.arange(100),y_test[:100])
plt.show()

prepare=Prepare()
prepare.order2band()

acquire=Acquire()
acquire.record_order()

## Private API

#path_key = 'C:/Users/atiro/Documents/tsa'
path_key = 'D:/atiroms/Documents/tsa'
access_key = open(os.path.join(path_key,'access_key.txt')).read()
secret_key = open(os.path.join(path_key,'secret_key.txt')).read()
ccprivate = CCPrivate(access_key, secret_key)

# Order sell
path_orders = '/api/exchange/orders'
params = {
    "pair": "btc_jpy",
    "order_type": "sell",
    "rate": 1000000,
    "amount": 0.005,
}
result = ccprivate.post(path_orders, params)
print(result)

# Order buy
path_orders = '/api/exchange/orders'
params = {
    "pair": "btc_jpy",
    "order_type": "buy",
    "rate": 800000,
    "amount": 0.005,
}
result = ccprivate.post(path_orders, params)
print(result)

# List orders
path_orders_opens = '/api/exchange/orders/opens'
result = ccprivate.get(path_orders_opens)
print(result)

# Cancel orders
path_orders_cancel = '/api/exchange/orders/2027429119'
result = ccprivate.delete(path_orders_cancel)
print(result)