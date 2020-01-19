import os
import time
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from publicAPI import CCPublic as CCPublic


class Acquire:
    def __init__(self):
        self.ccpublic = CCPublic()

    def record_order(self,interval_sample=10.0,length_sample=None,interval_save=360,path_save='D:/atiroms/Dropbox/tsa'):
        startdatetime="{0:%Y%m%d_%H%M%S}".format(datetime.datetime.now())
        os.mkdir(os.path.join(path_save,startdatetime))

        array_rate=np.ndarray([0,2],dtype='int64')
        array_asks=np.ndarray([0,200,2],dtype='float64')
        array_bids=np.ndarray([0,200,2],dtype='float64')

        starttime=int(np.ceil(time.time()))
        savetime=int(np.ceil(time.time()))
        while True:
            time.sleep(interval_sample - ((time.time() - starttime) % interval_sample))
            timestamp=int(time.time())
            if length_sample!=None:
                if time.time()-starttime>length_sample:
                    break
            print(str(timestamp-starttime))

            if time.time()-savetime+1 > interval_sample*interval_save:
                savetime=int(np.ceil(time.time()))

                datetimestamp="{0:%Y%m%d_%H%M%S}".format(datetime.datetime.now())
                np.save(os.path.join(path_save,startdatetime,datetimestamp+'_rate.npy'),array_rate)
                np.save(os.path.join(path_save,startdatetime,datetimestamp+'_asks.npy'),array_asks)
                np.save(os.path.join(path_save,startdatetime,datetimestamp+'_bids.npy'),array_bids)
                print('Saved '+datetimestamp+'.')

                array_rate=np.ndarray([0,2],dtype='int64')
                array_asks=np.ndarray([0,200,2],dtype='float64')
                array_bids=np.ndarray([0,200,2],dtype='float64')

            rate = self.acquire_rate()
            array_asks_add, array_bids_add = self.acquire_order()

            if rate!=False and np.size(array_asks_add)>1:
                array_rate=np.append(array_rate,np.reshape(np.array([timestamp,rate]),(1,2)),axis=0)
                array_asks=np.append(array_asks,np.reshape(array_asks_add,(1,-1,2)),axis=0)
                array_bids=np.append(array_bids,np.reshape(array_bids_add,(1,-1,2)),axis=0)

        return True
    
    def acquire_rate(self):
        ticker= self.ccpublic.f_ticker()
        if ticker==False:
            print('Ticker access error.')
            return False
        else:
            return int(ticker['last'])

    def acquire_order(self):
        order=self.ccpublic.f_order()
        if order== False:
            print("Order access error.")
            return False, False
        else:
            array_asks_add=np.ndarray([0,2],dtype='float64')
            for value in order['asks']:
                array_asks_add=np.append(array_asks_add,np.array([value[0],value[1]],dtype='float64').reshape(1,2),axis=0)

            array_bids_add=np.ndarray([0,2],dtype='float64')
            for value in order['bids']:
                array_bids_add=np.append(array_bids_add,np.array([value[0],value[1]],dtype='float64').reshape(1,2),axis=0)
            
            return array_asks_add,array_bids_add