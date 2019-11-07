
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

acquire=Acquire()
acquire.record_order()

range_rate=1000
int_rate=10

path_src='C:/Users/atiro/Dropbox/tsa/20191107_161734'
list_file=os.listdir(path_src)
list_time_file=list(set([f[:15] for f in list_file]))
list_time_file.sort()
for time_file in list_time_file:
	array_rate=np.load(os.path.join(path_src,time_file+'_rate.npy'))
	array_asks=np.load(os.path.join(path_src,time_file+'_asks.npy'))
	array_bids=np.load(os.path.join(path_src,time_file+'_bids.npy'))

	n_time=np.shape(array_rate)[0]
	array_order=np.ndarray([n_time,3,2*range_rate])

	for idx_time in range(n_time):
		rate=array_rate[idx_time,1]
		accum_amount=0.0
		current_step_rate=0
		for idx_order in range(np.shape(array_asks)[1]):
			diff_rate=array_asks[idx_time,idx_order,0]-rate
			reached_step_rate=int(diff_rate/int_rate)
			if reached_step_rate>range_rate:
				reached_step_rate=range_rate
				array_order[idx_time,0,(range_rate+current_step_rate):(range_rate+reached_step_rate)]=accum_amount
				break
			else:
				array_order[idx_time,0,(range_rate+current_step_rate):(range_rate+reached_step_rate)]=accum_amount
				current_step_rate=reached_step_rate
				accum_amount=accum_amount+array_asks[idx_time,idx_order,1]
				
		accum_amount=0.0
		current_step_rate=0
		for idx_order in range(np.shape(array_bids)[1]):
			diff_rate=rate-array_bids[idx_time,idx_order,0]
			reached_step_rate=int(diff_rate/int_rate)
			if reached_step_rate>range_rate:
				reached_step_rate=range_rate
				array_order[idx_time,0,(range_rate-reached_step_rate):(range_rate-current_step_rate)]=-accum_amount
				break
			else:
				array_order[idx_time,0,(range_rate-reached_step_rate):(range_rate-current_step_rate)]=-accum_amount
				current_step_rate=reached_step_rate
				accum_amount=accum_amount+array_asks[idx_time,idx_order,1]

fig, ax = plt.subplots()
heatmap = ax.pcolor(array_order[:,0,:])
#plt.plot(array_order[0],array_order[3])

plt.show()


ccpublic = CCPublic()

# Request order with intervals
array_order_history=np.ndarray([0,2*range_save])
array_rate=np.ndarray([0,2])
starttime=int(np.ceil(time.time()))
while True:
  time.sleep(interval_sampling - ((time.time() - starttime) % interval_sampling))
  timestamp=int(time.time())
  if time.time()-starttime>length_sampling:
    break
  print(str(timestamp-starttime))

  rate=int(ccpublic.f_ticker()['last'])
  array_rate=np.append(array_rate,np.reshape(np.array([timestamp,rate]),(1,2)),axis=0)
  order=ccpublic.f_order()
  df_asks=pd.DataFrame(columns=['rate','amount','accumulate'])
  df_bids=pd.DataFrame(columns=['rate','amount','accumulate'])
  for value in order['asks']:
    if len(df_asks)>0:
      add=[int(float(value[0])),float(value[1]),df_asks.loc[len(df_asks)-1,'accumulate']+float(value[1])]
    else:
      add=[int(float(value[0])),float(value[1]),+float(value[1])]
    df_asks.loc[len(df_asks),:]=add

  for value in order['bids']:
    if len(df_bids)>0:
      add=[int(float(value[0])),float(value[1]),df_bids.loc[len(df_bids)-1,'accumulate']+float(value[1])]
    else:
      add=[int(float(value[0])),float(value[1]),+float(value[1])]
    df_bids.loc[len(df_bids),:]=add

  array_order=np.ndarray([4,2*range_save])
  array_order[0,:]=np.arange(-range_save*int_save,range_save*int_save,int_save)
  for i in range(range_save):
    if df_bids.loc[0,'rate']>rate-(range_save-i)*int_save:
      id_max=max(df_bids.index[df_bids['rate']>rate-(range_save-i)*int_save])
      array_order[1,i]=-df_bids.loc[id_max,'accumulate']
    else:
      array_order[1,i]=0

    if df_asks.loc[0,'rate']<rate+(range_save-i-1)*int_save:
      id_max=max(df_asks.index[df_asks['rate']<rate+(range_save-i-1)*int_save])
      array_order[1,2*range_save-i-1]=df_asks.loc[id_max,'accumulate']
    else:
      array_order[1,2*range_save-i-1]=0

  fit_order=np.polyfit(array_order[0],array_order[1],1)
  array_order[2,:]=array_order[1,:]-array_order[0,:]*fit_order[0]
  sigma=np.std(array_order[2,:])
  array_order[3,:]=array_order[2,:]/sigma

  array_order_history=np.append(array_order_history,np.reshape(array_order[3,:],(1,range_save*2)),axis=0)

fig, ax = plt.subplots()
heatmap = ax.pcolor(array_order_history)
#plt.plot(array_order[0],array_order[3])

plt.show()

try:
  requests.get('https://coincheck.com/api/ticke').json()
except:
  print("error")

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