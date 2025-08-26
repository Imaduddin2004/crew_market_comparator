from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

class PredictionMarketScraper:
    def fetch_data(self):
        try:
            print("Starting PredictionMarket scraping...")
            
            # Set up Chrome options for better compatibility
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            print("Navigating to PredictionMarket...")
            # Try different URLs for prediction markets - more realistic ones
            urls_to_try = [
                "https://manifold.markets/",
                "https://manifold.markets/markets",
                "https://www.zeitgeist.pm/",
                "https://www.zeitgeist.pm/markets"
            ]
            
            markets = []
            working_url = None
            
            for url in urls_to_try:
                try:
                    print(f"Trying URL: {url}")
                    driver.get(url)
                    time.sleep(5)  # Wait longer for content to load
                    
                    print(f"Page title: {driver.title}")
                    print(f"Current URL: {driver.current_url}")
                    
                    # Try multiple selectors for better compatibility
                    selectors = [
                        "[data-testid*='market']",
                        ".market-item",
                        ".market-card",
                        ".event-item",
                        ".series-item",
                        "[class*='market']",
                        "[class*='event']",
                        "a[href*='/market']",
                        "a[href*='/event']",
                        ".market",
                        ".event",
                        "[class*='card']"
                    ]
                    
                    for selector in selectors:
                        try:
                            markets = driver.find_elements(By.CSS_SELECTOR, selector)
                            if markets:
                                print(f"Found {len(markets)} markets with selector: {selector}")
                                working_url = url
                                break
                        except Exception as e:
                            continue
                    
                    if markets:
                        break
                        
                except Exception as e:
                    print(f"Failed to load {url}: {e}")
                    continue
            
            if not markets:
                # Try to get any clickable elements that might be markets
                markets = driver.find_elements(By.TAG_NAME, "a")
                print(f"🔍 Fallback: Found {len(markets)} total links")
                
                # Show some sample links for debugging
                for i, m in enumerate(markets[:10]):
                    try:
                        text = m.text.strip()
                        href = m.get_attribute("href")
                        print(f"  Link {i+1}: '{text}' -> {href}")
                    except:
                        pass
                
                # Filter out navigation and utility links
                filtered_markets = []
                for m in markets:
                    href = m.get_attribute("href")
                    text = m.text.strip()
                    if (href and 
                        not href.startswith("mailto:") and 
                        not href.startswith("#") and
                        not href.endswith("/") and
                        text and len(text) > 5 and
                        not text.lower() in ["support", "help", "contact", "about", "privacy", "terms", "login", "sign up", "cloudflare"]):
                        filtered_markets.append(m)
                
                markets = filtered_markets
                print(f"Filtered to {len(markets)} potential market links")
            
            # If still no markets, try looking for div elements with market-like content
            if not markets:
                print("Trying to find market content in div elements...")
                divs = driver.find_elements(By.TAG_NAME, "div")
                market_divs = []
                
                for div in divs:
                    try:
                        text = div.text.strip()
                        if (text and len(text) > 10 and 
                            any(keyword in text.lower() for keyword in ["market", "event", "prediction", "bet", "odds", "probability", "question", "will", "when", "how"])):
                            market_divs.append(div)
                    except:
                        continue
                
                if market_divs:
                    print(f"Found {len(market_divs)} potential market divs")
                    markets = market_divs[:10]  # Limit to 10
            
            # If still no markets, try scrolling to trigger lazy loading
            if not markets:
                print("Trying to scroll page to trigger lazy loading...")
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
                driver.execute_script("window.scrollTo(0, 0);")
                time.sleep(2)
                
                # Try selectors again after scrolling
                for selector in selectors:
                    try:
                        new_markets = driver.find_elements(By.CSS_SELECTOR, selector)
                        if new_markets:
                            print(f"Found {len(new_markets)} markets with selector after scrolling: {selector}")
                            # Filter out empty elements
                            filtered_new_markets = []
                            for m in new_markets:
                                text = m.text.strip()
                                if text and len(text) > 10:
                                    filtered_new_markets.append(m)
                            
                            if filtered_new_markets:
                                markets = filtered_new_markets
                                print(f"Filtered to {len(markets)} non-empty market elements")
                                break
                    except:
                        continue
            
            # If still no markets, try a different approach - look for text content directly
            if not markets:
                print("Trying to find market content by searching page text...")
                page_text = driver.find_element(By.TAG_NAME, "body").text
                lines = page_text.split('\n')
                
                market_lines = []
                for line in lines:
                    line = line.strip()
                    if (line and len(line) > 20 and 
                        any(keyword in line.lower() for keyword in ["will", "when", "how many", "what", "which", "predict", "forecast", "odds", "probability"]) and
                        not any(skip in line.lower() for skip in ["cookie", "privacy", "terms", "login", "sign up", "support"])):
                        market_lines.append(line)
                
                if market_lines:
                    print(f"Found {len(market_lines)} potential market lines in page text")
                    # Create mock elements for these text lines
                    from selenium.webdriver.remote.webelement import WebElement
                    class MockElement:
                        def __init__(self, text):
                            self._text = text
                        def text(self):
                            return self._text
                        def get_attribute(self, attr):
                            return None if attr == 'href' else ''
                    
                    markets = [MockElement(line) for line in market_lines[:10]]
            
            results = []
            for i, m in enumerate(markets[:10]):  # limit to 10
                try:
                    text = m.text.strip()
                    href = m.get_attribute("href") if hasattr(m, 'get_attribute') else None
                    
                    print(f"Processing element {i+1}: text='{text[:100]}...' href='{href}'")
                    
                    if text and len(text) > 10:  # Increased minimum length
                        # Skip navigation and utility links
                        if any(skip in text.lower() for skip in ["support", "help", "contact", "about", "privacy", "terms", "login", "sign up", "cloudflare"]):
                            print(f"   Skipping navigation link: {text[:50]}...")
                            continue
                            
                        # Clean up the text if it's too long
                        if len(text) > 200:
                            text = text[:200] + "..."
                        
                        results.append({
                            "site": "PredictionMarket", 
                            "product": text, 
                            "price": None,
                            "url": href
                        })
                        print(f"   Market {i+1}: {text[:50]}...")
                    else:
                        print(f"   Skipping element with insufficient text: '{text}' (length: {len(text) if text else 0})")
                except Exception as e:
                    print(f" Error processing market {i+1}: {e}")
                    continue
            
            print(f" PredictionMarket scraping completed: {len(results)} markets found")
            if working_url:
                print(f"Working URL: {working_url}")
            driver.quit()
            return results
            
        except Exception as e:
            print(f" PredictionMarket scraping failed: {e}")
            if 'driver' in locals():
                driver.quit()
            return []