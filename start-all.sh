#!/bin/bash

# Start main application
echo "Starting main application on port 3001..."
cd frontend
npm start &
MAIN_PID=$!

# Setup trap to kill the process when script is terminated
trap "kill $MAIN_PID; exit" SIGINT SIGTERM

# Wait for process
wait 