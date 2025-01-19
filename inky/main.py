#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 15 08:34:55 2025

@author: william

main.py runs automatically on startup.

Assume that we are on battery and wake every 60 min.

"""

import inky_frame
import inky_helper as ih
import machine
import gc
import get_images
import disp_images 

def lights_off():
    led_warn = machine.Pin(6, machine.Pin.OUT)
    led_warn.off()
    inky_frame.button_a.led_off()
    inky_frame.button_b.led_off()
    inky_frame.button_c.led_off()
    inky_frame.button_d.led_off()
    inky_frame.button_e.led_off()
    inky_frame.led_wifi.off()

def sleep_until_next_hour():
    year, month, day, dow, hour, minute, second, _ = machine.RTC().datetime()
    sleep_time = 60-minute+1
    inky_frame.sleep_for(sleep_time) 

lights_off()

new_im = get_images.get_images() 
gc.collect()

if ih.inky_frame.button_d.read() :
    fname = 'dog.jpg'
else:
    fname = 'weekly.jpg'

disp_images.display_image(fname)    
gc.collect()
sleep_until_next_hour()
machine.reset() # safer than an infinte loop.  Avoids mem leaks.
