#!/bin/bash

INPUT_FILE=/app/input/${VIDEO_ID}.json

mkdir -p /app/output/ng_pattern/${VIDEO_ID}

python app.py ${VIDEO_ID} ${INPUT_FILE}
