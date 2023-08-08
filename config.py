import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
LOG_FILE = os.getenv('LOG_FILE')
REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
CHANNEL_ID = os.getenv('CHANNEL_ID')
ADMIN_ID = os.getenv('ADMIN_ID')
RATE_LIMIT = os.getenv('RATE_LIMIT')
