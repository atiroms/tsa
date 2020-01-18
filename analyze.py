import numpy as np
from tensorflow.keras import models as kmodels
from tensorflow.keras import layers as klayers
from tensorflow.keras import optimizers as koptimizers
from tensorflow.keras import callbacks as kcallbacks

import matplotlib.pyplot as plt

class Analyze():
    def __init__(self):
        return None
    
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