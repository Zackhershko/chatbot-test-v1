#!/bin/bash

# Start Python FastAPI server using uvicorn with production settings
python -m http.server $PORT &

# Start local web server for index.html on port 5500
# Disabled for production since static files should be served by a CDN/static host
# python -m http.server 5500 &

# Start conversationalRAG server on localhost for internal network access
uvicorn main:app --host 0.0.0.0 --port 10000 &

echo "Servers started:"
echo "http.server server running on port $PORT"
echo "main:app server running on http://localhost:8000"

# Wait for all background processes
wait
