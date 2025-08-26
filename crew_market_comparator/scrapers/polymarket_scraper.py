from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import re
import random

class PolymarketScraper:
    def fetch_data(self):
        try:
            print(" Starting Polymarket scraping...")
            
            # Set up Chrome options for better compatibility
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-cache")  # Disable caching
            chrome_options.add_argument("--disable-application-cache")
            chrome_options.add_argument("--disable-offline-load-stale-cache")
            chrome_options.add_argument("--disk-cache-size=0")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Add cache-busting parameter to URL
            cache_buster = random.randint(1000, 9999)
            url = f"https://polymarket.com/markets?cb={cache_buster}"
            print(f" Navigating to Polymarket with cache buster: {url}")
            driver.get(url)
            
            # Wait for page to load with random timing
            wait_time = random.uniform(4, 8)
            print(f" Waiting {wait_time:.1f} seconds for page to load...")
            time.sleep(wait_time)
            
            print(" Looking for market elements...")
            
            # Try multiple selectors for better compatibility
            selectors = [
                "a[href*='/event/']",
                "[data-testid*='market']",
                ".market-item",
                ".market-card"
            ]
            
            markets = []
            for selector in selectors:
                try:
                    markets = driver.find_elements(By.CSS_SELECTOR, selector)
                    if markets:
                        print(f" Found {len(markets)} markets with selector: {selector}")
                        break
                except Exception as e:
                    print(f" Selector {selector} failed: {e}")
                    continue
            
            if not markets:
                # Try to get any clickable elements
                markets = driver.find_elements(By.TAG_NAME, "a")
                print(f" Fallback: Found {len(markets)} total links")
            
            # Randomize the order and limit to get different results each time
            if markets:
                random.shuffle(markets)
                # Randomly select between 8-15 markets instead of always 10
                max_markets = random.randint(8, min(15, len(markets)))
                markets = markets[:max_markets]
                print(f" Randomly selected {len(markets)} markets from {len(markets)} found")
            
            results = []
            for i, m in enumerate(markets):
                try:
                    text = m.text.strip()
                    href = m.get_attribute("href")
                    
                    if text and len(text) > 5 and href and '/event/' in href:
                        # Clean up the product name - extract just the main question/topic
                        clean_name = self.clean_product_name(text)
                        
                        if clean_name:
                            results.append({
                                "site": "Polymarket", 
                                "product": clean_name, 
                                "price": self.extract_price(text),  # Extract actual price
                                "url": href
                            })
                            print(f"   Market {i+1}: {clean_name[:50]}...")
                except Exception as e:
                    print(f" Error processing market {i+1}: {e}")
                    continue
            
            print(f" Polymarket scraping completed: {len(results)} markets found")
            driver.quit()
            return results
            
        except Exception as e:
            print(f" Polymarket scraping failed: {e}")
            if 'driver' in locals():
                driver.quit()
            return []
    
    def clean_product_name(self, text):
        """Extract clean product name from verbose Polymarket text"""
        lines = text.split('\n')
        
        # Look for the main question or topic
        for line in lines:
            line = line.strip()
            if line and len(line) > 10 and not line.startswith('$') and not line.isdigit():
                # Remove common metadata
                clean = re.sub(r'\$[\d,]+m?\s+Vol\.?', '', line)
                clean = re.sub(r'\$[\d,]+m?\s+today', '', clean)
                clean = re.sub(r'\d+%', '', clean)
                clean = re.sub(r'↓\s*\d+k?', '', clean)
                clean = re.sub(r'\d+\s+bps\s+(increase|decrease)', '', clean)
                
                # Clean up extra whitespace
                clean = re.sub(r'\s+', ' ', clean).strip()
                
                if clean and len(clean) > 5:
                    return clean
        
        # If no clean line found, return the first meaningful line
        for line in lines:
            if line.strip() and len(line.strip()) > 5:
                return line.strip()[:100]  # Limit length
        
        return None

    def extract_price(self, text):
        """Extract price information from Polymarket text"""
        try:
            # Look for percentage patterns
            percentage_match = re.search(r'(\d+)%', text)
            if percentage_match:
                return f"{percentage_match.group(1)}%"
            
            # Look for volume amounts (e.g., "$48m Vol.", "$3m Vol.")
            volume_match = re.search(r'\$([\d,]+m?)\s+Vol\.?', text)
            if volume_match:
                return f"Vol: {volume_match.group(1)}"
            
            # Look for today's volume
            today_match = re.search(r'\$([\d,]+m?)\s+today', text)
            if today_match:
                return f"Today: {today_match.group(1)}"
            
            # Look for bps changes
            bps_match = re.search(r'(\d+)\s+bps\s+(increase|decrease)', text)
            if bps_match:
                return f"{bps_match.group(1)} bps {bps_match.group(2)}"
            
            return "N/A"
        except:
            return "N/A"