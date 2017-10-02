#!/bin/bash

set -e
if [ $# -eq 0 ]; then
  CSVFILE='ledger.csv'
else
  CSVFILE='$1'
fi

if [ ! -f $CSVFILE ]; then
  echo "Ledger file not found!"
  exit 1
fi

rm -rf env
virtualenv -p python3 env
. env/bin/activate
pip install -r requirements.txt
python manage.py db upgrade
python import_data.py $CSVFILE
python generate_api_key.py
