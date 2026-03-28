import pandas as pd

from emailSender import notify_rank_changes
from scraper import scrape_idealo, scrape_amazon, scrape_ebay
from database import initialize_db, insert_price_data
from visualization import generate_visualizations
from datetime import datetime

# Initialize the database
initialize_db()

# Load product data from Excel
def load_product_data(file_path):
    df = pd.read_excel(file_path)
    return df

# Process each product
def process_products(product_file):
    df = load_product_data(product_file)

    for _, row in df.iterrows():
        product_name = row['Product name']
        idealo_url = row['Idealo URL']
        amazon_url = row['Amazon URL']
        ebay_url = row['Ebay URL']
        company_price = row['G7 Price']

        # Add company product data
        insert_price_data(product_name, "G7", pd.Timestamp.now().strftime('%Y-%m-%d'), company_price)

        # Scrape data from each platform using the standardized name
        if pd.notna(idealo_url):
            scrape_idealo(product_name, idealo_url)  # ✅ Pass the fixed product name
        if pd.notna(amazon_url):
            scrape_amazon(product_name, amazon_url)  # ✅ Pass the fixed product name
        if pd.notna(ebay_url):
            scrape_ebay(product_name, ebay_url)  # ✅ Pass the fixed product name

print("All products processed.")

if __name__ == "__main__":
    product_file = "/Users/andrescadena/Library/CloudStorage/OneDrive-europa-uni.de/Python/Final Project/products.xlsx"  # Path to your Excel file
    process_products(product_file)

    # Generate visualizations
    db_file_path = "/Users/andrescadena/Library/CloudStorage/OneDrive-europa-uni.de/Python/Final Project/product_data.db"  # Path to the SQLite database
    pdf_file_path = f"/Users/andrescadena/Library/CloudStorage/OneDrive-europa-uni.de/Python/Final Project/{datetime.now().strftime('%Y-%m-%d')}_prices_visualizations.pdf"  # PDF output file
    generate_visualizations(db_file_path, pdf_file_path, product_file)

    recipients_file_path = "/Users/andrescadena/Library/CloudStorage/OneDrive-europa-uni.de/Python/Final Project/settings.txt"

    # Analyze ranks and send emails
    notify_rank_changes(db_file_path, product_file, recipients_file_path)
