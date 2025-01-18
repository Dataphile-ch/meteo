#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 12 15:13:24 2025

@author: william
"""

# %% libraries and constants
import requests
import datetime as dt
#import pytz # leave here as a reminder to maybe convert everything to UTC in case client and server are in different TZ
import json
import os
import sdcard
import machine
import gc
import uos
import wifi

#%% Setup

api_base_url = "http://pi.local:8000"

# mount SD card
try:
    os.stat("/sd")
    pass
except OSError:
    sd_spi = machine.SPI(0, sck=machine.Pin(18, machine.Pin.OUT), mosi=machine.Pin(19, machine.Pin.OUT), miso=machine.Pin(16, machine.Pin.OUT))
    sd = sdcard.SDCard(sd_spi, machine.Pin(22))
    uos.mount(sd, "/sd")
gc.collect()

# connect to wifi
wifi.connect()

#%% get doclist and then, if new files are avail, get doccontent and save to local store
url = f"{api_base_url}/doclist"
response = requests.get(url)
doclist = json.loads(response.text)

for i,_ in enumerate(doclist) :
    fname = doclist[i]['fname']
    fpath = '/sd/images/'
    mtime = dt.datetime.fromisoformat(doclist[i]['mtime'])

    # see if the images are newer than previously retrieved, or if they have never been retrieved.
    try :
        filestat = os.stat(f"{fpath}{fname}")
        last_mtime = dt.datetime.fromtimestamp(filestat[8])
    except OSError:
        last_mtime = dt.datetime.fromtimestamp(0)

    if mtime > last_mtime :
        url = url = f"{api_base_url}/doccontent?fname={fname}"
        response = requests.get(url)
        im = response.content
        with open(f'{fpath}/{fname}', 'wb') as file:
            file.write(im)

wifi.disconnect()