
interval_sampling=1.0
length_sampling=1200

range_save=1000
int_save=10

import os
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from publicAPI import CCPublic as CCPublic
from privateAPI import CCPrivate as CCPrivate
from acquire import Acquire as Acquire
from prepare import Prepare as Prepare
from analyze import Analyze as Analyze

prepare=Prepare(path_src='C:/Users/NICT_WS/Dropbox/tsa/20191107_161734')

(x_train,y_train),(x_test,y_test)=prepare.dataset_band(n_sequence=60,n_resample=1,
                                                       calc_diff=True,scale='standard')

(x_train,y_train),(x_test,y_test)=prepare.dataset_rate(n_sequence=60,n_resample=1,
                                                       calc_diff=True,scale='standard')

analyze=Analyze()
analyze.prep_model(n_sequence=60)
analyze.fit_model(x_train,y_train,n_epoch=100,n_patience=10)
analyze.predict(x_test,y_test)
analyze.predict(x_train,y_train)

prepare=Prepare()
prepare.order2band()

acquire=Acquire()
acquire.record_order()

## Private API

path_key = 'C:/Users/atiro/Documents/tsa'
access_key = open(os.path.join(path_key,'access_key.txt')).read()
secret_key = open(os.path.join(path_key,'secret_key.txt')).read()
ccprivate = CCPrivate(access_key, secret_key)

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