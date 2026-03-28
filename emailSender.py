import sqlite3
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.message import EmailMessage
import ssl

def send_email_notification(subject, body, recipients):
    context = ssl.create_default_context()
    # Email settings
    email_sender = "majoaysls@gmail.com"  # Replace with your email
    email_password = "xupa btqs dlaq ukwa"

    em = EmailMessage()

    em['From'] = email_sender
    em['To'] = recipients
    em['Subject'] = subject

    em.add_alternative(body, subtype='html')

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, recipients, em.as_string())


def read_recipients(file_path):
    with open(file_path, 'r') as f:
        recipients = [line.strip() for line in f.readlines() if line.strip()]
    return recipients

def get_ranks_data(db_file_path):
    conn = sqlite3.connect(db_file_path)  # Connect to the SQLite database
    query = '''
        SELECT * FROM prices        
    '''  # Query to fetch all data
    df = pd.read_sql(query, conn)  # Load data into a pandas DataFrame
    conn.close()  # Close the connection
    return df

def get_ranks_from_date(product, our_price, date_value, dataframe_from_date):
    company_data_from_yesterday = {
        'Product': [product],
        'Price': [our_price],
        'Date': [date_value],
        'Seller': 'G7 Price'
    }

    dataframe_from_product = dataframe_from_date.loc[dataframe_from_date['Product'] == product]
    our_price_dataframe = pd.DataFrame(company_data_from_yesterday)
    combined_dataframe_from_date = pd.concat([dataframe_from_product, our_price_dataframe]).sort_values(by=['Price'])
    combined_dataframe_from_date.loc[:, 'Rank'] = combined_dataframe_from_date['Price'].rank(method='min', ascending=True)
    return combined_dataframe_from_date


def notify_rank_changes(db_file_path, product_file, recipients_file_path):
    historical_prices_data = get_ranks_data(db_file_path)
    historical_prices_data['Date'] = pd.to_datetime(historical_prices_data['Date'])

    recipients = read_recipients(recipients_file_path)

    g7_prices_df = pd.read_excel(product_file)

    # Assumming we are gathering data everyday and values from yesterday and today are all populated
    today = pd.to_datetime('today').normalize()
    yesterday = today - pd.Timedelta(days=1)
    today_records = historical_prices_data[historical_prices_data['Date'].dt.date == today.date()]
    yesterday_records = historical_prices_data[historical_prices_data['Date'].dt.date == yesterday.date()]

    for product in historical_prices_data['Product'].unique():
        if product in g7_prices_df['Product name'].values:  # Use 'Product name' from the Excel file
            our_price = g7_prices_df[g7_prices_df['Product name'] == product]['G7 Price'].iloc[0]
        else:
            our_price = 0  # Set to 0 or another placeholder if G7 price is not available

        price_ranks_from_yesterday = get_ranks_from_date(product, our_price, yesterday, yesterday_records)
        price_ranks_from_today = get_ranks_from_date(product, our_price, today, today_records)

        rank_from_yesterday = price_ranks_from_yesterday.loc[price_ranks_from_yesterday['Seller'] == 'G7 Price']['Rank'].values[0]
        rank_from_today = price_ranks_from_today.loc[price_ranks_from_today['Seller'] == 'G7 Price']['Rank'].values[0]

        if rank_from_today !=  rank_from_yesterday:
            send_email_notification(f"Price Notification Change for Product: {product}",
                                    f"""
    <html>
    <body>
        <p>Hello,</p>
        <p>We are writing to inform you of a recent change in the price ranking for our product, <b>{product}</b>.</p>
        <ul>
            <li><b>Previous Rank (Yesterday):</b> {rank_from_yesterday}</li>
            <li><b>Current Rank (Today):</b> {rank_from_today}</li>
        </ul>
        <p>
            This ranking adjustment may indicate shifts in market trends, competitor actions, or demand fluctuations. 
        </p>
        <p>If you have any questions or require further analysis, please feel free to reach out to our team.</p>
        <p>Best regards,<br>G7</p>
    </body>
    </html>
    """, recipients)






