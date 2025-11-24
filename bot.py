#!/usr/bin/env python3
"""Main bot script for monitoring Best Buy deals."""
import schedule
import time
from datetime import datetime
import sys
from scraper import BestBuyScraper
from notifier import Notifier
from storage import DealStorage
import config


class PriceBot:
    """Main bot class for monitoring and notifying about deals."""
    
    def __init__(self):
        self.scraper = BestBuyScraper()
        self.notifier = Notifier()
        self.storage = DealStorage()
        self.run_count = 0
    
    def check_for_deals(self) -> None:
        """Main function to check for deals and send notifications."""
        self.run_count += 1
        print(f"\n{'='*80}")
        print(f"🤖 Price Bot Check #{self.run_count}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*80}\n")
        
        try:
            # Scrape Best Buy for products
            print("🔍 Scraping Best Buy for laptops and computers...")
            products = self.scraper.scrape_all_categories()
            print(f"Found {len(products)} total products\n")
            
            # Filter for deep discounts (65% or more off)
            print(f"🎯 Filtering for deals 65% or more off retail...")
            deep_discounts = self.scraper.find_deep_discounts(products)
            
            if deep_discounts:
                print(f"✅ Found {len(deep_discounts)} product(s) with 65%+ discount!\n")
                
                # Filter out deals we've already notified about
                new_deals = self.storage.filter_new_deals(deep_discounts)
                
                if new_deals:
                    print(f"🆕 {len(new_deals)} new deal(s) to notify about!")
                    
                    # Send notifications
                    self.notifier.notify(new_deals)
                    
                    # Save deals to storage
                    self.storage.save_deals(new_deals)
                else:
                    print("ℹ️  All deals have been previously notified. No new notifications sent.")
            else:
                print("❌ No products found with 65%+ discount at this time.\n")
            
            print(f"✅ Check complete. Next check in {config.CHECK_INTERVAL_MINUTES} minutes.\n")
            
        except KeyboardInterrupt:
            raise
        except Exception as e:
            print(f"❌ Error during deal check: {e}\n")
            import traceback
            traceback.print_exc()
    
    def run_once(self) -> None:
        """Run the bot once and exit."""
        print("🚀 Starting Price Bot (single run mode)...\n")
        self.check_for_deals()
        print("✅ Single run complete. Exiting.")
    
    def run_scheduled(self) -> None:
        """Run the bot on a schedule continuously."""
        print("🚀 Starting Price Bot (scheduled mode)...")
        print(f"⏰ Will check every {config.CHECK_INTERVAL_MINUTES} minutes")
        print(f"📧 Email notifications: {'Enabled' if config.ENABLE_EMAIL_NOTIFICATIONS else 'Disabled'}")
        print(f"💾 Deals log: {config.DEALS_LOG_FILE}")
        print("\nPress Ctrl+C to stop the bot.\n")
        
        # Run immediately on start
        self.check_for_deals()
        
        # Schedule periodic checks
        schedule.every(config.CHECK_INTERVAL_MINUTES).minutes.do(self.check_for_deals)
        
        # Keep running
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n🛑 Bot stopped by user. Goodbye!")
            sys.exit(0)


def main():
    """Main entry point."""
    bot = PriceBot()
    
    # Check command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == '--once':
        bot.run_once()
    else:
        bot.run_scheduled()


if __name__ == '__main__':
    main()

