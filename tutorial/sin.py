

from keras.models import Sequential
from keras.layers.core import Dense, Activation
from keras.layers.recurrent import LSTM
from keras.optimizers import Adam
from keras.callbacks import EarlyStopping

import sys
import numpy as np
import plotly
import plotly.plotly as py
import plotly.graph_objs as go
import pandas as pd
import math
import random
import warnings
import seaborn as sns
import matplotlib.pyplot as plt




plotly.offline.init_notebook_mode(connected=False)
warnings.filterwarnings('ignore')
sns.set_style("whitegrid", {'grid.linestyle': '--'})

def sin(x, T=100):
    return np.sin(2.0*np.pi * x / T)



def toy_problem(T=100, ampl=0.05):
    x = np.arange(0, 2 * T + 1)
    noise = ampl * np.random.uniform(low=-1.0, high=1.0, size=len(x))
    return sin(x) + noise


def make_dataset(raw_data, n_prev=100, maxlen=25):
    data, target = [], []
    
    for i in range(len(raw_data) - maxlen):
        data.append(raw_data[i : i + maxlen])
        target.append(raw_data[i + maxlen])
        
    reshaped_data = np.array(data).reshape(len(data), maxlen, 1)
    reshaped_target = np.array(target).reshape(len(target), 1)
    
    return reshaped_data, reshaped_target


function = toy_problem(T=100)
data, label = make_dataset(function, maxlen=25)
print(data.shape)
future_test = data[175].T
time_length = future_test.shape[1]
future_result = np.empty((0))
length_of_sequence = data.shape[1]
in_out_neurons = 1
n_hidden = 300



model = Sequential()
model.add(LSTM(n_hidden, batch_input_shape=(None, length_of_sequence, in_out_neurons), return_sequences=False))
model.add(Dense(in_out_neurons))
model.add(Activation('linear'))
optimizer = Adam(lr=1e-3)
model.compile(loss="mean_squared_error", optimizer=optimizer)

early_stopping = EarlyStopping(monitor='val_loss', mode='min', patience=15)

model.fit(data, label,
         batch_size=100, epochs=200,
         validation_split=0.1, callbacks=[early_stopping]
         )

for step in range(400):
    test_data= np.reshape(future_test, (1, time_length, 1))
    batch_predict = model.predict(test_data)
    
    future_test = np.delete(future_test, 0)
    future_test = np.append(future_test, batch_predict)
    
    future_result = np.append(future_result, batch_predict)

fig = plt.figure(figsize=(10,5),dpi=200)
sns.lineplot(
    color="#086039",
    data=function,
    label="Raw Data",
    marker="o"
)

sns.lineplot(
    color="#f44262",
    x=np.arange(25, len(predicted)+25),
    y=predicted.reshape(-1),
    label="Predicted Training Data",
    marker="o"
)

sns.lineplot(
    color="#a2fc23",
    y= future_result.reshape(-1),
    x = np.arange(0+len(function), len(future_result)+len(function)),
    label="Predicted Future Data",
    marker="o"
)


data_raw = go.Scatter(
    y = function, 
    x  = np.arange(0, len(function)),
    name = 'Raw Data',
    mode = 'lines',
    line = dict(
        color = 'red'
    )
)

predicted_graph = go.Scatter(
    y = predicted.reshape(-1),
    x = np.arange(25, len(predicted)+25),
    name  = 'Predicted Training Data',
    mode = 'lines',
    line = dict(
        color = 'blue'
    )
)

predicted_future = go.Scatter(
    y = future_result.reshape(-1),
    x = np.arange(0+len(function), len(future_result)+len(function)),
    name = 'Predicted Future Data',
    mode = 'lines',
    line = dict(
        color = 'green'
    )
)

data = [data_raw, predicted_graph, predicted_future]
plotly.offline.iplot(data)