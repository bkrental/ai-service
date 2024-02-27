#!/bin/sh
source ./venv/bin/activate
rasa run --enable-api --cors "*" --debug --credentials credentials.yml