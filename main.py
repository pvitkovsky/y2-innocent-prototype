import datetime
import os
import time
import re

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from selenuim.base_page import BasePage


def save_html(name: str, url: str):
    options = Options()
    driver = webdriver.Chrome(options=options)
    try:
        page = BasePage(driver)
        page.open(url)
        time.sleep(1)
        match = re.search("{.*}", driver.page_source)
        if match:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{name}_{timestamp}.json"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(match.group(0))
            print(f"Page saved as: {filename}")
    finally:
        driver.quit()


def get_latest_html(name: str) -> str:
    files = [f for f in os.listdir('.') if f.startswith(name) and f.endswith('.json')]
    if not files:
        raise FileNotFoundError(f"No HTML files found for name: {name}")

    latest_file = max(files, key=os.path.getmtime)  # Get the most recently modified file
    print(f"Latest HTML file: {latest_file}")
    return latest_file


def parse_and_save(name: str, url: str, fetch=True):
    if fetch:
        save_html(name, url)
    # TODO: next step - using those nice JSONS. step by step: parse them into a payload format, translate hebrew, start d/l images etc etc;


if __name__ == "__main__":

    searches = [
        { "name": "Gateway",
          "url": "https://gw.yad2.co.il/recommendations/items/realestate?type=home&count=20&categoryId=2&propertyValues=1&cityValues=6900,9700,6400&subCategoriesIds=2"
        },
    ]

    for search in searches:
       parse_and_save(name=search['name'].lower(), url=search['url'], fetch=True)