#!/bin/bash

# Start Python FastAPI server
python main.py &

# Start local web server for index.html on port 5500
python -m http.server 5500 &

echo "Servers started:"
echo "FastAPI server running on http://localhost:8000"
echo "Web server running on http://localhost:5500"

# Wait for both background processes
wait
