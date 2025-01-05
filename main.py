import time

from bs4 import BeautifulSoup


from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from selenuim.base_page import BasePage


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


if __name__ == "__main__":

    # TODO: optional launch;
    options = Options()
    driver = webdriver.Chrome(options=options)
    page = BasePage(driver)
    page.open("https://www.yad2.co.il/realestate/rent?multiCity=6900%2C9700%2C6400&propertyGroup=apartments&property=1&squaremeter=60-160&text=%D7%92%D7%92&zoom=13")
    time.sleep(25)
    with open("page.html", "w", encoding='utf-8') as f:
        f.write(driver.page_source)

    # TODO: can do dry run
    with open("page.html") as f:
        html_content = f.read()
        data = extract_agency_data(html_content)
        for idx, item in enumerate(data, start=1):
            print(f"Item {idx}:")
            print(f"  Price: {item['price']}")
            print(f"  Content: {item['content']}")
            print("-" * 30)
