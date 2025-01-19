#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 08:37:40 2025

@author: william
"""

import gc
import os
import uos
import machine
import time
import sdcard
from picographics import PicoGraphics, DISPLAY_INKY_FRAME as DISPLAY
from jpegdec import JPEG


def display_image(fname) :
    
    fpath = f"/sd/images/{fname}"
    
    # mount SD card
    try:
        os.stat("/sd")
        pass
    except OSError:
        sd_spi = machine.SPI(0, sck=machine.Pin(18, machine.Pin.OUT), mosi=machine.Pin(19, machine.Pin.OUT), miso=machine.Pin(16, machine.Pin.OUT))
        sd = sdcard.SDCard(sd_spi, machine.Pin(22))
        uos.mount(sd, "/sd")
    gc.collect()


    # get image and display
    graphics = PicoGraphics(DISPLAY)
    j = JPEG(graphics)
    
    try :
        j.open_file(fpath)
        j.decode()
        gc.collect()
    except :
        return False
    else: 
        graphics.set_blocking(False) # stops timeout and hanging when on battery.
        while graphics.is_busy():
            print("Waiting for graphics to be ready")
            time.sleep(0.5)
        graphics.update()
        while graphics.is_busy():
            print("Waiting for graphics to update")
            time.sleep(2)
        return True

