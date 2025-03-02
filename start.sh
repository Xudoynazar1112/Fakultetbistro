#!/bin/bash

# Run Django server in the background
python manage.py runserver 0.0.0.0:${PORT} &

# Run Telegram bot
python manage.py runbot &

# Keep container running
wait