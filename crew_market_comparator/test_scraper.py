#!/usr/bin/env python3
"""
Test script for individual scrapers
Useful for debugging and testing scrapers in isolation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrapers.polymarket_scraper import PolymarketScraper
from scrapers.kalshi_scraper import KalshiScraper
from scrapers.prediction_market_scraper import PredictionMarketScraper
from scrapers.mock_scraper import MockScraper

def test_scraper(scraper_name):
    """Test a specific scraper"""
    print(f"Testing {scraper_name} scraper...")
    print("=" * 50)
    
    try:
        if scraper_name.lower() == "polymarket":
            scraper = PolymarketScraper()
        elif scraper_name.lower() == "kalshi":
            scraper = KalshiScraper()
        elif scraper_name.lower() == "predictionmarket":
            scraper = PredictionMarketScraper()
        elif scraper_name.lower() == "mock":
            scraper = MockScraper("TestSite")
        else:
            print(f" Unknown scraper: {scraper_name}")
            return
        
        # Test the scraper
        data = scraper.fetch_data()
        
        print(f"\nResults:")
        print(f"   Total items: {len(data)}")
        
        if data:
            print(f"   Sample items:")
            for i, item in enumerate(data[:3]):  # Show first 3 items
                print(f"     {i+1}. {item}")
        else:
            print("   No data returned")
            
    except Exception as e:
        print(f"Error testing {scraper_name}: {e}")
        import traceback
        traceback.print_exc()

def main():
    if len(sys.argv) != 2:
        print("Usage: python test_scraper.py <scraper_name>")
        print("Available scrapers: polymarket, kalshi, predictionmarket, mock")
        print("\nExamples:")
        print("  python test_scraper.py polymarket")
        print("  python test_scraper.py kalshi")
        print("  python test_scraper.py predictionmarket")
        print("  python test_scraper.py mock")
        return
    
    scraper_name = sys.argv[1]
    test_scraper(scraper_name)

if __name__ == "__main__":
    main()
