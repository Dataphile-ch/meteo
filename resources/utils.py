#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 10 11:18:16 2024

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

import resources.credentials as cred

locations = {'gva' : {'name' : 'Genève', 'coords' : [(46.202714, 6.156264)]} ,
             'ovz' : {'name' : 'Ovronnaz', 'coords' : [(46.19713322143545, 7.179511629821311)]} ,
             'vic' : {'name' : 'Victoria BC', 'coords' : [(48.454544, -123.345373)]} ,
             'mgd' : {'name' : 'Magdeburg', 'coords' : [(52.176302, 11.606809)] } ,
             'wlg' : {'name' : 'Wellington', 'coords' : [(-41.291006, 174.793324)] } ,
             'akl' : {'name' : 'Auckland', 'coords' : [(-36.863569, 174.584487)] } ,
             'tos' : {'name' : 'Tromsø', 'coords' : [(69.662723, 18.965742)] } 
             }


#%% Get timezone from coordinates using google maps api
def get_tz_from_coord(coord) :
    google_key = cred.GMAPS_API_KEY
    api_base_url = 'https://maps.googleapis.com/maps/api/timezone/json'
    coord_url = "+".join(["{}%2C{}".format(*latlon_tuple) for latlon_tuple in coord])
    tstamp = time()

    url = f"{api_base_url}?location={coord_url}&timestamp={tstamp}&key={google_key}"
    response = requests.get(url)
    tzname = json.loads(response.text)['timeZoneId']
    tzID = tz.gettz(tzname)
    return tzID
    
#%% get_meteo function
def get_meteo(coord=locations['gva']['coords'], ndays=5) :
    """
    This version uses the direct REST API call and converts the JSON response to Pandas.
    No need for meteomatics python package to be installed.
    
    Parameters
    ----------
    coord : tuple with lat, long location coordinates 
    ndays : number of days to forecast

    Returns
    -------
    pd dataframe with date time index in UTC and columns for each weather parameter.

    """
    username = cred.METEOM_USER
    password = cred.METEOM_PASS
    
    # convert from UTC to timezone at coord    
    to_zone = get_tz_from_coord(coord)

    api_base_url = "https://api.meteomatics.com"

    startdate_ts = dt.datetime.now(tz=to_zone).replace(hour=0, minute=0, second=0, microsecond=0).astimezone(pytz.utc)
    enddate_ts = startdate_ts + dt.timedelta(days=ndays)
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

#%% Calibrate the forecast temp using pre-trained model
def calibrate_forecast(meteo_df) :
    """
    
    Parameters
    ----------
    meteo_df : pd.DataFrame

    Returns
    -------
    y_df : dataframe with predicted y values

    """
    import pickle
    import numpy as np
    filename = 'resources/calibration_model.pkl'
    clf = pickle.load(open(filename, 'rb'))

    X_df = meteo_df[['temp', 'pressure', 'precip', 'symbol', 'wind_speed', 'wind_dir']].copy()
    X_df['day_night'] = np.floor(X_df['symbol']/100)
    X_df['symbol'] = X_df['symbol']%100
    X_data = X_df.values

    y_pred = clf.predict(X_data)
    y_df = pd.Series(data=y_pred, index=X_df.index, name='calibrated_temp')
    y_df = y_df.rolling(3, min_periods=1, center=True).mean()
    return y_df
    
#%% TFA Dostman API call

def get_tfa_data(dev_ids) :
    
    api_base_url = "https://www.data199.com/api/pv1"
    req_type = "device/lastmeasurement"
    rqst_data = {"deviceids" : dev_ids}
    url = f"{api_base_url}/{req_type}"

    response = requests.post(url, json=rqst_data)

    tfa_df = pd.json_normalize(json.loads(response.text)['devices'])
    tfa_df.set_index('deviceid', inplace=True)
        
    return tfa_df

#%% Upload/Download log files to S3
def s3_upload(fname) :
    
    s3_client = boto3.client(
        's3',
        aws_access_key_id=cred.AWS_KEY,
        aws_secret_access_key=cred.AWS_SECRET
    )
    
    bucket = 'cloud-wm64-ch'
    key = f'meteo/{os.path.basename(fname)}' # remove the path from fname
    
    s3_client.upload_file(fname, bucket, key)

    return

def s3_download() :
    
    s3_client = boto3.client(
        's3',
        aws_access_key_id=cred.AWS_KEY,
        aws_secret_access_key=cred.AWS_SECRET
    )
    
    bucket = 'cloud-wm64-ch'
    key = 'meteo/'
    prefix = 'meteo_log2'

    #initiate s3 resource
    s3 = boto3.resource('s3')
    
    # select bucket
    my_bucket = s3.Bucket(bucket)
    
    # download all files in this bucket into logs directory
    for s3_object in my_bucket.objects.filter(Prefix=key):
        # Need to split s3_object.key into path and file name, else it will give error file not found.
        path, filename = os.path.split(s3_object.key)
        if filename != '' and filename.startswith(prefix):
            target = f'logs/{filename}'
            my_bucket.download_file(s3_object.key, target)
        
    return
