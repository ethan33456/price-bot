"""
Alternative Selenium-based scraper for Best Buy.
Use this if the regular requests-based scraper gets blocked.

Installation:
    pip install selenium webdriver-manager

Usage:
    from selenium_scraper import SeleniumBestBuyScraper
    scraper = SeleniumBestBuyScraper()
    products = scraper.scrape_all_categories()
"""

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("⚠️  Selenium not installed. Install with: pip install selenium webdriver-manager")

from bs4 import BeautifulSoup
import time
import random
from typing import List, Dict, Optional
import config


class SeleniumBestBuyScraper:
    """
    Selenium-based scraper for Best Buy.
    Uses a real browser, much harder to detect than requests.
    """
    
    def __init__(self, headless: bool = True):
        """
        Initialize Selenium scraper.
        
        Args:
            headless: If True, run browser in background (no window)
        """
        if not SELENIUM_AVAILABLE:
            raise ImportError("Selenium not installed. Run: pip install selenium webdriver-manager")
        
        self.headless = headless
        self.driver = None
    
    def _setup_driver(self):
        """Set up Chrome driver with anti-detection options."""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument('--headless')
        
        # Anti-detection settings
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument(f'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Remove "controlled by automation" banner
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Initialize driver
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Remove webdriver property
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    def scrape_category_page(self, url: str) -> List[Dict]:
        """
        Scrape a Best Buy category page using Selenium.
        
        Args:
            url: The Best Buy category URL to scrape
            
        Returns:
            List of product dictionaries
        """
        if not self.driver:
            self._setup_driver()
        
        products = []
        
        try:
            print(f"🌐 Loading page with Selenium: {url}")
            self.driver.get(url)
            
            # Random human-like delay
            time.sleep(random.uniform(3, 6))
            
            # Wait for products to load
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "sku-item"))
                )
            except:
                print("⚠️  Timeout waiting for products to load")
            
            # Scroll down to load lazy-loaded content
            self._scroll_page()
            
            # Get page source and parse with BeautifulSoup
            soup = BeautifulSoup(self.driver.page_source, 'lxml')
            
            # Extract products (same logic as requests scraper)
            product_items = soup.find_all('li', class_='sku-item')
            
            if not product_items:
                product_items = soup.find_all('div', class_='shop-sku-list-item')
            
            print(f"Found {len(product_items)} products")
            
            for item in product_items:
                try:
                    product = self._extract_product_info(item)
                    if product:
                        products.append(product)
                except Exception as e:
                    print(f"Error extracting product: {e}")
                    continue
            
        except Exception as e:
            print(f"Error scraping with Selenium: {e}")
        
        return products
    
    def _scroll_page(self):
        """Scroll page to trigger lazy loading."""
        try:
            # Scroll down in increments (like a human would)
            total_height = self.driver.execute_script("return document.body.scrollHeight")
            viewport_height = self.driver.execute_script("return window.innerHeight")
            
            current_position = 0
            while current_position < total_height:
                # Scroll by viewport height
                current_position += viewport_height
                self.driver.execute_script(f"window.scrollTo(0, {current_position});")
                time.sleep(random.uniform(0.5, 1.5))
        except Exception as e:
            print(f"Error scrolling: {e}")
    
    def _extract_product_info(self, item) -> Optional[Dict]:
        """Extract product info from BeautifulSoup element."""
        try:
            # Extract product name
            name_elem = item.find('h4', class_='sku-title') or item.find('h4', class_='sku-header')
            if not name_elem:
                name_elem = item.find('a', class_='sku-title')
            
            if not name_elem:
                return None
            
            product_name = name_elem.get_text(strip=True)
            
            # Extract product URL
            link_elem = item.find('a', class_='image-link') or item.find('a', href=True)
            product_url = ''
            if link_elem and link_elem.get('href'):
                href = link_elem['href']
                if href.startswith('http'):
                    product_url = href
                else:
                    product_url = f"https://www.bestbuy.com{href}"
            
            # Extract current price
            current_price = None
            price_elem = item.find('span', {'aria-label': lambda x: x and 'Your price for this item is' in x})
            
            if not price_elem:
                price_elem = item.find('span', class_='priceView-customer-price')
                if not price_elem:
                    price_elem = item.find('span', class_='priceView-hero-price')
            
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                current_price = self._parse_price(price_text)
            
            # Extract retail price
            retail_price = None
            retail_elem = item.find('span', {'aria-label': lambda x: x and 'was' in str(x).lower()})
            
            if not retail_elem:
                retail_elem = item.find('span', class_='pricing-price__regular-price')
                if not retail_elem:
                    retail_elem = item.find('span', class_='priceView-price-was')
            
            if retail_elem:
                retail_text = retail_elem.get_text(strip=True)
                retail_price = self._parse_price(retail_text)
            
            if current_price and not retail_price:
                retail_price = current_price
            
            if product_name and current_price:
                discount_percent = self._calculate_discount_percent(current_price, retail_price)
                return {
                    'name': product_name,
                    'current_price': current_price,
                    'retail_price': retail_price,
                    'url': product_url,
                    'discount_percent': discount_percent
                }
            
        except Exception as e:
            print(f"Error parsing product: {e}")
        
        return None
    
    def _parse_price(self, price_text: str) -> Optional[float]:
        """Parse price from text."""
        try:
            price_clean = price_text.replace('$', '').replace(',', '').strip()
            price_parts = price_clean.split()
            for part in price_parts:
                try:
                    return float(part)
                except ValueError:
                    continue
            return None
        except Exception:
            return None
    
    def _calculate_discount_percent(self, current_price: float, retail_price: Optional[float]) -> float:
        """Calculate discount percentage."""
        if not retail_price or retail_price == 0 or current_price >= retail_price:
            return 0.0
        discount = ((retail_price - current_price) / retail_price) * 100
        return round(discount, 2)
    
    def scrape_all_categories(self) -> List[Dict]:
        """Scrape all configured categories."""
        all_products = []
        
        for url in config.BESTBUY_URLS:
            products = self.scrape_category_page(url)
            all_products.extend(products)
            
            # Random delay between categories
            time.sleep(random.uniform(5, 10))
        
        return all_products
    
    def find_deep_discounts(self, products: List[Dict]) -> List[Dict]:
        """Filter for products with 65%+ discount."""
        deep_discounts = []
        
        for product in products:
            current_price = product.get('current_price', 0)
            retail_price = product.get('retail_price', 0)
            
            if retail_price > 0:
                price_ratio = current_price / retail_price
                
                if price_ratio <= config.DISCOUNT_THRESHOLD:
                    deep_discounts.append(product)
                    print(f"🎯 DEAL FOUND: {product['name']}")
                    print(f"   Current: ${current_price:.2f} | Retail: ${retail_price:.2f}")
                    print(f"   Discount: {product['discount_percent']:.1f}%")
                    print(f"   URL: {product['url']}\n")
        
        return deep_discounts
    
    def close(self):
        """Close the browser."""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def __del__(self):
        """Cleanup on deletion."""
        self.close()


# Example usage
if __name__ == '__main__':
    print("🚀 Testing Selenium scraper...\n")
    
    scraper = SeleniumBestBuyScraper(headless=True)
    
    try:
        products = scraper.scrape_all_categories()
        print(f"\n✅ Found {len(products)} total products")
        
        deals = scraper.find_deep_discounts(products)
        print(f"🎯 Found {len(deals)} deep discounts (65%+ off)")
        
    finally:
        scraper.close()
        print("\n✅ Browser closed")

