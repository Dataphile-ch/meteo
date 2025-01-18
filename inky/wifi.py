import inky_frame
import network
from utime import sleep as utime_sleep

import secrets

def connect():
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.config(pm=0xa11140)  # Turn WiFi power saving off for some slow APs

    wlan.connect(secrets.WIFI_SSID, secrets.WIFI_PASSWORD)

    connect_retries = 0
    while not wlan.isconnected() :
        print('Waiting for WiFi connection...')
        utime_sleep(1)
        connect_retries += 1
        if connect_retries > 10 :
            break

    if connect_retries > 10 :
        return False
    else :
        inky_frame.led_wifi.on()
        # take the opportunity to set RTC to network time.
        inky_frame.set_time()
        print(wlan.ifconfig())
        return True

def disconnect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.disconnect()
    inky_frame.led_wifi.off()

