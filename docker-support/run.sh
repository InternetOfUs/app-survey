#!/bin/bash


echo "Running service..."

#
# Important note: env variables should not be passed as arguments to the module!
# This will allow for an easier automatisation of the docker support creation.
#



echo "Running migrations"
python manage.py migrate

exec uwsgi --ini=./uwsgi.ini --socket=0.0.0.0:80 --static-map "/static=/var/www/static"
