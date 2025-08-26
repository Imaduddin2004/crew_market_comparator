class MockScraper:
    def __init__(self, site_name):
        self.site_name = site_name
    
    def fetch_data(self):
        # Mock data for testing
        mock_data = [
            {"site": self.site_name, "product": f"Mock Product 1 from {self.site_name}", "price": "0.65"},
            {"site": self.site_name, "product": f"Mock Product 2 from {self.site_name}", "price": "0.32"},
            {"site": self.site_name, "product": f"Mock Product 3 from {self.site_name}", "price": "0.78"}
        ]
        return mock_data