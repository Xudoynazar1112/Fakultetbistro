from decouple import config

BASE_URL = "https://itchy-regions-grow.loca.lt"  # Update for production or hosting
TOKEN = config('TELEGRAM_TOKEN')
ADMIN_GROUP_ID = int(config('ADMIN_GROUP_ID'))  # Replace with your private group chat ID