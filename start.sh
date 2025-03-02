#!/bin/bash
if [ -n "$DB_HOST" ]; then
    python manage.py migrate
fi
# Run Django server with Gunicorn on Heroku's dynamic port
gunicorn --bind 0.0.0.0:${PORT} config.wsgi:application &
# Run Telegram bot
python manage.py runbot &
wait