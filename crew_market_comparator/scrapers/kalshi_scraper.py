from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import random
import re


class KalshiScraper:
    def __init__(self):
        self.driver = None

    def _setup_driver(self):
        """Set up Chrome WebDriver with proper options."""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-cache")  # Disable caching
        chrome_options.add_argument("--disable-application-cache")
        chrome_options.add_argument("--disable-offline-load-stale-cache")
        chrome_options.add_argument("--disk-cache-size=0")
        chrome_options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

    def fetch_data(self):
        try:
            print(" Starting Kalshi scraping...")
            self._setup_driver()

            # Add cache-busting parameter to URL
            cache_buster = random.randint(1000, 9999)
            url = f"https://kalshi.com/events?cb={cache_buster}"
            print(f" Navigating to Kalshi with cache buster: {url}")
            self.driver.get(url)

            # Wait until body loads fully
            try:
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                print(" Page loaded successfully")
            except:
                print(" Page took too long to load")

            # Random wait time to simulate human behavior
            wait_time = random.uniform(3, 7)
            print(f" Waiting {wait_time:.1f} seconds for dynamic content...")
            time.sleep(wait_time)

            # Try scrolling to trigger dynamic content loading
            print(" Scrolling to trigger dynamic content...")
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(2, 4))
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(random.uniform(1, 3))

            print(" Searching for market elements...")
            selectors = [
                "[data-testid*='market']",
                ".market-item",
                ".market-card",
                "[class*='market']",
                "[class*='event']",
                "[class*='card']",
                "[class*='prediction']",
                "[class*='bet']",
            ]

            markets = []
            for selector in selectors:
                try:
                    markets = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if markets:
                        print(f" Found {len(markets)} markets using selector: {selector}")
                        break
                except Exception:
                    continue

            # Fallback: get links if no market cards found
            if not markets:
                print(" No markets found with selectors, falling back to links...")
                links = self.driver.find_elements(By.TAG_NAME, "a")
                markets = [
                    link for link in links
                    if link.text.strip() and link.get_attribute("href")
                    and len(link.text.strip()) > 5
                    and not any(x in link.text.lower() for x in [
                        "login", "sign up", "contact", "privacy", "terms"
                    ])
                ]
                print(f" Fallback found {len(markets)} potential market links")

            # Final fallback: grab visible text from <div>
            if not markets:
                print(" Trying to fetch market data from divs...")
                divs = self.driver.find_elements(By.TAG_NAME, "div")
                markets = [
                    div for div in divs
                    if div.text.strip() and len(div.text.strip()) > 10
                    and any(k in div.text.lower() for k in [
                        "will", "when", "what", "how", "odds", "probability"
                    ])
                ]
                print(f" Found {len(markets)} market divs")

            # Randomize the order and limit to get different results each time
            if markets:
                random.shuffle(markets)
                # Randomly select between 5-15 markets instead of always 10
                max_markets = random.randint(5, min(15, len(markets)))
                markets = markets[:max_markets]
                print(f" Randomly selected {len(markets)} markets from {len(markets)} found")

            # Process the results
            results = []
            for i, market in enumerate(markets):
                try:
                    text = market.text.strip()
                    href = market.get_attribute("href") if market.get_attribute("href") else None

                    if not text or len(text) < 10:
                        continue

                    # Skip navigation-related items
                    if any(skip in text.lower() for skip in [
                        "contact", "privacy", "terms", "login", "sign up"
                    ]):
                        continue

                    results.append({
                        "site": "Kalshi",
                        "product": text,
                        "price": self.extract_price(text),  # Extract actual price
                        "url": href,
                    })

                    print(f"   Market {i + 1}: {text[:80]}...")
                except Exception:
                    continue

            print(f" Kalshi scraping completed: {len(results)} markets found")
            return results

        except Exception as e:
            print(f" Kalshi scraping failed: {e}")
            return []

        finally:
            if self.driver:
                self.driver.quit()

    def extract_price(self, text):
        """Extract price information from market text"""
        try:
            # Look for percentage patterns (e.g., "28%", "51%")
            percentage_match = re.search(r'(\d+)%', text)
            if percentage_match:
                return f"{percentage_match.group(1)}%"
            
            # Look for dollar amounts (e.g., "$100 → $352")
            dollar_match = re.search(r'\$(\d+(?:,\d+)*)', text)
            if dollar_match:
                return f"${dollar_match.group(1)}"
            
            # Look for cent amounts (e.g., "27¢", "75¢")
            cent_match = re.search(r'(\d+)¢', text)
            if cent_match:
                return f"{cent_match.group(1)}¢"
            
            # Look for "Yes/No" patterns
            if "Yes" in text and "No" in text:
                return "Yes/No"
            
            return "N/A"
        except:
            return "N/A"


# Run the scraper directly for testing
if __name__ == "__main__":
    scraper = KalshiScraper()
    data = scraper.fetch_data()
    print("\n Final Results:", data)
