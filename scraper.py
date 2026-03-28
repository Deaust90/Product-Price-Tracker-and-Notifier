from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from database import insert_price_data
from datetime import datetime


def init_driver1():
    options = Options()
   # options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    chromedriver_path = '/Users/andrescadena/Library/CloudStorage/OneDrive-europa-uni.de/Python/Final Project/chromedriver-mac-arm64/chromedriver'  # Adjust to your chromedriver path
    service = Service(chromedriver_path)
    return webdriver.Chrome(service=service, options=options)

def init_driver2():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    chromedriver_path = '/Users/andrescadena/Library/CloudStorage/OneDrive-europa-uni.de/Python/Final Project/chromedriver-mac-arm64/chromedriver'  # Adjust to your chromedriver path
    service = Service(chromedriver_path)
    return webdriver.Chrome(service=service, options=options)

# Scraping Idealo
def scrape_idealo(product_name, url):
    driver = init_driver1()
    try:
        driver.get(url)
        WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'h1.oopStage-title span'))
        )
        WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.oopStage-conditionButton-wrapper-text-price strong'))
        )
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        #title = soup.select_one('h1.oopStage-title span').text.strip() if soup.select_one('h1.oopStage-title span') else 'N/A'
        price_elements = soup.select('.productOffers-listItemOfferPrice')
        seller_elements = soup.select('.productOffers-listItemOfferShopV2LogoImage')
        date = datetime.now().strftime('%Y-%m-%d')
        for price_element, seller_element in zip(price_elements, seller_elements):
            price = price_element.text.replace('€', '').replace(',', '.').strip()
            price = float(price) if price else 0.00
            seller_name = seller_element.get('alt', 'Unknown Seller').strip()
            insert_price_data(product_name, seller_name, date, price)
            print(f"Idealo - Product: {product_name}, Seller: {seller_name}, Price: {price}")
    except Exception as e:
        print(f"Error scraping Idealo: {e}")
    finally:
        driver.quit()

# Scraping Amazon
def scrape_amazon(product_name, url):
    driver = init_driver2()
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "productTitle"))
        )
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        #title = soup.find('span', id='productTitle').text.strip() if soup.find('span', id='productTitle') else 'N/A'
        whole_price_tag = soup.find('span', class_='a-price-whole')
        fraction_price_tag = soup.find('span', class_='a-price-fraction')
        if whole_price_tag and fraction_price_tag:
            product_price = f"{whole_price_tag.get_text(strip=True)}.{fraction_price_tag.get_text(strip=True)}"
        else:
            price_tag = soup.find('span', class_='a-offscreen')
            product_price = price_tag.get_text(strip=True) if price_tag else '0.00'

            # Clean the price string
        product_price = (
            product_price.replace('€', '')
            .replace(',', '')  # Remove commas
            .replace('.', '', product_price.count('.') - 1)  # Retain only the last period
            .strip()
        )

        product_price = float(product_price)  # Convert the cleaned price to a float
        driver.quit()

        # Insert data into the database
        insert_price_data(product_name, "Amazon", datetime.now().strftime('%Y-%m-%d'), product_price)
        print(f"Amazon - Product: {product_name}, Price: {product_price}")

    except ValueError as ve:
        print(f"Error converting price to float for {url}: {ve}")
    finally:
        driver.quit()

# Scraping eBay
def scrape_ebay(product_name, url):
    driver = init_driver2()
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "x-item-title__mainTitle"))
        )
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        #title = soup.find('h1', class_='x-item-title__mainTitle').text.strip() if soup.find('h1', class_='x-item-title__mainTitle') else 'N/A'
        price_container = soup.find('div', class_='x-price-primary')
        price_tag = price_container.find('span', class_='ux-textspans') if price_container else None
        price = float(price_tag.text.replace('EUR', '').replace(',', '.').strip()) if price_tag else 0.00
        insert_price_data(product_name, "eBay", datetime.now().strftime('%Y-%m-%d'), price)
        print(f"eBay - Product: {product_name}, Price: {price}")
    except Exception as e:
        print(f"Error scraping eBay: {e}")
    finally:
        driver.quit()

