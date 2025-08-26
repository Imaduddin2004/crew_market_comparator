import argparse
import pandas as pd
import random
import time
import re
from scrapers.mock_scraper import MockScraper
from scrapers.polymarket_scraper import PolymarketScraper
from scrapers.kalshi_scraper import KalshiScraper
from scrapers.prediction_market_scraper import PredictionMarketScraper
from utils.semantic_matcher import SemanticMatcher
from utils.csv_writer import CSVWriter

def search_markets(query, csv_files=None):
    """Search for markets matching a specific query"""
    print(f"Searching for: '{query}'")
    print("=" * 60)
    
    if not csv_files:
        # Find all CSV files in current directory
        import glob
        csv_files = glob.glob("unified_products_*.csv")
        csv_files.sort(reverse=True)  # Most recent first
    
    if not csv_files:
        print("No CSV files found. Run the scraper first with --live flag.")
        return
    
    print(f"Searching in {len(csv_files)} CSV files...")
    
    all_results = []
    query_lower = query.lower()
    
    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file)
            print(f"Searching {csv_file} ({len(df)} markets)...")
            
            # Search in Product column
            matches = df[df['Product'].str.lower().str.contains(query_lower, na=False)]
            
            for _, row in matches.iterrows():
                result = {
                    'file': csv_file,
                    'product': row['Product'],
                    'confidence': row['Confidence'],
                    'total_entries': row.get('Total_Entries', 'N/A'),
                    'kalshi_price': row.get('Kalshi_Price', 'N/A'),
                    'polymarket_price': row.get('Polymarket_Price', 'N/A'),
                    'match_score': calculate_match_score(query, row['Product'])
                }
                all_results.append(result)
                
        except Exception as e:
            print(f"Error reading {csv_file}: {e}")
    
    if not all_results:
        print(f"No markets found matching '{query}'")
        return
    
    # Sort by match score (best matches first)
    all_results.sort(key=lambda x: x['match_score'], reverse=True)
    
    print(f"\nFound {len(all_results)} matching markets:")
    print("=" * 80)
    
    for i, result in enumerate(all_results[:10]):  # Show top 10
        print(f"\n Match {i+1} (Score: {result['match_score']:.2f})")
        print(f" Product: {result['product']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Total Entries: {result['total_entries']}")
        print(f"Kalshi Price: {result['kalshi_price']}")
        print(f"Polymarket Price: {result['polymarket_price']}")
        print(f"Source: {result['file']}")
        print("-" * 40)
    
    if len(all_results) > 10:
        print(f"\n... and {len(all_results) - 10} more matches")
    
    return all_results

def calculate_match_score(query, product_text):
    """Calculate how well a product matches the search query"""
    query_words = set(re.findall(r'\w+', query.lower()))
    product_words = set(re.findall(r'\w+', product_text.lower()))
    
    # Exact word matches
    exact_matches = query_words.intersection(product_words)
    
    # Partial matches (e.g., "bitcoin" matches "Bitcoin")
    partial_matches = sum(1 for qw in query_words 
                         for pw in product_words 
                         if qw in pw or pw in qw)
    
    # Length bonus for longer queries
    length_bonus = len(query_words) * 0.1
    
    score = len(exact_matches) * 2 + partial_matches * 0.5 + length_bonus
    return score

def run_pipeline(use_mock: bool):
    print("Starting prediction market data collection pipeline...")
    print(f"Mode: {'Mock Data' if use_mock else 'Live Scraping'}")
    print("=" * 60)
    
    # Add some randomization to prevent repetitive output
    if not use_mock:
        random.seed(time.time())  # Seed with current time
        print(f"Random seed: {random.randint(1000, 9999)}")
    
    # Step 1: Collect data
    if use_mock:
        print("Using mock data for testing...")
        scrapers = [MockScraper("Polymarket"), MockScraper("Kalshi"), MockScraper("PredictionMarket")]
    else:
        print("Using live scrapers...")
        # Randomize the order of scrapers to get different results
        scrapers = [PolymarketScraper(), KalshiScraper(), PredictionMarketScraper()]
        random.shuffle(scrapers)
        print("Scraper order randomized for variety")

    all_data = []
    successful_scrapers = 0
    
    for i, scraper in enumerate(scrapers):
        print(f"\n{'='*20} Scraper {i+1}/{len(scrapers)} {'='*20}")
        try:
            site_data = scraper.fetch_data()
            if site_data:
                print(f"Data from {scraper.__class__.__name__}: {len(site_data)} items")
                print(f"Sample: {site_data[0] if site_data else 'None'}")
                successful_scrapers += 1
            else:
                print(f"No data returned from {scraper.__class__.__name__}")
            all_data.append(site_data)
        except Exception as e:
            print(f"Error fetching from {scraper.__class__.__name__}: {e}")
            all_data.append([])

    print(f"\n{'='*60}")
    print(f"Total data collected: {len(all_data)} sites, {sum(len(data) for data in all_data)} total items")
    print(f"Successful scrapers: {successful_scrapers}/{len(scrapers)}")
    
    # Check if we have any data to process
    total_items = sum(len(data) for data in all_data)
    if total_items == 0:
        print("No data collected from any scraper!")
        if not use_mock:
            print("Consider running with --mock flag to test with sample data")
            print("Check if websites are accessible and scrapers are working")
        return
    
    # Step 2: Semantic product unification
    print(f"\nStarting semantic product unification...")
    matcher = SemanticMatcher()
    unified_products = matcher.unify(all_data)
    
    print(f"Unified products: {len(unified_products)} groups")

    # Step 3: Export to CSV with timestamp
    print(f"\nExporting to CSV...")
    timestamp = int(time.time())
    filename = f"unified_products_{timestamp}.csv"
    writer = CSVWriter(filename)
    writer.write(unified_products)

    print("Unified product board generated: " + filename)
    print(f"File location: {writer.filename}")
    print(f"Total unified products: {len(unified_products)}")
    print(f"Timestamp: {timestamp}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prediction Market Data Collection Pipeline")
    parser.add_argument("--mock", action="store_true", help="Run with mock data instead of live scraping")
    parser.add_argument("--live", action="store_true", help="Run with live data scraping")
    parser.add_argument("--search", type=str, help="Search for specific markets (e.g., 'bitcoin price')")
    args = parser.parse_args()

    if args.search:
        # Search mode
        search_markets(args.search)
    elif not args.mock and not args.live:
        # Default to mock if no arguments provided
        print("No mode specified. Use --mock for testing, --live for production, or --search to find markets.")
        print("Running with mock data for safety...")
        args.mock = True
        run_pipeline(use_mock=args.mock)
    else:
        # Normal pipeline mode
        run_pipeline(use_mock=args.mock)
