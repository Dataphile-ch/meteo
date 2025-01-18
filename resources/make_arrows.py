# -*- coding: utf-8 -*-

from PIL import Image

compass = {'N' : 0,
           'NW' : 45,
           'W' : 90,
           'SW' : 135,
           'S' : 180,
           'SE' : 225,
           'E' : 270,
           'NE' : 315}

with Image.open("resources/N.jpg") as im :
    for comp in compass :
        fname = f"resources/{comp}.PNG"
        p = im.rotate(compass[comp],fillcolor='#ffffff')
        p.save(fname)

