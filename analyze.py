import numpy as np
from tensorflow.keras import models as kmodels
from tensorflow.keras import layers as klayers
from tensorflow.keras import optimizers as koptimizers
from tensorflow.keras import callbacks as kcallbacks

import matplotlib.pyplot as plt

class Analyze():
    def __init__(self):
        return None
    
    def prep_model(self,n_sequence=120,n_in=1,n_hidden=300,n_out=1):
        print('Preparing LSTM model.')
        model = kmodels.Sequential()  
        model.add(klayers.LSTM(n_hidden, batch_input_shape=(None, n_sequence, n_in), return_sequences=False))  
        model.add(klayers.Dense(n_out))  
        model.add(klayers.Activation("linear"))  
        optimizer = koptimizers.Adam(lr=1e-3)
        model.compile(loss="mean_squared_error", optimizer=optimizer)
        model.summary()
        self.model=model
        return True

    def fit_model(self,x_train,y_train,n_batch=600,n_epoch=15,r_validation=0.05):
        print('Fitting model.')
        # reshape input to be 3D [samples, timesteps, features]
        x_train=x_train.reshape(x_train.shape[0],x_train.shape[1],1)
        early_stopping = kcallbacks.EarlyStopping(monitor='val_loss', patience=2)
        self.model.fit(x_train, y_train, batch_size=n_batch, epochs=n_epoch, validation_split=r_validation, callbacks=[early_stopping]) 
        return True

    def predict(self,x_test,y_test):
        print('Predicting using model.')
        # reshape input to be 3D [samples, timesteps, features]
        x_test=x_test.reshape(x_test.shape[0],x_test.shape[1],1)
        y_predict=self.model.predict(x_test)
        fig=plt.figure()
        ax=fig.add_subplot(1,1,1)
        ax.plot(np.arange(0,x_test.shape[0],1),y_predict)
        ax.plot(np.arange(0,x_test.shape[0],1),y_test)
        plt.show()
        return y_predict