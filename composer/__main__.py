#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  9 09:53:40 2024

@author: william

This is the weather graphic composer.
Get weather data from meteomatics and from local TFA sensors
Calibrate it using pre-trained model
Create graphics for display somewhere

"""
# %% Libraries and constants
import resources.utils as utils
import numpy as np
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from matplotlib.patches import FancyArrowPatch
from matplotlib import ticker
import matplotlib.cm as cm
import matplotlib.colors as colours
from PIL import Image, ImageDraw, ImageFont

LOCATION = 'ovz'
loc_name = utils.locations[LOCATION]['name']
coord = utils.locations[LOCATION]['coords']
to_zone = utils.get_tz_from_coord(coord)


#%% helper functions
def make_in_out(in_t : float, out_t: float) :
    house = Image.open('resources/house.png')
    y_coord = int(house.size[1]/2)
    x1_coord = int(house.size[0]*1/5)
    x2_coord = int(house.size[0]*1/2)
    d = ImageDraw.Draw(house)
    d.text((x1_coord,y_coord), f"{int(in_t)}\N{DEGREE SIGN}C", fill='#000000', font_size=98)
    d.text((x2_coord,y_coord), f" {out_t:.1f}\N{DEGREE SIGN}", fill='#000000', font_size=98)
    new_size = tuple(int(x/8) for x in house.size)
    house = house.resize(new_size)
    return house

def get_wind_arrow(direct: float, speed: float):
#    d360 = np.arange(361 )
    dir_bucket = (direct + 45/2) // 45 % 8
    compass_dir = {0 : 'N' ,
               1 : 'NE',
               2 : 'E',
               3 : 'SE',
               4 : 'S',
               5 : 'SW',
               6 : 'W',
               7 : 'NW'}

    # map wind speed to colours using cmap
    # cmap from 0-100kmh, use viridis_r
    norm = colours.Normalize(vmin=0, vmax=100, clip=True)
    cmap = plt.get_cmap('viridis_r')
    R, G, B, _ = cmap(norm(speed))
    R = int(R*256)
    G = int(G*256)
    B = int(B*256)

    fname = f"resources/{compass_dir[dir_bucket]}.PNG"
    with Image.open(fname) as im :
        arrow = Image.new('RGB', size=(40,60), color='#ffffff')
        arrow.paste(im.resize((40,40)))
        d_out = list(arrow.getdata())
        for i,d in enumerate(d_out) :
            if d == (0,0,0):
                d_out[i] = (R,G,B)
        arrow.putdata(d_out)
            
        d = ImageDraw.Draw(arrow)
        d.text((2,45), f"{compass_dir[dir_bucket]} {speed:.1f}", fill='#000000', font_size=12)
    return arrow


def turning_points(series : pd.Series ) :
    # turning points are more interesting than daily max/min
    # apply some more smoothing to get rid of local max/min
    smooth = series.rolling(5, min_periods=1, center=True).mean() 

    dx = np.gradient(smooth)
    dx2 = np.gradient(dx)
    tp = dx[1:] * dx[:-1] <0 # tp=True for turning points
    mins = np.logical_and( (dx[:-1] * dx[1:] <0) , dx2[:-1] > 0 )
    maxs = np.logical_and( (dx[:-1] * dx[1:] <0) , dx2[:-1] < 0 )
    mins[0] = False
    mins = np.append(mins, False) # add one more to preserve size
    maxs[0] = False
    maxs = np.append(maxs, False) # add one more to preserve size
    return series[mins], series[maxs]
    

# %% Get data from Meteomatics and local TFA sensors

meteo_df = utils.get_meteo(coord, 7)

if LOCATION == 'ovz' :
    calibrated_temp = utils.calibrate_forecast(meteo_df)
    meteo_df['temp'] = calibrated_temp

# make daily table of min, max temp and symbol at 12.00
min_temp = meteo_df.resample('d').min()['temp']
max_temp = meteo_df.resample('d').max()['temp']
w_sym = meteo_df[meteo_df.index.hour==12]['symbol']
daily_wind_dir = meteo_df[meteo_df.index.hour==12]['wind_dir'].astype(float)
daily_wind_speed = meteo_df[meteo_df.index.hour==12]['wind_speed'].astype(float)

outside = '037D79D802E0'
upstairs = '12432F33E468'
downstairs = '037DB068AC88'
dev_ids = f"{outside},{upstairs},{downstairs}"
tfa_df = utils.get_tfa_data(dev_ids)
out_t = tfa_df.loc[outside]['measurement.t1']
out_h = tfa_df.loc[outside]['measurement.h']
in_t = tfa_df.loc[upstairs]['measurement.t1']
in_h = tfa_df.loc[upstairs]['measurement.h']


# %% Plotting

now = dt.datetime.now().astimezone(to_zone)

px = 1/plt.rcParams['figure.dpi']  # pixel in inches
fig = plt.figure(figsize=(800*px, 480*px), layout='constrained')
fig = plt.figure(figsize=(600.5*px, 448.5*px), layout='constrained')
gs = plt.GridSpec(2, 1, height_ratios=[7, 3], figure=fig)

ax1 = fig.add_subplot(gs[0])
ax2 = ax1.twinx()
ax3 = fig.add_subplot(gs[1])
ax3.axis("off") # this ax just creates some white space at the bottom

xvalues = meteo_df.index 
ytemp = meteo_df['temp'].values
yrain = meteo_df['precip'].values
ax1.plot(xvalues, ytemp, color='red', linewidth=2)

# fidding with the x labels
xfmt = DateFormatter('   %a %d.%m', tz=to_zone)
ax1.xaxis.set_major_formatter(xfmt)
ax1.axes.set_xticklabels(ax1.xaxis.get_majorticklabels(),ha = "left")
ax1.tick_params(axis='both', labelsize=8)

# vertical line at current time
ax1.axvline(now,color='r', linestyle='--') 
ax1.axhline(y=0, color='b')

# annotate max and min points
temp_series = meteo_df['temp']
min_pts, max_pts = turning_points(temp_series)
for i,m in enumerate(max_pts) :
    ax1.annotate(f"{max_pts.values[i]:.0f}\N{DEGREE SIGN}", 
                 xy=(max_pts.index[i], max_pts.values[i]), 
                 xytext=(max_pts.index[i], max_pts.values[i] +0.5),
                 size=9)
for i,m in enumerate(min_pts) :
    ax1.annotate(f"{min_pts.values[i]:.0f}\N{DEGREE SIGN}", 
                 xy=(min_pts.index[i], min_pts.values[i]), 
                 xytext=(min_pts.index[i], min_pts.values[i] -1),
                 size=9)

# more formatting
ax1.set(ylim=(ytemp.min() // 1 -1 , ytemp.max() // 1 +2))
ax1.set_ylabel('Temperature C', size=7)
ax1.grid(True)

# precipitation on the second axis
ax2.bar(xvalues, yrain, width=0.03)
ymin, ymax = ax2.get_ylim()
ax2.set(ylim=(0,max(2,ymax*2)))
ax2.set_ylabel('Precipitation mm', size=6)
ax2.tick_params(axis='both', labelsize=8)
ax2.yaxis.set_major_formatter(ticker.StrMethodFormatter("{x:.1f}"))

# Current temp and humid readings.
if LOCATION == 'ovz' and True:
    im = make_in_out(in_t, out_t)
    plt.figimage(im, xo=5, yo=5)

# get xtick pixel locations to use for positioning graphics and other info
# note that the tick labels are approx 80px apart -> 80x80 for the graphics
xt = ax1.get_xticks()
ymin, _ = ax1.get_ylim()
xt_locs = ax1.transData.transform([(xtick, ymin) for xtick in xt])

xcoord = xt_locs.T[0][:w_sym.size] *1.05 # scaling because the images don't align :(
ycoord = xt_locs.T[1][:w_sym.size] 

# weather symbols at midday
for i, (_,sym) in enumerate(w_sym.items()) :
    fname = f'../meteo/resources/{int(sym)}.png'
    with Image.open(fname) as im :
        xc = xcoord[i] - 20
        yc = ycoord[i] - 95
        plt.figimage(im, xo=xc, yo=yc)

# wind direction and speed    
for i, w in enumerate(daily_wind_dir.values) :
    wind = get_wind_arrow(daily_wind_dir[i], daily_wind_speed[i])
    xc = xcoord[i] - 12
    yc = ycoord[i] - 150
    plt.figimage(wind, xo=xc, yo=yc)

# timestamp in corner
ts = f"{loc_name}\n{now:%Y.%m.%d %H:%M}"
fig.text(0.83,0.01, ts, fontsize=7, in_layout=True)

# all finished
plt.show()
fname = 'images/weekly.png'
fig.savefig(fname)
fname = 'images/weekly.jpg'
fig.savefig(fname)
