"""Best Buy web scraper for finding laptop and computer deals."""
import requests
from bs4 import BeautifulSoup
import time
import json
from typing import List, Dict, Optional
import config


class BestBuyScraper:
    """Scraper for Best Buy website to find computer deals."""
    
    def __init__(self):
        self.headers = {
            'User-Agent': config.USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def scrape_category_page(self, url: str) -> List[Dict]:
        """
        Scrape a Best Buy category page for products.
        
        Args:
            url: The Best Buy category URL to scrape
            
        Returns:
            List of product dictionaries with name, current_price, retail_price, url, etc.
        """
        products = []
        
        try:
            print(f"Scraping: {url}")
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Best Buy uses various selectors, we'll try multiple approaches
            # Approach 1: Look for product list items
            product_items = soup.find_all('li', class_='sku-item')
            
            if not product_items:
                # Approach 2: Look for alternative product containers
                product_items = soup.find_all('div', class_='shop-sku-list-item')
            
            print(f"Found {len(product_items)} products on page")
            
            for item in product_items:
                try:
                    product = self._extract_product_info(item)
                    if product:
                        products.append(product)
                except Exception as e:
                    print(f"Error extracting product: {e}")
                    continue
            
            # Add a small delay to be respectful to the server
            time.sleep(2)
            
        except requests.RequestException as e:
            print(f"Error fetching URL {url}: {e}")
        except Exception as e:
            print(f"Unexpected error scraping {url}: {e}")
        
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

