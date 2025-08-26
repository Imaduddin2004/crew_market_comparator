import pandas as pd

class CSVWriter:
    def __init__(self, filename):
        self.filename = filename

    def write(self, unified_products):
        rows = []
        
        for u in unified_products:
            row = {
                "Product": u["product"], 
                "Confidence": u["confidence"],
                "Total_Entries": len(u["entries"])
            }
            
            # Group entries by site and extract prices
            site_data = {}
            for entry in u["entries"]:
                site = entry['site']
                if site not in site_data:
                    site_data[site] = []
                site_data[site].append(entry.get("price", "N/A"))
            
            # Add site-specific columns
            for site, prices in site_data.items():
                # Create a clean column name
                clean_site = site.replace("Scraper", "").replace("PredictionMarket", "Other")
                row[f"{clean_site}_Price"] = " | ".join(filter(None, prices)) if prices else "N/A"
                row[f"{clean_site}_Count"] = len(prices)
            
            rows.append(row)

        df = pd.DataFrame(rows)
        
        # Reorder columns for better readability
        priority_cols = ["Product", "Confidence", "Total_Entries"]
        other_cols = [col for col in df.columns if col not in priority_cols]
        df = df[priority_cols + sorted(other_cols)]
        
        df.to_csv(self.filename, index=False)
        print(f"CSV written with {len(rows)} rows and {len(df.columns)} columns")
        print(f"Columns: {', '.join(df.columns)}")
