import time
import json
import random
import csv
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException


def change_list(r_data):
    ret_val = dict()
    # ret_val = list()
    keys = ['title', 'review', 'rating', 'author', 'review_date']

    while True:
        try:
            nrow = r_data.__next__()
            ret_val[nrow[-2]] = dict(zip(keys, nrow))
            # ret_val.append(dict(zip(keys, nrow)))
        except StopIteration:
            break

        print(ret_val)

    return ret_val


def get_reviews():
    base_url = 'https://www.amazon.com/RockBirds-Flashlights-Bright-Aluminum-Flashlight/product-reviews/B00X61AJYM'
    driver = webdriver.Chrome(executable_path='chromedriver')
    driver.get(base_url)

    ret_val = dict()
    # ret_val = list()
    a = parse_page(driver.page_source)
    ret_val.update(change_list(a))
    # ret_val.extend(change_list(a))

    for t in range(0, 149):
        time.sleep(random.randint(1, 5))
        try:
            driver.find_element_by_xpath('//*[@id="cm_cr-pagination_bar"]/ul/li[9]').click()
        except NoSuchElementException:
            driver.find_element_by_xpath('//*[@id="cm_cr-pagination_bar"]/ul/li[8]').click()

        time.sleep(random.randint(1, 5))
        rdata = parse_page(driver.page_source)
        ret_val.extend(change_list(rdata))

    with open('json_output.txt', 'w') as outfile:
        json.dump(ret_val, outfile)

    # with open('output.csv', 'w') as f:
        # outfile = csv.DictWriter(f, fieldnames=['title', 'review', 'rating', 'author', 'review_date'])
        # outfile.writeheader()
        # outfile.writerows(ret_val)


def parse_page(page_source):
    soup = BeautifulSoup(page_source, 'lxml')

    review_divs = soup.find('div', {'id': 'cm_cr-review_list'}).find_all('div', {'class': 'a-section celwidget'})

    for rd in review_divs:
        # get only verified purchases
        try:
            rd.find('span', {'data-hook': 'avp-badge'}).get_text()
        except AttributeError:
            continue

        yield [rd.find('a', {'data-hook': 'review-title'}).get_text(),  # title
               rd.find('span', {'data-hook': 'review-body'}).get_text(),  # review
               rd.find('span', {'class': 'a-icon-alt'}).get_text(),  # rating
               rd.find('a', {'data-hook': 'review-author'}).get_text(),  # author
               rd.find('span', {'data-hook': 'review-date'}).get_text()]  # review date


get_reviews()
