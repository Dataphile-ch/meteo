#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 16 20:52:18 2024

@author: william
"""

#%% Imports and constants
import resources.utils as utils
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from glob import glob
from math import floor, ceil

#%% Functions
def merge_logs() :
    
    col_names = ['datestamp', 'pred_temp', 'pred_precip', 'act_temp_out', 'act_humid_out', 'act_temp_in', 'act_humid_in']
    files = glob('logs/meteo_log2_*.log')
    meteo_log = pd.concat((pd.read_csv(f, names=col_names) for f in files), ignore_index=True, axis=0)
    meteo_log.set_index('datestamp', inplace=True)
    meteo_log.index = pd.to_datetime(meteo_log.index)

    return meteo_log

#%% main
utils.s3_download()
meteo_log = merge_logs()

px = 1/plt.rcParams['figure.dpi']  # pixel in inches
fig = plt.figure(figsize=(800*px, 880*px))

plt.scatter(meteo_log['pred_temp'], meteo_log['act_temp_out'] )
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.title('Predicted vs Actual Temp')

min_temp = floor(min(meteo_log['pred_temp'].min(), meteo_log['act_temp_out'].min()))
max_temp = ceil(max(meteo_log['pred_temp'].max(), meteo_log['act_temp_out'].max()))
plt.xlim(min_temp, max_temp)
plt.ylim(min_temp, max_temp)
plt.grid()

plt.show()
