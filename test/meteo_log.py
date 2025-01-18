#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 16 14:08:23 2024

@author: william

Get data from meteomatics and from local sensors hourly.
Log to a CSV file daily.

"""

#%% packages and constants
import utils
import numpy as np
import pandas as pd
import datetime as dt
import time

coordinates_gva = [(46.202714, 6.156264)]
coordinates_ovz = [(46.19713322143545, 7.179511629821311)]
coordinates_vic = [(48.454544, -123.345373)]
coordinates_mgd = [(52.176302, 11.606809)] 
coord = coordinates_ovz

#%% Main
while True :

    to_zone = utils.get_tz_from_coord(coord)
    hour_timestamp = dt.datetime.now(tz=to_zone).replace(minute=0, second=0, microsecond=0)
    day_timestamp = hour_timestamp.replace(hour=0)
    
    meteo_df = utils.get_meteo(coord, 1)
    
    mm_out_t = meteo_df.loc[hour_timestamp]['temp']
    mm_out_p = meteo_df.loc[hour_timestamp]['precip']
    
    outside = '037D79D802E0'
    upstairs = '12432F33E468'
    downstairs = '037DB068AC88'
    dev_ids = f"{outside},{upstairs},{downstairs}"
    tfa_df = utils.get_tfa_data(dev_ids)
    out_t = tfa_df.loc[outside]['measurement.t1']
    out_h = tfa_df.loc[outside]['measurement.h']
    in_t = tfa_df.loc[upstairs]['measurement.t1']
    in_h = tfa_df.loc[upstairs]['measurement.h']
    
    # prepare the csv output
    newRow = f'"{hour_timestamp}", {mm_out_t}, {mm_out_p}, {out_t}, {out_h}, {in_t}, {in_h}\n'
    
    #Create a log file for each day.  Either open and append to it, or create a new one for a new day.
    today = day_timestamp.strftime("%Y%m%d")
    log_fname = f'meteo_log_{today}.log'
    
    with open(log_fname, 'a') as f :
        f.write(newRow)
        f.close()  
    
    utils.s3_upload(log_fname)
     
    time.sleep(3600)
