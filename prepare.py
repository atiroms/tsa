
import os
import numpy as np
import sklearn.preprocessing as skprep
import matplotlib.pyplot as plt

class Prepare:
    def __init__(self,path_src='C:/Users/atiro/Dropbox/tsa/20191107_161734'):
        self.path_src=path_src

    def dataset_rate(self,n_sequence=120,r_test=0.1):
        print('Preparing rate dataset.')
        array_rate=self.read_rate()
        scaler = skprep.MinMaxScaler(feature_range=(0, 1))
        array_rate = scaler.fit_transform(array_rate)
        array_x=np.ndarray([0,n_sequence])
        array_y=np.ndarray([0])
        for i in range(array_rate.shape[0]-n_sequence):
            array_x=np.append(array_x,array_rate[i:i+n_sequence,1].reshape(1,n_sequence),axis=0)
            array_y=np.append(array_y,array_rate[i+n_sequence,1].reshape(1),axis=0)

        n_train=int(round(array_y.shape[0]*(1-r_test)))
        x_train=array_x[0:n_train,:]
        y_train=array_y[0:n_train]
        x_test=array_x[n_train:,:]
        y_test=array_y[n_train:]
        
        return (x_train,y_train),(x_test,y_test)

    def read_rate(self):
        list_file=os.listdir(self.path_src)
        list_time_file=list(set([f[:15] for f in list_file]))
        list_time_file.sort()
        array_rate_long=np.ndarray([0,2])
        for time_file in list_time_file:
            array_rate=np.load(os.path.join(self.path_src,time_file+'_rate.npy'))
            array_rate_long=np.append(array_rate_long,array_rate,axis=0)

        fig=plt.figure()
        ax=fig.add_subplot(1,1,1)
        ax.plot(array_rate_long[:,0],array_rate_long[:,1])
        plt.show()
        return array_rate_long


    def order2band(self,range_rate=1000,int_rate=10):
        list_file=os.listdir(self.path_src)
        list_time_file=list(set([f[:15] for f in list_file]))
        list_time_file.sort()
        for time_file in list_time_file:
            if os.path.exists(os.path.join(self.path_src,time_file+'_band.npy')):
                print(time_file+' already processed.')
            else:
                array_rate=np.load(os.path.join(self.path_src,time_file+'_rate.npy'))
                array_asks=np.load(os.path.join(self.path_src,time_file+'_asks.npy'))
                array_bids=np.load(os.path.join(self.path_src,time_file+'_bids.npy'))

                n_time=np.shape(array_rate)[0]
                array_band=np.ndarray([n_time,2*range_rate])

                for idx_time in range(n_time):
                    rate=array_rate[idx_time,1]
                    accum_amount=0.0
                    current_step_rate=0
                    for idx_order in range(np.shape(array_asks)[1]):
                        diff_rate=array_asks[idx_time,idx_order,0]-rate
                        reached_step_rate=int(diff_rate/int_rate)
                        if reached_step_rate>range_rate:
                            reached_step_rate=range_rate
                            array_band[idx_time,(range_rate+current_step_rate):(range_rate+reached_step_rate)]=accum_amount
                            break
                        else:
                            array_band[idx_time,(range_rate+current_step_rate):(range_rate+reached_step_rate)]=accum_amount
                            current_step_rate=reached_step_rate
                            accum_amount=accum_amount+array_asks[idx_time,idx_order,1]

                    accum_amount=0.0
                    current_step_rate=0
                    for idx_order in range(np.shape(array_bids)[1]):
                        diff_rate=rate-array_bids[idx_time,idx_order,0]
                        reached_step_rate=int(diff_rate/int_rate)
                        if reached_step_rate>range_rate:
                            reached_step_rate=range_rate
                            array_band[idx_time,(range_rate-reached_step_rate):(range_rate-current_step_rate)]=-accum_amount
                            break
                        else:
                            array_band[idx_time,(range_rate-reached_step_rate):(range_rate-current_step_rate)]=-accum_amount
                            current_step_rate=reached_step_rate
                            accum_amount=accum_amount+array_bids[idx_time,idx_order,1]

                np.save(os.path.join(self.path_src,time_file+'_band.npy'),array_band)
                print(time_file+' processed and saved.')

        print('Combining processed results.')
        array_band_long=np.ndarray([0,2*range_rate])
        for time_file in list_time_file:
            array_band=np.load(os.path.join(self.path_src,time_file+'_band.npy'))
            array_band_long=np.append(array_band_long,array_band,axis=0)

        print('Preparing figure.')
        fig=plt.figure()
        ax=fig.add_subplot(1,1,1)
        ax.pcolor(array_band_long,cmap='jet')
        plt.show()
        print('Finished order2band()')
        return array_band_long
