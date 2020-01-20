import numpy as np
from tensorflow.keras import models as kmodels
from tensorflow.keras import layers as klayers
from tensorflow.keras import optimizers as koptimizers
from tensorflow.keras import callbacks as kcallbacks
from scipy.stats.stats import pearsonr
import matplotlib.pyplot as plt

class Analyze():
    def __init__(self):
        return None
    
    def moving_average(self,array_rate,range_average=60):
        print('Calculating moving average over ',str(range_average),' points.')
        # arry_rate is in N x 2 shape (Columns: timepoint, rate)
        array_average=np.zeros([np.shape(array_rate)[0],3])
        array_average[:,:]=np.nan
        for time in range(1,np.shape(array_rate)[0]):
            array_average[time,0]=array_rate[time,1]-array_rate[time-1,1]
        for time in range(range_average-1,np.shape(array_rate)[0]):
            array_average[time,1]=np.average(array_rate[(time-range_average+1):time+1,1])
            array_average[time,2]=array_rate[time,1]-array_average[time,1]
        array_average=np.concatenate([array_rate,array_average],axis=1)

        # 0:timepoint, 1:rate, 2:rate change, 
        # 3:rate moving average 4:divergence from moving average
        cor_coef=pearsonr(array_average[range_average+1:,2],array_average[range_average:-1,4])
        print("R: ",cor_coef[0],", p: ",cor_coef[1])
        
        #fig=plt.figure()
        #ax=fig.add_subplot(1,1,1)
        #ax.plot(array_average[:,0],array_average[:,1])
        #ax.plot(array_average[:,0],array_average[:,3])
        #plt.show()

        fig=plt.figure()
        ax=fig.add_subplot(1,1,1)
        ax.scatter(array_average[:-1,4],array_average[1:,2])
        plt.show()
        return array_average,cor_coef[0],cor_coef[1]

    def moving_average_multi(self,array_rate,start=2,ratio=2,n_step=10):
        array_rp=np.zeros([n_step,3])
        for i_step in range(n_step):
            range_average=start*(ratio**i_step)
            _,r_cor,p_cor=self.moving_average(array_rate,range_average=range_average)
            array_rp[i_step,:]=[range_average,r_cor,p_cor]

        fig=plt.figure()
        ax=fig.add_subplot(1,1,1)
        ax.plot(array_rp[:,0],array_rp[:,1])
        plt.show()
        return(array_rp)


    def prep_model(self,x_train,y_train,n_hidden=300,n_out=1):
        print('Preparing LSTM model.')
        # x_train is in 3D [samples, timesteps, features]
        # y_train is in 1D [samples]
        n_sequence=x_train.shape[1]
        n_in=x_train.shape[2]
        n_out=1
        model = kmodels.Sequential()  
        model.add(klayers.LSTM(n_hidden, batch_input_shape=(None, n_sequence, n_in), return_sequences=False))  
        model.add(klayers.Dense(n_out))  
        model.add(klayers.Activation("linear"))  
        optimizer = koptimizers.Adam(lr=1e-3)
        model.compile(loss="mean_squared_error", optimizer=optimizer)
        model.summary()
        self.model=model
        return True

    def fit_model(self,x_train,y_train,n_batch=600,n_epoch=15,r_validation=0.2,n_patience=2,stop_early=True):
        print('Fitting model.')
        # x_train is in 3D [samples, timesteps, features]
        # y_train is in 1D [samples]
        if stop_early:
            early_stopping = kcallbacks.EarlyStopping(monitor='val_loss', patience=n_patience)
            self.model.fit(x_train, y_train, batch_size=n_batch, epochs=n_epoch, validation_split=r_validation, callbacks=[early_stopping]) 
        else:
            self.model.fit(x_train, y_train, batch_size=n_batch, epochs=n_epoch, validation_split=r_validation) 
        return True

    def predict(self,x_test,y_test):
        print('Predicting using model.')
        # x_test is in 3D [samples, timesteps, features]
        # y_test is in 1D [samples]
        y_predict=self.model.predict(x_test)
        fig=plt.figure()
        ax=fig.add_subplot(1,1,1)
        ax.plot(np.arange(0,x_test.shape[0],1),y_predict)
        ax.plot(np.arange(0,x_test.shape[0],1),y_test)
        plt.show()
        return y_predict