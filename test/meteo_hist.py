#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 22 10:21:30 2024

@author: william
"""
# %% libraries and constants
import requests
import pandas as pd
import datetime as dt
from dateutil import tz
from time import time
import pytz
import json
import os
import boto3
from utils import get_tz_from_coord

import credentials as cred

coordinates_gva = [(46.202714, 6.156264)]
coordinates_ovz = [(46.19713322143545, 7.179511629821311)]
coordinates_vic = [(48.454544, -123.345373)]

#%% get_meteo function
def get_meteo(coord, startdate_ts, enddate_ts) :
    """
    This version uses the direct REST API call and converts the JSON response to Pandas.
    No need for meteomatics python package to be installed.
    
    Parameters
    ----------
    coord : tuple with lat, long location coordinates 

    Returns
    -------
    pd dataframe with date time index in UTC and columns for each weather parameter.

    """
    username = cred.METEOM_USER
    password = cred.METEOM_PASS
    
    # convert from UTC to timezone at coord    
    to_zone = get_tz_from_coord(coord)

    api_base_url = "https://api.meteomatics.com"

    interval_ts = 'PT1H'

    parameters_dict = {
        't_2m:C' : 'temp',
        'msl_pressure:hPa' :'pressure' ,
        'precip_1h:mm' : 'precip',
        'weather_symbol_1h:idx' : 'symbol',
        'uv:idx' : 'uv' ,
        'wind_speed_10m:ms' : 'wind_speed', 
        'wind_dir_10m:d' : 'wind_dir',
        'sunrise:sql' : 'sunrise', 
        'sunset:sql' : 'sunset'
        }
    parameters_url = ','.join(parameters_dict.keys())
    
    start_url = startdate_ts.replace(tzinfo=pytz.UTC).isoformat()
    end_url = enddate_ts.replace(tzinfo=pytz.UTC).isoformat()
    coord_url = "+".join(["{},{}".format(*latlon_tuple) for latlon_tuple in coord])
    model = 'mix'

# example url 
# TIME_SERIES_TEMPLATE = "{api_base_url}/{startdate}--{enddate}:{interval}/{parameters}/{coordinates}/bin?{urlParams}"
#    https://api.meteomatics.com/2024-12-10T18:40:00.000+01:00--2024-12-13T18:40:00.000+01:00:PT1H/t_2m:C/51.5073219,-0.1276474/json?model=mix
    url = f"{api_base_url}/{start_url}--{end_url}:{interval_ts}/{parameters_url}/{coord_url}/json?model={model}"
    response = requests.get(url, auth=(username, password))
#    if response.status_code != requests.codes.ok:
#        raise response.text

# data is in response.text['data'] with 1 row per requested parameter
# parameter name is in 'parameter' key
# data is in list of dict with key 'dates' inside dict with key 'coordinates'
    j = json.loads(response.text)
    
    meteo = pd.DataFrame()
    for p in j['data'] :
        col = p['parameter']
        t_series = p['coordinates'][0]['dates']
        df = pd.json_normalize(t_series)
        df['Datetime'] = pd.to_datetime(df['date'])
        df.set_index('Datetime', inplace=True)
        df.drop(['date'], axis=1, inplace=True)
        df.rename(columns={'value' : col}, inplace=True)
        meteo = pd.concat([meteo, df], axis=1)

    meteo.rename(columns=parameters_dict, inplace=True)

# convert from UTC to timezone at coord    
    meteo = meteo.tz_convert(tz=to_zone)
        
    return meteo

#%% main

to_zone = get_tz_from_coord(coordinates_ovz)

# 2024-12-19
startdate_ts = dt.datetime(2024,12,19,1,0,0,0, to_zone).astimezone(pytz.utc)
enddate_ts =  dt.datetime.now(tz=to_zone).replace(minute=0, second=0, microsecond=0).astimezone(pytz.utc)

meteo_hist = get_meteo(coordinates_ovz, startdate_ts, enddate_ts)

