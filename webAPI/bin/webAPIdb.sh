#!/bin/bash
# insta485db

# Stop on errors
# See https://vaneyckt.io/posts/safer_bash_scripts_with_set_euxo_pipefail/
set -Eeuo pipefail
# set -x

# Set paths
initDir="var"
dbDir="var/db"
dbFile="insta485db.sqlite3"
filePath="var/webAPI.sqlite3"
schemaPath="sql/schema.sql"
dataPath="sql/data.sql"

# Sanity check command line options
usage() {
  echo "Usage: $0 (create|destroy|reset|dump)"
}

if [ $# -ne 1 ]; then
  usage
  exit 1
fi

# Parse argument.  $1 is the first argument
case $1 in
  "create")
    if [ -f "$filePath" ]; then 
        echo "Error: database already exists"
        exit 1
    fi 

    mkdir -p "$initDir"
    sqlite3 "$filePath" < "$schemaPath"
    # sqlite3 "$filePath" < "$dataPath"
    ;;


  "destroy")
    rm -rf "$filePath" "$initDir"
    ;;

  "reset")
    "$0" destroy
    "$0" create
    ;;

  "dump")
    sqlite3 -batch -line "$filePath" 'SELECT * FROM data'
    ;;
  *)
    usage
    exit 1
    ;;
esac
