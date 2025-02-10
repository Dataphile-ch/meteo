#!/bin/bash
exec 2>&1 1>meteo_composer.out

cd meteo
source .venv/bin/activate
python -m logger

exit 0
