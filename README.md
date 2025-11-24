# Best Buy Price Bot 🤖

A Python bot that uses the **official Best Buy API** to monitor computers and laptops with **65% or more discount** and notifies you when deals are found.

## Features

- 🔑 **Official Best Buy API**: Uses Best Buy's official API (no blocking, no scraping issues!)
- 🆓 **Free**: 50,000 API calls per day on free tier (you'll use ~100-150/day)
- 💰 **Deep Discount Detection**: Finds products 65% or more below retail price
- 🔔 **Multiple Notification Methods**: Console alerts and optional email notifications
- 📊 **Deal Tracking**: Prevents duplicate notifications for the same deals
- ⏰ **Scheduled Monitoring**: Runs continuously at configurable intervals
- 📝 **Deal Logging**: Saves all found deals to JSON file for review
- ⚡ **Fast & Reliable**: Direct API access, no HTML parsing

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

3. **Get a FREE Best Buy API Key** (highly recommended):
   - Visit https://bestbuyapis.github.io/bby-query-builder/
   - Click "Sign up for a Best Buy API Key"
   - Complete the registration (takes 2 minutes)
   - Copy your API key

4. **Configure settings**:
   - Copy `env.example` to `.env`
   - Add your Best Buy API key to `.env`

```bash
cp env.example .env
# Edit .env and add: BESTBUY_API_KEY=your_actual_key_here
```

**Important:** This bot requires a Best Buy API key. The API is free and much better than web scraping:
- ✅ No blocking issues
- ✅ Fast and reliable
- ✅ 50,000 calls/day free
- ✅ Officially supported
- ✅ Never breaks

## Configuration

### Basic Settings

Edit your `.env` file to customize:

- `DISCOUNT_THRESHOLD`: Default is 0.35 (35% of retail = 65% off) - edit in `config.py`
- `CHECK_INTERVAL_MINUTES`: How often to check (default: 30 minutes)
- `MAX_PRODUCTS_PER_CATEGORY`: Max products to check per category (default: 100)

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
python3 bot.py
```

Press `Ctrl+C` to stop the bot.

**Note:** Use `python3` not `python` (which may point to Python 2.7 on your system)

### Run Once (Test Mode)

To run a single check and exit:

```bash
python3 bot.py --once
```

This is useful for testing your setup.

## How It Works

1. **API Query**: Uses Best Buy's official Products API to search for laptops and desktops
2. **Price Analysis**: Gets current sale prices and regular prices directly from Best Buy's database
3. **Discount Calculation**: Identifies products where current price ≤ 35% of retail price (65%+ discount)
4. **Notification**: Alerts you via console (and email if enabled) when deals are found
5. **Tracking**: Saves deals to `deals_found.json` to avoid duplicate notifications
6. **Scheduling**: Repeats the process at your configured interval

**Why API?** No blocking, fast, reliable, and completely free (50,000 calls/day)!

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

Edit `.env`:

```env
CHECK_INTERVAL_MINUTES=15  # Check every 15 minutes
CHECK_INTERVAL_MINUTES=60  # Check once per hour
```

### Search More Products

Edit `.env`:

```env
MAX_PRODUCTS_PER_CATEGORY=200  # Check 200 laptops and 200 desktops
```

## Troubleshooting

### "API Key Required" Error

- Get your free API key at: https://bestbuyapis.github.io/bby-query-builder/
- Add it to `.env`: `BESTBUY_API_KEY=your_key_here`
- See `API_SETUP.md` for detailed instructions

### No products found

- This is normal if there aren't any 65%+ discounts currently
- Try lowering the discount threshold in `config.py` to see more deals
- Verify your API key is correct in `.env`
- Check you haven't exceeded rate limits (50,000 calls/day - very unlikely)

### Email not sending

- Verify your email credentials in `.env`
- For Gmail, ensure you're using an App Password, not your regular password
- Check that 2FA is enabled on your Google account
- Verify SMTP settings are correct

### Bot crashes

- Check the error message in the console
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Verify your API key is set in `.env`
- Try running with `--once` flag to test: `python3 bot.py --once`
- Make sure you're using `python3` not `python` (Python 2.7 won't work)

## Important Notes

⚠️ **API Usage**: 
- This bot uses Best Buy's official API (free and legal!)
- Free tier: 50,000 API calls per day
- Each check uses 2-3 API calls (well within limits)
- API Terms: https://developer.bestbuy.com/

⚠️ **Deal Verification**:
- Always verify deals on Best Buy's website before purchasing
- Prices and availability can change rapidly
- Some "retail prices" may be inflated; use your judgment

## Project Structure

```
price-bot/
├── bot.py              # Main bot script
├── api_scraper.py      # Best Buy API client
├── notifier.py         # Notification system
├── storage.py          # Deal tracking/storage
├── config.py           # Configuration settings
├── requirements.txt    # Python dependencies
├── env.example         # Example environment file
├── API_SETUP.md        # API key setup guide
├── README.md           # This file
└── deals_found.json    # Generated: stored deals
```

## License

This project is provided as-is for educational and personal use.

## Contributing

Feel free to submit issues or pull requests if you find bugs or want to add features!

---

**Happy deal hunting! 🎉**

