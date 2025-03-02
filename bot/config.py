from decouple import config

BASE_URL = "https://fakultetbistro.herokuapp.com"  # Update for production or hosting  https://mighty-teeth-open.loca.lt
TOKEN = config('TELEGRAM_TOKEN')
ADMIN_GROUP_ID = int(config('ADMIN_GROUP_ID'))  # Replace with your private group chat ID