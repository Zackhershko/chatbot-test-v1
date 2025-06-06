#!/bin/bash

# Start conversationalRAG server on localhost for internal network access
uvicorn main:app --host 0.0.0.0 --port 10000 &

echo "Server started:"
echo "main:app server running on http://localhost:8000"

# Wait for all background processes
wait
