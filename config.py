"""Configuration settings for the price bot."""
import os
from dotenv import load_dotenv

load_dotenv()

# Discount threshold (65% below retail = 35% of original price or less)
DISCOUNT_THRESHOLD = 0.35  # Item must be 35% or less of retail price

# Best Buy URLs - Using simpler category pages
BESTBUY_URLS = [
    # Laptop deals page (more likely to have actual deals)
    "https://www.bestbuy.com/site/laptop-computers/all-laptops/pcmcat138500050001.c?id=pcmcat138500050001",
    # Desktop computers page
    "https://www.bestbuy.com/site/computers-pcs/desktop-computers/abcat0501000.c?id=abcat0501000",
    # Deal of the day (often has good discounts)
    "https://www.bestbuy.com/site/electronics/top-deals/pcmcat1563299784494.c?id=pcmcat1563299784494",
]

# Alternative: simpler search URLs (uncomment to use instead)
# BESTBUY_URLS = [
#     "https://www.bestbuy.com/site/searchpage.jsp?st=laptop",
#     "https://www.bestbuy.com/site/searchpage.jsp?st=desktop+computer",
# ]

# Notification settings
ENABLE_EMAIL_NOTIFICATIONS = os.getenv('ENABLE_EMAIL_NOTIFICATIONS', 'false').lower() == 'true'
EMAIL_FROM = os.getenv('EMAIL_FROM', '')
EMAIL_TO = os.getenv('EMAIL_TO', '')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))

# Scraping settings
CHECK_INTERVAL_MINUTES = int(os.getenv('CHECK_INTERVAL_MINUTES', '30'))
RETRY_ATTEMPTS = int(os.getenv('RETRY_ATTEMPTS', '3'))
REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '30'))
MIN_DELAY_SECONDS = int(os.getenv('MIN_DELAY_SECONDS', '2'))
MAX_DELAY_SECONDS = int(os.getenv('MAX_DELAY_SECONDS', '5'))

# Storage
DEALS_LOG_FILE = 'deals_found.json'

