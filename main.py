import time

from bs4 import BeautifulSoup


from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import os
import datetime

from selenuim.base_page import BasePage


def save_html(name: str, url: str):
    """Launch the WebDriver, save the page source as an HTML file with a timestamped filename."""
    options = Options()
    # options.add_argument("--proxy-server=http://127.0.0.1:8081") # TODO: hook a json directly? consider run  mitmdump -s proxy.py --set listen_port=8081
    driver = webdriver.Chrome(options=options)
    try:
        page = BasePage(driver)
        page.open(url)
        time.sleep(10)  # Wait for the page to load completely

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.html"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print(f"Page saved as: {filename}")
    finally:
        driver.quit()


def get_latest_html(name: str) -> str:
    """Fetch the latest HTML file for the given name."""
    files = [f for f in os.listdir('.') if f.startswith(name) and f.endswith('.html')]
    if not files:
        raise FileNotFoundError(f"No HTML files found for name: {name}")

    latest_file = max(files, key=os.path.getmtime)  # Get the most recently modified file
    print(f"Latest HTML file: {latest_file}")
    return latest_file

def extract_agency_data(html):
    soup = BeautifulSoup(html, "html.parser")
    agency_items = soup.find_all("li", {"data-testid": "agency-item"})
    extracted_data = []
    for item in agency_items:
        price_element = item.find("span", {"data-testid": "price"})
        price = price_element.get_text(strip=True) if price_element else None
        content_element = item.find("div", class_="item-data-content_itemDataContentBox__gvAC2")
        content = content_element.get_text(strip=True) if content_element else None
        extracted_data.append({
            "price": price,
            "content": content
        })
    return extracted_data


def parse_html(name: str):
    """Parse the latest HTML file for the given name and extract data."""
    html_file = get_latest_html(name)

    with open(html_file, "r", encoding="utf-8") as f:
        html_content = f.read()

        data = extract_agency_data(html_content)

        for idx, item in enumerate(data, start=1):
            print(f"Item {idx}:")
            print(f"  Price: {item['price']}")
            print(f"  Content: {item['content']}")
            print("-" * 30)


def parse_and_save(name: str, url: str, fetch=True):
    if fetch:
        save_html(name, url)
    print (f"RESULTS FOR {name}")
    parse_html(name)

if __name__ == "__main__":

    searches = [
        {
            "name": "Regular_apartments",
            "url": "https://www.yad2.co.il/realestate/rent?multiCity=8700%2C6400%2C6900%2C9700&propertyGroup=apartments&property=1&rooms=2-3.5&price=3500-6000&balcony=1"
        },
        {
            "name" : "Penthouses",
            "url": "https://www.yad2.co.il/realestate/rent?multiCity=6900%2C9700%2C6400&propertyGroup=apartments&property=1&squaremeter=60-160&text=%D7%92%D7%92"
        }
    ]

    for search in searches:
        # print(f"{search['name'].lower()} , {search['url']}")
        parse_and_save(name=search['name'].lower(), url=search['url'], fetch=False)

