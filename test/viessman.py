#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 15 20:49:00 2024

@author: william
"""

import utils
import credentials as cred
import boto3

#%% Get data from Viessman heating system
def v_auth() :
    
    # authorization
    # returns some html stuff with a key like this:
    #    data-sitekey="6Lcjo98nAAAAAN-26e_wrRwaMARp1a3HBpcSmC8P"

    code_verifier, code_challenge = pkce.generate_pkce_pair()
    
    api_base_url = 'https://iam.viessmann.com/idp/v3/authorize'
    redirect_uri = 'http://localhost:4200/'
    scope = 'IoT'

    url_payload = {
        'response_type' : 'code' ,
        'client_id' : cred.V_KEY ,
        'redirect_uri' : redirect_uri ,
        'scope' : scope ,
        'code_challenge' : code_challenge ,
        'code_challenge_method' : 'S256'
        }

    # authorization code exchange
    api_base_url = 'https://iam.viessmann.com/idp/v3/authorize'

    response = requests.get(api_base_url, data=url_payload)
    
    return code_verifier, response

def v_token(code_verifier, auth_code) :

    auth_code = '2SjLev9nvZv7etqTtZSmah8rME-APp4TTkRLnLgSXn4'
    api_base_url = 'https://iam.viessmann.com/idp/v3/authorize'
    redirect_uri = 'http://localhost:4200/'

    url_payload = {
        'grant_type' : 'authorization_code' ,
        'client_id' : cred.V_KEY ,
        'redirect_uri' : redirect_uri ,
        'code_verifier' : code_verifier ,
        'code' : auth_code
        }

    url_header = {'Content-Type' : 'application/x-www-form-urlencoded'}

    # authorization code exchange
    api_base_url = 'https://iam.viessmann.com/idp/v3/token'

    response = requests.get(api_base_url, data=url_payload, headers=url_header)
    
    return response

def v_get_data() :
    # get temp data    
    api_base_url = 'https://iam.viessmann.com/iot/v2/features/installations'

# GET https://api.viessmann.com/iot/v2/features/installations/{{installationID}}/gateways/{{gatewaySerial}}/devices/{{deviceId}}/features/heating.sensors.temperature.outside
    
    return

