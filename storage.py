"""Storage module for tracking deals found."""
import json
import os
from typing import List, Dict, Set
from datetime import datetime
import config


class DealStorage:
    """Manage storage of deals to avoid duplicate notifications."""
    
    def __init__(self, filepath: str = None):
        self.filepath = filepath or config.DEALS_LOG_FILE
        self.deals_cache: Set[str] = set()
        self._load_cache()
    
    def _load_cache(self) -> None:
        """Load previously found deals from file."""
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r') as f:
                    data = json.load(f)
                    # Create cache of deal identifiers
                    for deal in data.get('deals', []):
                        deal_id = self._create_deal_id(deal)
                        self.deals_cache.add(deal_id)
            except Exception as e:
                print(f"Error loading deals cache: {e}")
    
    def _create_deal_id(self, deal: Dict) -> str:
        """
        Create unique identifier for a deal.
        
        Args:
            deal: Deal dictionary
            
        Returns:
            Unique string identifier
        """
        # Use product name and current price as identifier
        name = deal.get('name', '').strip()
        price = deal.get('current_price', 0)
        return f"{name}|{price:.2f}"
    
    def is_new_deal(self, deal: Dict) -> bool:
        """
        Check if a deal is new (not previously notified).
        
        Args:
            deal: Deal dictionary
            
        Returns:
            True if deal is new, False if already seen
        """
        deal_id = self._create_deal_id(deal)
        return deal_id not in self.deals_cache
    
    def filter_new_deals(self, deals: List[Dict]) -> List[Dict]:
        """
        Filter list of deals to only new ones.
        
        Args:
            deals: List of deal dictionaries
            
        Returns:
            List of only new deals
        """
        return [deal for deal in deals if self.is_new_deal(deal)]
    
    def save_deals(self, deals: List[Dict]) -> None:
        """
        Save deals to storage file.
        
        Args:
            deals: List of deal dictionaries to save
        """
        if not deals:
            return
        
        # Load existing data
        existing_data = {'deals': [], 'last_updated': None}
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r') as f:
                    existing_data = json.load(f)
            except Exception as e:
                print(f"Error loading existing deals: {e}")
        
        # Add new deals with timestamp
        for deal in deals:
            deal_with_timestamp = deal.copy()
            deal_with_timestamp['found_at'] = datetime.now().isoformat()
            existing_data['deals'].append(deal_with_timestamp)
            
            # Update cache
            deal_id = self._create_deal_id(deal)
            self.deals_cache.add(deal_id)
        
        existing_data['last_updated'] = datetime.now().isoformat()
        
        # Save to file
        try:
            with open(self.filepath, 'w') as f:
                json.dump(existing_data, f, indent=2)
            print(f"Saved {len(deals)} deal(s) to {self.filepath}")
        except Exception as e:
            print(f"Error saving deals: {e}")
    
    def get_all_deals(self) -> List[Dict]:
        """
        Get all deals from storage.
        
        Returns:
            List of all stored deals
        """
        if not os.path.exists(self.filepath):
            return []
        
        try:
            with open(self.filepath, 'r') as f:
                data = json.load(f)
                return data.get('deals', [])
        except Exception as e:
            print(f"Error reading deals: {e}")
            return []

