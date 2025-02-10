# Install meteo composer and API on RPI

## GIT install and download repo

sudo apt-get install git

git config --global user.name "William"

git config --global user.email "william@dataphile.ch"

sudo apt-get install gh

gh auth login

gh repo clone meteo

cd meteo

python -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt 

sudo apt install python3-fastapi

## To get updates from main repo
git fetch origin

git merge

## Python install

python -m venv .venv

pip install -r requirements.txt

source .venv/bin/activate

## Composer and Logger
copy bash script to user home:

cp meteo/composer/meteo_composer.sh ~

cp meteo/logger/meteo_logger.sh ~

put this entry in crontab (crontab -e) :

0 * * * * ./meteo_composer.sh

5 * * * * ./meteo_logger.sh

## API
Copy docservice.sh to user home ~

cp meteo/api/docservice.sh ~

sudo cp api/docservice.service /etc/systemd/system

sudo systemctl daemon-reload

sudo systemctl start docservice

sudo systemctl status docservice
