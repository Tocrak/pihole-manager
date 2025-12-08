#!/bin/sh

while true; do
    echo "Starting service..."
    uvicorn app:app --host 0.0.0.0 --port 8100 --no-access-log
done
