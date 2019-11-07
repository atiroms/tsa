
import os
import numpy as np
import matplotlib.pyplot as plt

class Analyze:
    def __init__(self,path_src='C:/Users/atiro/Dropbox/tsa/20191107_161734'):
        self.path_src=path_src

    def order2carpet(self,range_rate=1000,int_rate=10):
        list_file=os.listdir(self.path_src)
        list_time_file=list(set([f[:15] for f in list_file]))
        list_time_file.sort()
        for time_file in list_time_file:
            array_rate=np.load(os.path.join(self.path_src,time_file+'_rate.npy'))
            array_asks=np.load(os.path.join(self.path_src,time_file+'_asks.npy'))
            array_bids=np.load(os.path.join(self.path_src,time_file+'_bids.npy'))

            n_time=np.shape(array_rate)[0]
            array_order=np.ndarray([n_time,2*range_rate])

            for idx_time in range(n_time):
                rate=array_rate[idx_time,1]
                accum_amount=0.0
                current_step_rate=0
                for idx_order in range(np.shape(array_asks)[1]):
                    diff_rate=array_asks[idx_time,idx_order,0]-rate
                    reached_step_rate=int(diff_rate/int_rate)
                    if reached_step_rate>range_rate:
                        reached_step_rate=range_rate
                        array_order[idx_time,(range_rate+current_step_rate):(range_rate+reached_step_rate)]=accum_amount
                        #break
                    else:
                        array_order[idx_time,(range_rate+current_step_rate):(range_rate+reached_step_rate)]=accum_amount
                        current_step_rate=reached_step_rate
                        accum_amount=accum_amount+array_asks[idx_time,idx_order,1]

                accum_amount=0.0
                current_step_rate=0
                for idx_order in range(np.shape(array_bids)[1]):
                    diff_rate=rate-array_bids[idx_time,idx_order,0]
                    reached_step_rate=int(diff_rate/int_rate)
                    if reached_step_rate>range_rate:
                        reached_step_rate=range_rate
                        array_order[idx_time,(range_rate-reached_step_rate):(range_rate-current_step_rate)]=-accum_amount
                        #break
                    else:
                        array_order[idx_time,(range_rate-reached_step_rate):(range_rate-current_step_rate)]=-accum_amount
                        current_step_rate=reached_step_rate
                        accum_amount=accum_amount+array_bids[idx_time,idx_order,1]
                        os.path.join(self.path_src, time_file+'_order.npy')

            np.save(os.path.join(self.path_src,time_file+'_order.npy'),array_order)

        fig, ax = plt.subplots()
        heatmap = ax.pcolor(array_order)

        plt.show()
