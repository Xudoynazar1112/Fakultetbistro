from decouple import config

BASE_URL = config('BASE_URL', default="https://fakultetbistro-66a0cec5bbe0.herokuapp.com")
TOKEN = config('TELEGRAM_TOKEN')
ADMIN_GROUP_ID = int(config('ADMIN_GROUP_ID'))  # Replace with your private group chat ID