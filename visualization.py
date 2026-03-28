import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import seaborn as sns

# Function to read data from SQLite database
def read_data_from_db(db_file_path):
    conn = sqlite3.connect(db_file_path)  # Connect to the SQLite database
    query = "SELECT * FROM PRICES"  # Query to fetch all data
    df = pd.read_sql(query, conn)  # Load data into a pandas DataFrame
    conn.close()  # Close the connection
    return df

# Function to analyze price data
def analyze_price_data(df):
    df['Date'] = pd.to_datetime(df['Date'])  # Convert the 'Date' column to datetime format
    df.sort_values(by=['Product', 'Date'], inplace=True)  # Sort by 'Product' and 'Date'
    return df

def generate_visualizations(db_file_path, pdf_file_path, product_file):
    sns.set(style="whitegrid")  # Set Seaborn style
    df = read_data_from_db(db_file_path)  # Load data from the database
    analyzed_df = analyze_price_data(df)  # Analyze and process the data
    g7_prices_df = pd.read_excel(product_file)  # Make sure this contains 'Product name' and 'G7_Price' columns

    # Create a PDF file to save the visualizations
    with PdfPages(pdf_file_path) as pdf:
        for product in analyzed_df['Product'].unique():  # Use 'Product' from the database
            product_df = analyzed_df[analyzed_df['Product'] == product]  # Filter for the current product

            # Create a date range for the data
            date_range = pd.date_range(start=product_df['Date'].min(), end=product_df['Date'].max())

            # Retrieve the "Our Company" (G7) price for this product from the Excel file
            # Match the product name in the Excel file with the one in the database
            if product in g7_prices_df['Product name'].values:  # Use 'Product name' from the Excel file
                our_price = g7_prices_df[g7_prices_df['Product name'] == product]['G7 Price'].iloc[0]
            else:
                our_price = 0  # Set to 0 or another placeholder if G7 price is not available
            our_price_df = pd.DataFrame({'Date': date_range, 'Price': our_price, 'Seller': 'G7 Price'})

            plt.figure(figsize=(12, 15))  # Create a large figure

            # Plot 1: Minimal price and G7 price
            plt.subplot(3, 1, 1)
            for seller in product_df['Seller'].unique():
                seller_df = product_df[product_df['Seller'] == seller]
                plt.plot(seller_df['Date'], seller_df['Price'], label=seller)
            plt.plot(our_price_df['Date'], our_price_df['Price'], label='G7 Price', marker='o', linestyle='-', linewidth=2.5, color='red')
            plt.title(f'Minimal Price and G7 Price for {product}')
            plt.xlabel('Date')
            plt.ylabel('Price (€)')
            plt.xticks(rotation=45)
            plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
            plt.grid(True)

            # Plot 2: Average price and G7 price
            plt.subplot(3, 1, 2)
            avg_price_df = product_df.groupby('Date')['Price'].mean().reset_index()
            plt.plot(avg_price_df['Date'], avg_price_df['Price'], label='Average Price', marker='x', linestyle='-', linewidth=2.5, color='blue')
            plt.plot(our_price_df['Date'], our_price_df['Price'], label='G7 Price', marker='o', linestyle='-', linewidth=2.5, color='red')
            plt.title(f'Average Price and G7 Price for {product}')
            plt.xlabel('Date')
            plt.ylabel('Price (€)')
            plt.xticks(rotation=45)
            plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
            plt.grid(True)

            # Plot 3: Rank of G7 price compared to other prices
            plt.subplot(3, 1, 3)
            combined_df = pd.concat([product_df, our_price_df]).sort_values(by=['Date', 'Price'])
            combined_df['Rank'] = combined_df.groupby('Date')['Price'].rank(method='min')
            our_rank_df = combined_df[combined_df['Seller'] == 'G7 Price']
            if not our_rank_df.empty:
                plt.plot(our_rank_df['Date'], our_rank_df['Rank'], label='G7 Price Rank', marker='o', linestyle='-', linewidth=2.5, color='red')
            plt.title(f'Rank of G7 Price for {product} Compared with Other Prices')
            plt.xlabel('Date')
            plt.ylabel('Rank')
            plt.xticks(rotation=45)
            plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
            plt.grid(True)

            # Save all plots for this product to the PDF
            plt.tight_layout()
            pdf.savefig()
            plt.close()

    print(f"Visualizations saved to {pdf_file_path}")
