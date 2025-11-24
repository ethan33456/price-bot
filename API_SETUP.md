# Best Buy API Setup Guide

## Why Use the API Instead of Web Scraping?

The Best Buy Official API is **vastly superior** to web scraping:

| Feature | Web Scraping | Official API |
|---------|-------------|--------------|
| **Reliability** | ❌ Gets blocked frequently | ✅ Always works |
| **Speed** | ❌ Slow (needs HTML parsing) | ✅ Fast (direct data) |
| **Maintenance** | ❌ Breaks when site changes | ✅ Stable interface |
| **Legal** | ⚠️ Gray area | ✅ Officially sanctioned |
| **Rate Limits** | ❌ Unknown, gets blocked | ✅ Clear: 50,000/day (free) |
| **Data Quality** | ⚠️ May be incomplete | ✅ Complete & accurate |
| **Cost** | Free | ✅ **FREE** (up to 50k calls/day) |

## Getting Your FREE API Key

### Step 1: Visit the API Portal

Go to: **https://bestbuyapis.github.io/bby-query-builder/**

### Step 2: Sign Up

1. Click "**Sign up for a Best Buy API Key**" in the top navigation
2. You'll be taken to: https://developer.bestbuy.com/
3. Click "**Get a Key**" or "**Sign Up**"

### Step 3: Complete Registration

Fill out the registration form:
- **Name**: Your name
- **Email**: Your email address
- **Company** (optional): Can leave blank or put "Personal Project"
- **Website** (optional): Not required
- **Description**: "Personal price monitoring tool" or similar

### Step 4: Get Your Key

- After registration, you'll receive your API key immediately
- Copy the API key (it looks like: `abcdefgh12345678`)

### Step 5: Add to Your Bot

1. Open your `.env` file in the price-bot directory
2. Add your API key:

```env
BESTBUY_API_KEY=your_actual_api_key_here
USE_API=true
```

3. Save the file

### Step 6: Test It

```bash
# Test the API scraper
python3 api_scraper.py

# Or run the full bot
python3 bot.py --once
```

You should see: `🔑 Using Best Buy Official API (recommended)`

## API Rate Limits

### Free Tier (Perfect for This Bot!)

- **50,000 requests per day**
- **5 requests per second**

### How Many Calls Does This Bot Use?

- Each check = 2-3 API calls (laptops + desktops)
- Checking every 30 minutes = 48 checks/day = ~100-150 calls/day
- **You're well within the free limit!** ✅

## What Data Does the API Provide?

The Products API gives you:

- ✅ Product name and SKU
- ✅ Current sale price (`salePrice`)
- ✅ Regular retail price (`regularPrice`)
- ✅ Direct product URL
- ✅ Product images
- ✅ Category information
- ✅ Whether item is on sale
- ✅ Much more...

## API Documentation

Full documentation: https://bestbuyapis.github.io/api-documentation/

Key endpoints this bot uses:

### Products API

```
GET https://api.bestbuy.com/v1/products(search=laptop)?apiKey=YOUR_KEY&format=json
```

**Query Parameters:**
- `search` - Search term (laptop, desktop computer, etc.)
- `show` - Which attributes to return
- `sort` - Sort order (e.g., `salePrice.asc`)
- `pageSize` - Results per page (max 100)
- `format` - Response format (json or xml)

**Example Response:**
```json
{
  "products": [
    {
      "sku": 6534009,
      "name": "HP - 15.6\" Laptop - AMD Ryzen 5",
      "salePrice": 479.99,
      "regularPrice": 679.99,
      "onSale": true,
      "url": "https://www.bestbuy.com/site/..."
    }
  ]
}
```

## Switching Between API and Web Scraping

The bot automatically uses the API if you have a key configured. To switch:

### Use API (Recommended):
```env
USE_API=true
BESTBUY_API_KEY=your_key_here
```

### Use Web Scraping (Not Recommended):
```env
USE_API=false
# or just don't set BESTBUY_API_KEY
```

## Troubleshooting

### "API Key Required" Error

**Problem:** Bot says API key is missing

**Solution:** 
1. Make sure you copied your API key correctly
2. Verify `.env` file has: `BESTBUY_API_KEY=your_key`
3. No spaces around the `=` sign
4. No quotes around the key

### "Invalid API Key" Error

**Problem:** API returns 403 or 401 error

**Solution:**
1. Check your API key is correct
2. Make sure your key is active (check Best Buy developer portal)
3. Verify you haven't exceeded rate limits

### No Results Found

**Problem:** API returns 0 products

**Solution:**
1. This may be normal - there might not be any 65%+ discounts right now
2. Lower the discount threshold in `config.py` to see more results
3. Try searching manually: https://www.bestbuy.com/

## Advanced: Custom API Queries

You can modify `api_scraper.py` to customize searches:

```python
# Search for specific brands
query = '(search=laptop&manufacturer=apple)'

# Search for price range
query = '(salePrice<500&salePrice>200)'

# Search for items on sale only
query = '(search=laptop&onSale=true)'

# Combine conditions
query = '(search=laptop&onSale=true&salePrice<500)'
```

## Support

- **Best Buy API Documentation**: https://bestbuyapis.github.io/api-documentation/
- **Developer Portal**: https://developer.bestbuy.com/
- **API Status**: Check Best Buy's developer site for any outages

---

**Bottom Line**: Get the free API key - it's 1000x better than web scraping! 🚀

