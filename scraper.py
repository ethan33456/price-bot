"""Best Buy web scraper for finding laptop and computer deals."""
import requests
from bs4 import BeautifulSoup
import time
import json
import random
from typing import List, Dict, Optional
import config


class BestBuyScraper:
    """Scraper for Best Buy website to find computer deals."""
    
    def __init__(self):
        # Rotate through multiple realistic user agents
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        self.session = requests.Session()
        self._update_headers()
    
    def _update_headers(self):
        """Update session headers with a random user agent."""
        self.session.headers.update({
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        })
    
    def scrape_category_page(self, url: str, retry_count: int = 3) -> List[Dict]:
        """
        Scrape a Best Buy category page for products with retry logic.
        
        Args:
            url: The Best Buy category URL to scrape
            retry_count: Number of retries on failure
            
        Returns:
            List of product dictionaries with name, current_price, retail_price, url, etc.
        """
        products = []
        
        for attempt in range(retry_count):
            try:
                if attempt > 0:
                    # Exponential backoff: wait longer between retries
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    print(f"Retry attempt {attempt + 1}/{retry_count}, waiting {wait_time:.1f}s...")
                    time.sleep(wait_time)
                    # Update headers with new user agent for retry
                    self._update_headers()
                
                print(f"Scraping: {url}")
                
                # Add random delay before request (2-5 seconds)
                time.sleep(random.uniform(2, 5))
                
                response = self.session.get(url, timeout=30, allow_redirects=True)
                response.raise_for_status()
                
                # Check if we got blocked (common block pages)
                if 'blocked' in response.text.lower() or len(response.content) < 1000:
                    print(f"⚠️  Possible block detected (response too small: {len(response.content)} bytes)")
                    if attempt < retry_count - 1:
                        continue
                    else:
                        print("❌ All retry attempts exhausted")
                        return products
                
                soup = BeautifulSoup(response.content, 'lxml')
                
                # Best Buy uses various selectors, we'll try multiple approaches
                # Approach 1: Look for product list items
                product_items = soup.find_all('li', class_='sku-item')
                
                if not product_items:
                    # Approach 2: Look for alternative product containers
                    product_items = soup.find_all('div', class_='shop-sku-list-item')
                
                if not product_items:
                    # Approach 3: Try JSON data embedded in page
                    script_tags = soup.find_all('script', type='application/ld+json')
                    for script in script_tags:
                        try:
                            data = json.loads(script.string)
                            if isinstance(data, dict) and 'itemListElement' in data:
                                products.extend(self._extract_from_json(data))
                        except:
                            continue
                
                print(f"Found {len(product_items)} products on page")
                
                for item in product_items:
                    try:
                        product = self._extract_product_info(item)
                        if product:
                            products.append(product)
                    except Exception as e:
                        print(f"Error extracting product: {e}")
                        continue
                
                # Success - break out of retry loop
                break
                
            except requests.exceptions.Timeout as e:
                print(f"⏱️  Timeout on attempt {attempt + 1}/{retry_count}: {e}")
                if attempt == retry_count - 1:
                    print(f"❌ Failed after {retry_count} attempts")
            except requests.RequestException as e:
                print(f"🚫 Request error on attempt {attempt + 1}/{retry_count}: {e}")
                if attempt == retry_count - 1:
                    print(f"❌ Failed after {retry_count} attempts")
            except Exception as e:
                print(f"Unexpected error scraping {url}: {e}")
                break
        
        return products
    
    def _extract_product_info(self, item) -> Optional[Dict]:
        """
        Extract product information from a product item element.
        
        Args:
            item: BeautifulSoup element containing product information
            
        Returns:
            Dictionary with product details or None if extraction fails
        """
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
            
            # Extract current price (sale price)
            current_price = None
            price_elem = item.find('span', {'aria-label': lambda x: x and 'Your price for this item is' in x})
            
            if not price_elem:
                # Try alternative price selectors
                price_elem = item.find('span', class_='priceView-customer-price')
                if not price_elem:
                    price_elem = item.find('span', class_='priceView-hero-price')
            
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                current_price = self._parse_price(price_text)
            
            # Extract retail price (original price)
            retail_price = None
            retail_elem = item.find('span', {'aria-label': lambda x: x and 'was' in str(x).lower()})
            
            if not retail_elem:
                # Try alternative retail price selectors
                retail_elem = item.find('span', class_='pricing-price__regular-price')
                if not retail_elem:
                    retail_elem = item.find('span', class_='priceView-price-was')
            
            if retail_elem:
                retail_text = retail_elem.get_text(strip=True)
                retail_price = self._parse_price(retail_text)
            
            # If we have a current price but no retail price, use current price as retail
            if current_price and not retail_price:
                retail_price = current_price
            
            # Only return if we have at least name and price
            if product_name and current_price:
                return {
                    'name': product_name,
                    'current_price': current_price,
                    'retail_price': retail_price,
                    'url': product_url,
                    'discount_percent': self._calculate_discount_percent(current_price, retail_price)
                }
            
        except Exception as e:
            print(f"Error parsing product item: {e}")
        
        return None
    
    def _parse_price(self, price_text: str) -> Optional[float]:
        """
        Parse price from text string.
        
        Args:
            price_text: String containing price (e.g., "$1,299.99")
            
        Returns:
            Float price or None if parsing fails
        """
        try:
            # Remove dollar signs, commas, and other non-numeric characters
            price_clean = price_text.replace('$', '').replace(',', '').strip()
            # Extract first number (handles cases like "$999.99 was $1,299.99")
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
        """
        Calculate discount percentage.
        
        Args:
            current_price: Current sale price
            retail_price: Original retail price
            
        Returns:
            Discount percentage (0-100)
        """
        if not retail_price or retail_price == 0 or current_price >= retail_price:
            return 0.0
        
        discount = ((retail_price - current_price) / retail_price) * 100
        return round(discount, 2)
    
    def _extract_from_json(self, data: Dict) -> List[Dict]:
        """
        Extract product data from JSON-LD structured data.
        
        Args:
            data: JSON-LD data dictionary
            
        Returns:
            List of product dictionaries
        """
        products = []
        try:
            if 'itemListElement' in data:
                for item in data['itemListElement']:
                    if isinstance(item, dict) and 'item' in item:
                        product_data = item['item']
                        product = {
                            'name': product_data.get('name', ''),
                            'url': product_data.get('url', ''),
                            'current_price': 0,
                            'retail_price': 0,
                            'discount_percent': 0
                        }
                        
                        # Extract price info
                        if 'offers' in product_data:
                            offers = product_data['offers']
                            if isinstance(offers, dict):
                                price = offers.get('price', 0)
                                try:
                                    product['current_price'] = float(price)
                                    product['retail_price'] = float(price)
                                except:
                                    pass
                        
                        if product['name'] and product['current_price'] > 0:
                            products.append(product)
        except Exception as e:
            print(f"Error extracting from JSON: {e}")
        
        return products
    
    def scrape_all_categories(self) -> List[Dict]:
        """
        Scrape all configured Best Buy category URLs.
        
        Returns:
            List of all products found across all categories
        """
        all_products = []
        
        for url in config.BESTBUY_URLS:
            products = self.scrape_category_page(url)
            all_products.extend(products)
        
        return all_products
    
    def find_deep_discounts(self, products: List[Dict]) -> List[Dict]:
        """
        Filter products to find those with 65% or more discount.
        
        Args:
            products: List of product dictionaries
            
        Returns:
            List of products meeting the discount threshold
        """
        deep_discounts = []
        
        for product in products:
            current_price = product.get('current_price', 0)
            retail_price = product.get('retail_price', 0)
            
            if retail_price > 0:
                # Calculate what percentage of retail the current price is
                price_ratio = current_price / retail_price
                
                # If current price is 35% or less of retail (65%+ discount)
                if price_ratio <= config.DISCOUNT_THRESHOLD:
                    deep_discounts.append(product)
                    print(f"🎯 DEAL FOUND: {product['name']}")
                    print(f"   Current: ${current_price:.2f} | Retail: ${retail_price:.2f}")
                    print(f"   Discount: {product['discount_percent']:.1f}%")
                    print(f"   URL: {product['url']}\n")
        
        return deep_discounts

