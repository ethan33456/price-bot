# Best Buy Price Bot 🤖

A Python bot that automatically scrapes Best Buy for computers and laptops with **65% or more discount** and notifies you when deals are found.

## Features

- 🔍 **Automated Scraping**: Monitors Best Buy for laptop and desktop computer deals
- 💰 **Deep Discount Detection**: Finds products 65% or more below retail price
- 🔔 **Multiple Notification Methods**: Console alerts and optional email notifications
- 📊 **Deal Tracking**: Prevents duplicate notifications for the same deals
- ⏰ **Scheduled Monitoring**: Runs continuously at configurable intervals
- 📝 **Deal Logging**: Saves all found deals to JSON file for review

## Requirements

- Python 3.7+
- Internet connection
- (Optional) Gmail account for email notifications

## Installation

1. **Clone or download this repository**

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure settings** (optional):
   - Copy `env.example` to `.env`
   - Edit `.env` to customize settings

```bash
cp env.example .env
```

## Configuration

### Basic Settings (in `config.py`)

- `DISCOUNT_THRESHOLD`: Default is 0.35 (35% of retail = 65% off)
- `CHECK_INTERVAL_MINUTES`: How often to check (default: 30 minutes)

### Email Notifications (optional)

To enable email notifications, create a `.env` file:

```env
ENABLE_EMAIL_NOTIFICATIONS=true
EMAIL_FROM=your_email@gmail.com
EMAIL_TO=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

**For Gmail users**: You need to use an "App Password" instead of your regular password:
1. Go to your Google Account settings
2. Enable 2-Factor Authentication
3. Go to Security → App Passwords
4. Generate a new app password for "Mail"
5. Use that password in the `.env` file

## Usage

### Run Continuously (Recommended)

The bot will check for deals every 30 minutes (or your configured interval):

```bash
python bot.py
```

Press `Ctrl+C` to stop the bot.

### Run Once (Test Mode)

To run a single check and exit:

```bash
python bot.py --once
```

This is useful for testing your setup.

## How It Works

1. **Scraping**: The bot visits Best Buy's laptop and desktop computer category pages
2. **Price Analysis**: Extracts current prices and retail prices for each product
3. **Discount Calculation**: Identifies products where current price ≤ 35% of retail price (65%+ discount)
4. **Notification**: Alerts you via console (and email if enabled) when deals are found
5. **Tracking**: Saves deals to `deals_found.json` to avoid duplicate notifications
6. **Scheduling**: Repeats the process at your configured interval

## Output

### Console Notifications

When deals are found, you'll see:

```
================================================================================
🚨 ALERT: 2 DEEP DISCOUNT(S) FOUND!
Time: 2025-11-24 14:30:00
================================================================================

Deal #1:
  Product: HP Pavilion Laptop 15.6" - Intel Core i7
  Current Price: $349.99
  Retail Price: $999.99
  Discount: 65.0%
  Savings: $650.00
  URL: https://www.bestbuy.com/...

================================================================================
```

### Email Notifications

If enabled, you'll receive a formatted HTML email with:
- Deal details with pricing
- Discount percentage highlighted
- Direct links to products
- Professional Best Buy-themed styling

### Deal Log

All found deals are saved to `deals_found.json`:

```json
{
  "deals": [
    {
      "name": "HP Pavilion Laptop...",
      "current_price": 349.99,
      "retail_price": 999.99,
      "discount_percent": 65.0,
      "url": "https://...",
      "found_at": "2025-11-24T14:30:00"
    }
  ],
  "last_updated": "2025-11-24T14:30:00"
}
```

## Customization

### Change Discount Threshold

Edit `config.py`:

```python
# For 70% off or more (30% of retail)
DISCOUNT_THRESHOLD = 0.30

# For 50% off or more (50% of retail)
DISCOUNT_THRESHOLD = 0.50
```

### Change Check Frequency

Edit `.env` or `config.py`:

```env
CHECK_INTERVAL_MINUTES=15  # Check every 15 minutes
```

### Add More Categories

Edit `config.py` and add URLs to `BESTBUY_URLS`:

```python
BESTBUY_URLS = [
    "https://www.bestbuy.com/site/searchpage.jsp?st=laptop...",
    "https://www.bestbuy.com/site/searchpage.jsp?st=desktop...",
    "https://www.bestbuy.com/site/searchpage.jsp?st=gaming+laptop...",  # Add more
]
```

## Troubleshooting

### No products found

- Best Buy may have updated their HTML structure. The scraper uses multiple fallback selectors but may need updates.
- Check your internet connection
- Best Buy may be blocking automated requests (try increasing `CHECK_INTERVAL_MINUTES`)

### Email not sending

- Verify your email credentials in `.env`
- For Gmail, ensure you're using an App Password, not your regular password
- Check that 2FA is enabled on your Google account
- Verify SMTP settings are correct

### Bot crashes

- Check the error message in the console
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Try running with `--once` flag to test: `python bot.py --once`

## Important Notes

⚠️ **Web Scraping Disclaimer**: 
- This bot is for personal use only
- Be respectful of Best Buy's servers (don't set interval too low)
- Best Buy's website structure may change, requiring updates to the scraper
- Always review Best Buy's Terms of Service

⚠️ **Deal Verification**:
- Always verify deals on Best Buy's website before purchasing
- Prices and availability can change rapidly
- Some "retail prices" may be inflated; use your judgment

## Project Structure

```
price-bot/
├── bot.py              # Main bot script
├── scraper.py          # Best Buy web scraper
├── notifier.py         # Notification system
├── storage.py          # Deal tracking/storage
├── config.py           # Configuration settings
├── requirements.txt    # Python dependencies
├── env.example         # Example environment file
├── README.md          # This file
└── deals_found.json   # Generated: stored deals
```

## License

This project is provided as-is for educational and personal use.

## Contributing

Feel free to submit issues or pull requests if you find bugs or want to add features!

---

**Happy deal hunting! 🎉**

