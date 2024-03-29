#!/bin/bash

echo "Verifying env variables presence."
declare -a REQUIRED_ENV_VARS=(
                                "${WENET_APP_ID}"
                                "${WENET_APP_SECRET}"
                                "${WENET_INSTANCE_URL}"
                                "${OAUTH_CALLBACK_URL}"
                                "${SURVEY_FORM_ID_EN}"
                                "${SURVEY_FORM_ID_IT}"
                                "${SURVEY_FORM_ID_ES}"
                                "${SURVEY_FORM_ID_MN}"
                                "${SURVEY_FORM_ID_DA}"
                              )

for e in "${REQUIRED_ENV_VARS[@]}"
do
  if [[ -z "$e" ]]; then
    # TODO should print the missing variable
    echo >&2 "Error: A required env variable is missing."
    exit 1
  fi
done

echo "Running survey..."

#
# Important note: env variables should not be passed as arguments to the module!
# This will allow for an easier automatisation of the docker support creation.
#

echo "Running migrations"
python manage.py migrate



exec uwsgi --ini=./uwsgi.ini --socket=0.0.0.0:80 --static-map "/${BASE_URL}static/=/var/www/static" 
