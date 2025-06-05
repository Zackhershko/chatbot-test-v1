#!/bin/bash

# Start Python FastAPI server using uvicorn with production settings
uvicorn main:app --host 0.0.0.0 --port $PORT --workers 4 &

# Start local web server for index.html on port 5500
# Disabled for production since static files should be served by a CDN/static host
# python -m http.server 5500 &

echo "Server started:"
echo "FastAPI server running on port $PORT"

# Wait for the FastAPI server process
wait
