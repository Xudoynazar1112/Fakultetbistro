from decouple import config

BASE_URL = config('BASE_URL', default="https://ec2-13-60-157-193.eu-north-1.compute.amazonaws.com")
TOKEN = config('TELEGRAM_TOKEN')
ADMIN_GROUP_ID = int(config('ADMIN_GROUP_ID'))  # Replace with your private group chat ID
