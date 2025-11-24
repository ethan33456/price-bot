"""Configuration settings for the price bot."""
import os
from dotenv import load_dotenv

load_dotenv()

# Best Buy API Key (REQUIRED)
# Get your free key at: https://bestbuyapis.github.io/bby-query-builder/
# Free tier: 50,000 API calls per day
BESTBUY_API_KEY = os.getenv('BESTBUY_API_KEY', '')

# Discount threshold (65% below retail = 35% of original price or less)
DISCOUNT_THRESHOLD = 0.35  # Item must be 35% or less of retail price

# Notification settings
ENABLE_EMAIL_NOTIFICATIONS = os.getenv('ENABLE_EMAIL_NOTIFICATIONS', 'false').lower() == 'true'
EMAIL_FROM = os.getenv('EMAIL_FROM', '')
EMAIL_TO = os.getenv('EMAIL_TO', '')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))

# Bot settings
CHECK_INTERVAL_MINUTES = int(os.getenv('CHECK_INTERVAL_MINUTES', '30'))
MAX_PRODUCTS_PER_CATEGORY = int(os.getenv('MAX_PRODUCTS_PER_CATEGORY', '100'))

# Storage
DEALS_LOG_FILE = 'deals_found.json'

