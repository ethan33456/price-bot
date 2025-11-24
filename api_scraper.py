"""
Best Buy API-based scraper - Much more reliable than web scraping!

Get your free API key at: https://bestbuyapis.github.io/bby-query-builder/
Free tier: 50,000 calls per day
"""

import requests
import time
from typing import List, Dict, Optional
import config


class BestBuyAPIScraper:
    """
    Official Best Buy API scraper.
    Much more reliable than web scraping - no blocking issues!
    """
    
    def __init__(self, api_key: str):
        """
        Initialize API scraper.
        
        Args:
            api_key: Your Best Buy API key from https://bestbuyapis.github.io/
        """
        if not api_key or api_key == 'YOUR_API_KEY_HERE':
            raise ValueError(
                "Best Buy API key required!\n"
                "Get your free key at: https://bestbuyapis.github.io/bby-query-builder/\n"
                "Then add it to your .env file: BESTBUY_API_KEY=your_key_here"
            )
        
        self.api_key = api_key
        self.base_url = "https://api.bestbuy.com/v1"
        self.session = requests.Session()
    
    def search_products(self, category: str, page: int = 1, page_size: int = 100) -> List[Dict]:
        """
        Search for products in a category.
        
        Args:
            category: Category to search (e.g., "laptop", "desktop computer")
            page: Page number (default: 1)
            page_size: Items per page, max 100 (default: 100)
            
        Returns:
            List of product dictionaries
        """
        # Build the search query
        # Search for active products with prices in the specified category
        query = f'(search={category}&active=true&salePrice>0)'
        
        # Build the API URL
        url = f"{self.base_url}/products{query}"
        
        params = {
            'apiKey': self.api_key,
            'format': 'json',
            'show': 'sku,name,salePrice,regularPrice,onSale,url,image,categoryPath.name',
            'pageSize': min(page_size, 100),  # API max is 100
            'page': page,
            'sort': 'salePrice.asc'  # Sort by price ascending
        }
        
        try:
            print(f"🔍 Searching Best Buy API for: {category} (page {page})")
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            products = []
            for item in data.get('products', []):
                product = self._parse_product(item)
                if product:
                    products.append(product)
            
            total = data.get('total', 0)
            print(f"✅ Found {len(products)} products on this page ({total} total matches)")
            
            return products
            
        except requests.RequestException as e:
            print(f"❌ API request error: {e}")
            return []
        except Exception as e:
            print(f"❌ Error parsing API response: {e}")
            return []
    
    def search_laptops(self, max_results: int = 100) -> List[Dict]:
        """
        Search for laptop deals.
        
        Args:
            max_results: Maximum number of results to return (default: 100)
            
        Returns:
            List of product dictionaries
        """
        all_products = []
        page = 1
        page_size = min(max_results, 100)
        
        while len(all_products) < max_results:
            products = self.search_products("laptop", page=page, page_size=page_size)
            
            if not products:
                break
            
            all_products.extend(products)
            
            # Stop if we've gotten enough or if this page wasn't full
            if len(products) < page_size or len(all_products) >= max_results:
                break
            
            page += 1
            time.sleep(0.5)  # Be nice to the API
        
        return all_products[:max_results]
    
    def search_desktops(self, max_results: int = 100) -> List[Dict]:
        """
        Search for desktop computer deals.
        
        Args:
            max_results: Maximum number of results to return (default: 100)
            
        Returns:
            List of product dictionaries
        """
        all_products = []
        page = 1
        page_size = min(max_results, 100)
        
        while len(all_products) < max_results:
            products = self.search_products("desktop computer", page=page, page_size=page_size)
            
            if not products:
                break
            
            all_products.extend(products)
            
            if len(products) < page_size or len(all_products) >= max_results:
                break
            
            page += 1
            time.sleep(0.5)
        
        return all_products[:max_results]
    
    def _parse_product(self, item: Dict) -> Optional[Dict]:
        """
        Parse product data from API response.
        
        Args:
            item: Product dictionary from API
            
        Returns:
            Standardized product dictionary
        """
        try:
            sku = item.get('sku')
            name = item.get('name', '')
            sale_price = float(item.get('salePrice', 0))
            regular_price = float(item.get('regularPrice', 0))
            url = item.get('url', '')
            
            # If no regular price, use sale price
            if regular_price == 0:
                regular_price = sale_price
            
            # Calculate discount
            discount_percent = 0.0
            if regular_price > 0 and sale_price < regular_price:
                discount_percent = ((regular_price - sale_price) / regular_price) * 100
            
            return {
                'sku': sku,
                'name': name,
                'current_price': sale_price,
                'retail_price': regular_price,
                'url': url,
                'discount_percent': round(discount_percent, 2),
                'on_sale': item.get('onSale', False)
            }
            
        except Exception as e:
            print(f"Error parsing product: {e}")
            return None
    
    def scrape_all_categories(self, max_per_category: int = 100) -> List[Dict]:
        """
        Search all configured categories.
        
        Args:
            max_per_category: Max results per category (default: 100)
            
        Returns:
            List of all products found
        """
        all_products = []
        
        print("📱 Searching for laptops...")
        laptops = self.search_laptops(max_results=max_per_category)
        all_products.extend(laptops)
        
        print("\n🖥️  Searching for desktop computers...")
        desktops = self.search_desktops(max_results=max_per_category)
        all_products.extend(desktops)
        
        print(f"\n✅ Total products found: {len(all_products)}")
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
                    print(f"   SKU: {product['sku']}")
                    print(f"   Current: ${current_price:.2f} | Retail: ${retail_price:.2f}")
                    print(f"   Discount: {product['discount_percent']:.1f}%")
                    print(f"   URL: {product['url']}\n")
        
        return deep_discounts


# Example usage and testing
if __name__ == '__main__':
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    api_key = os.getenv('BESTBUY_API_KEY', '')
    
    if not api_key or api_key == 'YOUR_API_KEY_HERE':
        print("="*80)
        print("❌ Best Buy API Key Required!")
        print("="*80)
        print("\n1. Get your FREE API key at:")
        print("   https://bestbuyapis.github.io/bby-query-builder/\n")
        print("2. Add it to your .env file:")
        print("   BESTBUY_API_KEY=your_key_here\n")
        print("3. Run this script again\n")
        print("="*80)
    else:
        print("🚀 Testing Best Buy API Scraper...\n")
        
        scraper = BestBuyAPIScraper(api_key)
        
        # Search for laptops on sale
        products = scraper.scrape_all_categories(max_per_category=50)
        
        # Find deep discounts
        deals = scraper.find_deep_discounts(products)
        
        print(f"\n{'='*80}")
        print(f"📊 Results Summary:")
        print(f"   Total products searched: {len(products)}")
        print(f"   Deep discounts found (65%+ off): {len(deals)}")
        print(f"{'='*80}\n")

