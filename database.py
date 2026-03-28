import sqlite3

# Initialize database
def initialize_db():
    conn = sqlite3.connect('product_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS PRICES (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Product TEXT NOT NULL,
            Seller TEXT NOT NULL,
            Date DATE NOT NULL,
            Price REAL NOT NULL,
            UNIQUE(Product, Seller, Date)
        );
    ''')
    conn.commit()
    conn.close()

def insert_price_data(product, seller, date, price):
    try:
        # Establish connection
        conn = sqlite3.connect('product_data.db')
        cursor = conn.cursor()

        # Insert data into the PRICES table
        cursor.execute('''
            INSERT OR IGNORE INTO PRICES (Product, Seller, Date, Price)
            VALUES (?, ?, ?, ?)
        ''', (product, seller, date, price))

        # Commit the transaction
        conn.commit()

    except sqlite3.IntegrityError as e:
        # Handle the case where a duplicate entry might occur due to the UNIQUE constraint
        print(f"Error inserting data: {e}")
    finally:
        # Ensure the connection is closed
        conn.close()

def insert_multiple_prices(prices_list):
    try:
        # Establish connection
        conn = sqlite3.connect('product_data.db')
        cursor = conn.cursor()

        # Start a transaction
        cursor.execute("BEGIN TRANSACTION")

        # Insert multiple rows
        cursor.executemany('''
            INSERT INTO PRICES (Product, Seller, Date, Price)
            VALUES (?, ?, ?, ?)
        ''', prices_list)

        # Commit the transaction
        conn.commit()

    except sqlite3.IntegrityError as e:
        # Handle any errors (e.g., duplicates)
        print(f"Error inserting data: {e}")
    finally:
        # Ensure the connection is closed
        conn.close()
