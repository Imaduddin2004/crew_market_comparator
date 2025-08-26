#!/usr/bin/env python3
"""
Search script for finding specific prediction markets
Usage: python search_markets.py "bitcoin price"
"""

import sys
import pandas as pd
import glob
import re

def search_markets(query):
    """Search for markets matching a specific query"""
    print(f"Searching for: '{query}'")
    print("=" * 60)
    
    # Find all CSV files in current directory
    csv_files = glob.glob("unified_products_*.csv")
    csv_files.sort(reverse=True)  # Most recent first
    
    if not csv_files:
        print("No CSV files found. Run the scraper first with --live flag.")
        print("Try: python unified_markets_flow.py --live")
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
        print("\n Try these search terms:")
        print("   - 'bitcoin' or 'crypto'")
        print("   - 'price' or 'prediction'")
        print("   - 'election' or 'politics'")
        print("   - 'sports' or 'tennis'")
        return
    
    # Sort by match score (best matches first)
    all_results.sort(key=lambda x: x['match_score'], reverse=True)
    
    print(f"\nFound {len(all_results)} matching markets:")
    print("=" * 80)
    
    for i, result in enumerate(all_results[:10]):  # Show top 10
        print(f"\n Match {i+1} (Score: {result['match_score']:.2f})")
        print(f"Product: {result['product']}")
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

def main():
    if len(sys.argv) != 2:
        print("Usage: python search_markets.py 'search query'")
        print("\nExamples:")
        print("  python search_markets.py 'bitcoin price'")
        print("  python search_markets.py 'ethereum'")
        print("  python search_markets.py 'election'")
        print("  python search_markets.py 'tennis'")
        print("\nMake sure you have CSV files from running the scraper first!")
        return
    
    query = sys.argv[1]
    search_markets(query)

if __name__ == "__main__":
    main()
