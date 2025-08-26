# Prediction Market Data Collection System

A robust Python-based backend system that automatically collects, unifies, and analyzes prediction market data from multiple platforms, including **Polymarket**, **Kalshi**, and other prediction market sites.


## Features

* **Multi-Platform Scraping**: Collects real-time data from multiple prediction market platforms.
* **Intelligent Data Unification**: Uses semantic similarity to group identical or related markets.
* **Real-Time Price Extraction**: Captures current prices, odds, and key market metrics.
* **Advanced Search**: Quickly find markets based on keywords like "Bitcoin price" or "election odds".
* **Historical Tracking**: Generates timestamped CSV outputs for analysis over time.
* **Robust Error Handling**: Gracefully handles API errors, scraper failures, and connectivity issues.
* **Extensible Framework**: Modular structure allows adding more platforms easily.


## Deliverables

* Unified CSV reports containing:

  * Consolidated product names
  * Prices from each platform
  * Confidence scores for semantic matches
* Reusable web scrapers for Polymarket, Kalshi, and other sites.
* CLI search tool for querying the collected data.
* Well-documented codebase with clear instructions.


## Installation

### Prerequisites

* Python 3.7 or higher
* Google Chrome browser
* Internet connection

### Setup Instructions

1. **Clone the repository**

```bash
git clone https://github.com/Imaduddin2004/prediction-market-collector.git
cd prediction-market-collector
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Verify the installation**

```bash
python unified_markets_flow.py --mock
```


## Quick Start

### 1. Test with Mock Data

```bash
python unified_markets_flow.py --mock
```

### 2. Collect Live Data

```bash
python unified_markets_flow.py --live
```

### 3. Search for Specific Markets

```bash
python search_markets.py "bitcoin"
python search_markets.py "election"
```


## Project Structure

```
prediction-market-collector/
├── scrapers/                        # Web scraping modules
│   ├── polymarket_scraper.py       # Polymarket scraper
│   ├── kalshi_scraper.py           # Kalshi scraper
│   ├── prediction_market_scraper.py# Other prediction markets
│   └── mock_scraper.py             # Mock data for testing
├── utils/                           # Utility modules
│   ├── semantic_matcher.py         # Semantic product unification
│   └── csv_writer.py               # CSV export functionality
├── unified_markets_flow.py         # Main pipeline entry point
├── search_markets.py               # Search tool for querying CSVs
├── requirements.txt                # Project dependencies
└── README.md                      # Documentation
```



## Usage Examples

### Collect Live Data

```bash
python unified_markets_flow.py --live
```

Generates a timestamped CSV file:

```
output/unified_products_<timestamp>.csv
```

### Search Unified Data

```bash
python search_markets.py "bitcoin"
python search_markets.py "ethereum price"
python search_markets.py "election"
```

### Test Individual Scrapers

```bash
python test_scraper.py polymarket
python test_scraper.py kalshi
python test_scraper.py predictionmarket
```


## Output Format

The generated CSV contains the following columns:

| Column            | Description                     | Example                                  |
| ----------------- | ------------------------------- | ---------------------------------------- |
| Product           | Unified market name/description | "What price will Bitcoin hit in August?" |
| Confidence        | Similarity score                | 0.92                                     |
| Total\_Entries    | Number of matched markets       | 2                                        |
| Kalshi\_Count     | Markets from Kalshi             | 1                                        |
| Kalshi\_Price     | Latest price from Kalshi        | "28%"                                    |
| Polymarket\_Count | Markets from Polymarket         | 1                                        |
| Polymarket\_Price | Latest price from Polymarket    | "14%"                                    |


## Search Capabilities

* **Exact matches**: Searching “bitcoin” returns all markets containing “Bitcoin”.
* **Partial matches**: Searching “price” fetches relevant price prediction markets.
* **Context-aware matching**: “election 2028” retrieves related political markets.

Each search result includes:

* Match relevance score
* Current market prices
* Platform information
* Confidence scores


## Troubleshooting

### Common Issues

**1. No Data Collected**

```bash
python unified_markets_flow.py --mock
python test_scraper.py polymarket
```

**2. Chrome Driver Issues**

* Ensure Chrome is installed and updated.
* Check firewall/antivirus permissions.
* `webdriver-manager` automatically installs ChromeDriver.

**3. Empty CSV Output**

* Use `--live` for fresh data.
* Verify internet connectivity.
* Check console logs for error messages.


## Privacy & Ethics

* Only collects **publicly available data**.
* Implements **rate limiting** to avoid server overload.
* Follows websites’ **terms of service**.
* Uses realistic browser identification for respectful scraping.


## Future Enhancements

* Real-time price monitoring with notifications.
* Historical data storage and trend visualization.
* Additional prediction market integrations.
* REST API endpoints for data access.
* Machine learning for improved semantic clustering.
* Web dashboard for interactive exploration.

## Requirements

The full dependency list is in `requirements.txt`.
Key dependencies:

* `requests` – API integration
* `selenium` – Web scraping automation
* `beautifulsoup4` – HTML parsing
* `pandas` – Data handling and CSV export
* `sentence-transformers` – Semantic similarity matching
* `webdriver-manager` – Automatic ChromeDriver installation


## Contact

**Author:** \ MD Imaduddin Aiman
**GitHub:** (https://github.com/Imaduddin2004)
**LinkedIn:** (www.linkedin.com/in/imadaiman)


