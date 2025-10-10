#!/bin/bash
# webAPIrun

# Stop on errors
set -Eeuo pipefail
set -x

# If var/webAPI.sqlite3 does not exist, print an error and exit non-zero. 
if [ ! -f var/webAPI.sqlite3 ]; then
  echo "Error: can't find database var/webAPI.sqlite3"
  echo "Try: bash /bin/webAPIdb.sh create"
  exit 1
fi

#Run the development server on port 8000.
flask --app webAPI --debug run --host 0.0.0.0 --port 8000

# http://localhost:8000/api/datas/
# pasrse this link to view the output format of the API call