import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
G_API_FILE = os.getenv('G_API_FILE')
G_API_EMAIL = os.getenv('G_API_EMAIL')
G_API_LINK = os.getenv('G_API_LINK')
DB_FILE = os.getenv('DB_FILE')
LOG_FILE = os.getenv('LOG_FILE')
REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
MOSCOW_CHANNEL_ID = os.getenv('MOSCOW_CHANNEL_ID')
CENTER_CHANNEL_ID = os.getenv('CENTER_CHANNEL_ID')
NORTH_CHANNEL_ID = os.getenv('NORTH_CHANNEL_ID')
DEFAULT_CHANNEL_ID = os.getenv('DEFAULT_CHANNEL_ID')
ADMIN_ID = os.getenv('ADMIN_ID')
RATE_LIMIT = os.getenv('RATE_LIMIT')
