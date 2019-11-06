import os
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from publicAPI import CCPublic as CCPublic

ccpublic = CCPublic()

class Acquire:
    def __init__(self):
        self.ccpublic = CCPublic()

    def acquire_order(self,interval_sampling=1.0,length_sampling=10):
        array_asks=np.ndarray([0,200,2],dtype='float64')
        array_bids=np.ndarray([0,200,2],dtype='float64')
        array_rate=np.ndarray([0,2],dtype='int64')
        starttime=int(np.ceil(time.time()))
        while True:
            time.sleep(interval_sampling - ((time.time() - starttime) % interval_sampling))
            timestamp=int(time.time())
            if time.time()-starttime>length_sampling:
                break
            print(str(timestamp-starttime))

            rate=self.acquire_rate()
            array_rate=np.append(array_rate,np.reshape(np.array([timestamp,rate]),(1,2)),axis=0)
            order=self.ccpublic.f_order()

            array_add=np.ndarray([0,2],dtype='float64')
            for value in order['asks']:
                array_add=np.append(array_add,np.array([value[0],value[1]],dtype='float64').reshape(1,2),axis=0)
            array_asks=np.append(array_asks,np.reshape(array_add,(1,-1,2)),axis=0)

            array_add=np.ndarray([0,2],dtype='float64')
            for value in order['bids']:
                array_add=np.append(array_add,np.array([value[0],value[1]],dtype='float64').reshape(1,2),axis=0)
            array_bids=np.append(array_asks,np.reshape(array_add,(1,-1,2)),axis=0)

        return array_rate, array_asks, array_bids
    
    def acquire_rate(self):
        return int(self.ccpublic.f_ticker()['last'])

