#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 12 15:13:24 2025

@author: william
"""

# %% libraries and constants
#import datetime as dt
#import pytz # leave here as a reminder to maybe convert everything to UTC in case client and server are in different TZ
import json
import os
import sdcard
import machine
import gc
import uos
import requests
import wifi


def get_images() :
    
    api_base_url = "http://pi.local:8000"
    
    # mount SD card
    try:
        os.stat("/sd")
    except OSError:
        sd_spi = machine.SPI(0, sck=machine.Pin(18, machine.Pin.OUT), mosi=machine.Pin(19, machine.Pin.OUT), miso=machine.Pin(16, machine.Pin.OUT))
        sd = sdcard.SDCard(sd_spi, machine.Pin(22))
        uos.mount(sd, "/sd")
    gc.collect()
    
    
    # get doclist and then, if new files are avail, get doccontent and save to local store

    # connect to wifi
    connected = wifi.connect()
    if not connected :
        return False

    url = f"{api_base_url}/doclist"
    try:
        response = requests.get(url)
    except:
        return False
    
    doclist = json.loads(response.text)
    del response
    gc.collect()
    
    for i,_ in enumerate(doclist) :
        fname = doclist[i]['fname']
        if fname[-3:] == 'jpg' : # we only want the jpeg files.
            fpath = '/sd/images/'
            
            # here we could put some code to only download images that are newer.
            
            url = f"{api_base_url}/doccontent?fname={fname}"
            try :
                response = requests.get(url)
                im = response.content
            except :
                return "Get Doc Content Failed"

            gc.collect()
            with open(f'{fpath}/{fname}', 'wb') as file:
                file.write(im)
            del response
            gc.collect()
            
    source = "Inky 5.7".replace(" ", "%20")
    message = "Images downloaded".replace(" ", "%20")
    url = f"{api_base_url}/status?source={source}&message={message}"
    try :
        response = requests.put(url)
    except :
        return "Write Log Failed"

    wifi.disconnect()
    
    return True
