import logging
import time
from numbers import Number
from urllib.parse import urlparse

from selenium.common import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib3.exceptions import MaxRetryError


class BasePage(object):
    def __init__(self, driver):
        self.driver = driver
        self.timeout = 30

    def find_element(self, *locator):
        return self.driver.find_element(*locator)

    def find_element(self, by, value):
        return self.driver.find_element(by, value)

    def open(self, url):
        self.driver.get(url)

    def get_title(self):
        return self.driver.title

    def get_url(self):
        return self.driver.current_url

    def hover(self, *locator):
        element = self.find_element(*locator)
        hover = ActionChains(self.driver).move_to_element(element)
        hover.perform()

    def wait_element(self, *locator):
        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(locator))
        except TimeoutException:
            logging.info("\n * ELEMENT NOT FOUND WITHIN GIVEN TIME! --> %s" %(locator[1]))
            self.driver.quit()

    def scroll_and_wait(self, element=None):
        if element is None:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        else:
            self.driver.execute_script("arguments[0].scrollIntoView();", element)
        time.sleep(0.5)  # TODO: explain why needs sleep after moving; can it be made explicit?

    def get_url_part(self, part: Number) -> str:
        current_url = self.get_url()
        parsed_url = urlparse(current_url)
        path = parsed_url.path
        path_parts = path.split('/')
        sample_id = path_parts[part]
        return sample_id

    def get_placeholder(self, value):
        return f"//input[@placeholder='{value}']"

    def wait_paginator(self):
        try:
            WebDriverWait(self.driver, 15).until(
                lambda driver: driver.find_element(By.CSS_SELECTOR, '.mat-paginator-range-label').get_attribute(
                   "innerHTML") != 0)
        except MaxRetryError:
            logging.error("paginator not found, looks like the page wasn't loaded")
