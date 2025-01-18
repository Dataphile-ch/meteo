#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 18 07:09:48 2024

@author: william

designed to run in a cron job every hour.

"""

#%% packages and constants
import resources.utils as utils
import datetime as dt

coord = utils.coordinates_ovz

outside = '037D79D802E0'
upstairs = '12432F33E468'
downstairs = '037DB068AC88'

#%% main()
to_zone = utils.get_tz_from_coord(coord)
hour_timestamp = dt.datetime.now(tz=to_zone).replace(minute=0, second=0, microsecond=0)
day_timestamp = hour_timestamp.replace(hour=0)

meteo_df = utils.get_meteo(coord, 1)

mm_out_t = meteo_df.loc[hour_timestamp]['temp']
mm_out_p = meteo_df.loc[hour_timestamp]['pressure']
mm_out_r = meteo_df.loc[hour_timestamp]['precip']
mm_out_s = meteo_df.loc[hour_timestamp]['symbol']
mm_out_w = meteo_df.loc[hour_timestamp]['wind_speed']
mm_out_d = meteo_df.loc[hour_timestamp]['wind_dir']

dev_ids = f"{outside},{upstairs},{downstairs}"
tfa_df = utils.get_tfa_data(dev_ids)
out_t = tfa_df.loc[outside]['measurement.t1']
out_h = tfa_df.loc[outside]['measurement.h']
in_t = tfa_df.loc[upstairs]['measurement.t1']
in_h = tfa_df.loc[upstairs]['measurement.h']

# prepare the csv output
newRow = f'"{hour_timestamp}", {mm_out_t}, {mm_out_p}, {mm_out_r}, {mm_out_s}, {mm_out_w}, {mm_out_d}, {out_t}, {out_h}, {in_t}, {in_h}\n'

#Create a log file for each day.  Either open and append to it, or create a new one for a new day.
today = day_timestamp.strftime("%Y%m%d")
log_fname = f'logs/meteo_log2_{today}.log'

with open(log_fname, 'a') as f :
    f.write(newRow)
    f.close()  

# this will overwrite (create new version) if it already exists
utils.s3_upload(log_fname)
     
