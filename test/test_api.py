#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 16 18:39:14 2025

@author: william
"""
import requests
api_base_url = "http://pi.local:8000"

source = "Inky 5.7"
message = "Images downloaded"
url = url = f"{api_base_url}/status?source={source}&message={message}"
try :
    response = requests.put(url)
    im = response.content
except :
    pass
