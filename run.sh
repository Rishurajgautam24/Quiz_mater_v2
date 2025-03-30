#!/bin/bash

# Get the absolute path of the project directory
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Function to open new terminal with command
open_terminal_with_command() {
    osascript -e "tell application \"Terminal\"
        do script \"cd $PROJECT_DIR && $1\"
        activate
    end tell"
}

# Start Redis server in a new terminal
open_terminal_with_command "conda activate app_dev && redis-server"
sleep 2  # Wait for Redis to start

# Start Flask application in a new terminal
open_terminal_with_command "conda activate app_dev && python main.py"
sleep 2  # Wait for Flask to start

# Start Celery worker in a new terminal
open_terminal_with_command "conda activate app_dev && celery -A make_celery:celery_app worker --loglevel=INFO"
sleep 2  # Wait for Flask to start

# Start Celery worker in a new terminal
open_terminal_with_command "conda activate app_dev && celery -A make_celery:celery_app beat --loglevel=INFO"
sleep 2  # Wait for Flask to start

open_terminal_with_command "conda activate app_dev && mailhog"


echo "All services started in separate terminals!"
