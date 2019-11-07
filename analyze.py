
import os
import numpy as np

class Analyze:
    def __init__(self,path_src='C:/Users/atiro/Dropbox/tsa/20191107_161734'):
        self.path_src=path_src

    def order2carpet(self,range_rate=1000,int_rate=10):

        
        array_order=np.ndarray([4,2*range_rate])
        array_order[0,:]=np.arange(-range_rate*int_rate,range_rate*int_rate,int_rate)
        for i in range(range_rate):
            if df_bids.loc[0,'rate']>rate-(range_rate-i)*int_rate:
                id_max=max(df_bids.index[df_bids['rate']>rate-(range_rate-i)*int_rate])
                array_order[1,i]=-df_bids.loc[id_max,'accumulate']
            else:
                array_order[1,i]=0

            if df_asks.loc[0,'rate']<rate+(range_rate-i-1)*int_rate:
                id_max=max(df_asks.index[df_asks['rate']<rate+(range_rate-i-1)*int_rate])
                array_order[1,2*range_rate-i-1]=df_asks.loc[id_max,'accumulate']
            else:
                array_order[1,2*range_rate-i-1]=0

        fit_order=np.polyfit(array_order[0],array_order[1],1)
        array_order[2,:]=array_order[1,:]-array_order[0,:]*fit_order[0]
        sigma=np.std(array_order[2,:])
        array_order[3,:]=array_order[2,:]/sigma

        array_order_history=np.append(array_order_history,np.reshape(array_order[3,:],(1,range_rate*2)),axis=0)