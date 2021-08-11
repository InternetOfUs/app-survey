#!/bin/bash
python manage.py test

if [[ $? != 0 ]]; then
    echo "Error: Tests are failing."
    exit 1
fi

