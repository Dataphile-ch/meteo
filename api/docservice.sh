#!/bin/bash
exec 2>&1 1>/home/william/docservice.out

cd /home/william/meteo
source .venv/bin/activate
fastapi run /home/william/meteo/api/__main__.py 

exit 0
