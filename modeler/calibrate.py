#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 21 12:15:48 2024

@author: william

Uses historical data from meteomatics and actual readings from TFA to calibrate the meteomatics forecast.


"""

#%% Packages and constants
import resources.utils as utils
import numpy as np
import pandas as pd
from glob import glob

from sklearn.pipeline import Pipeline
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, KBinsDiscretizer, StandardScaler
from sklearn.compose import ColumnTransformer

import pickle
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

#%% Functions
def merge_logs() :
    
    col_names = [ 'pred_temp', 'pressure', 'pred_precip', 'w_symbol', 'wind_speed', 'wind_dir', 'act_temp_out', 'act_humid_out', 'act_temp_in', 'act_humid_in']
    files = glob('logs/meteo_log2_*.log')
    meteo_log = pd.concat((pd.read_csv(f, names=col_names, parse_dates=True) for f in files), axis=0)

    return meteo_log

#%% Data retrieval and prep

utils.s3_download()
meteo_log = merge_logs()

# drop the inside temp and humid readings.
meteo_log.drop(['act_temp_in', 'act_humid_in'], axis=1, inplace=True)
# move the day/night indicator to a separate column
meteo_log['day_night'] = np.floor(meteo_log['w_symbol']/100)
meteo_log['w_symbol'] = meteo_log['w_symbol']%100
meteo_log.sort_index(inplace=True)

#%% Main

y_data = meteo_log['act_temp_out'].values
X_data = meteo_log.drop(['act_temp_out', 'act_humid_out'], axis=1).values

X_train, X_test, y_train, y_test = train_test_split(X_data, y_data, random_state=42)

### Transformer for weather categories
weather_categories = [i for i in range(1,17)] 

categorical_features = [3] 
categorical_transformer = Pipeline(
    steps=[
        ("encoder", OneHotEncoder(handle_unknown="ignore")),
    ]
)
compass_feature = [5]
compas_transformer = Pipeline(
    steps=[
        ("discretize", KBinsDiscretizer(n_bins=4))
    ]
)

numeric_features = [i for i in range( X_train.shape[1] )] 
for c in categorical_features :
    numeric_features.remove(c)
for c in compass_feature :
    numeric_features.remove(c)

numeric_features = [0,1,2,4]    

numeric_transformer = Pipeline(
    steps=[
        ("scaler", StandardScaler()),
    ]
)

preprocessor = ColumnTransformer(
    transformers=[
        ("cat", categorical_transformer, categorical_features),
        ("num", numeric_transformer, numeric_features),
        ("compass", compas_transformer, compass_feature),
    ]
)

clf = Pipeline(
    steps=[("preprocessor", preprocessor), 
           ("classifier", MLPRegressor(hidden_layer_sizes=(200,100,50,)))]
)

clf.fit(X_train, y_train)
print("model score: %.3f" % clf.score(X_test, y_test))
filename = 'resources/calibration_model.pkl'
pickle.dump(clf, open(filename, 'wb'))

#%% Show results on all data
y_pred = clf.predict(X_data)
y_forecast = meteo_log['pred_temp'].values

px = 1/plt.rcParams['figure.dpi']  # pixel in inches
fig, ax1 = plt.subplots(figsize=(800*px, 600*px))

ax1.plot(meteo_log.index, y_forecast, label='Weather Forecast')
ax1.plot(meteo_log.index, y_data, label='Actuals')
ax1.plot(meteo_log.index, y_pred, label='Model Predictions')
ax1.set_ylabel('Temp \N{DEGREE SIGN}C', size=10)
ax1.xaxis.set_major_locator(mdates.DayLocator())
ax1.xaxis.set_minor_locator(mdates.DayLocator())
ax1.xaxis.set_major_formatter(mdates.ConciseDateFormatter(ax1.xaxis.get_major_locator()))
ax1.grid(axis='x')
ax1.legend()
plt.show()
