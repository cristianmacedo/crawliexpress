import csv
import math
import requests
import urllib.parse
import random
import json
import re

from bs4 import BeautifulSoup

class Crawliexpress:
    
    # Set default request parameters
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36', 
    }
    cookies = {
        "aep_usuc_f": "region=US",
    }
    item_uri = 'https://www.aliexpress.com/item/'
    feedback_uri = "https://feedback.aliexpress.com/display/productEvaluation.htm"

    def __init__(self, owner_member_id="", company_id="", member_type="seller", region="US"):
        self.owner_member_id = owner_member_id or self.generate_id()
        self.company_id = company_id or self.generate_id()
        self.cookies['aep_usuc_f'] = f'region={region}'
        self.member_type = member_type
        self.count = 1
        pass

    # Generate random ID
    @staticmethod
    def generate_id(length=9, suffix =2):
        numbers =  range(0,10)
        id = f'{suffix}'
        for i in range(0, length-1):
            id = f'{id}{random.choice(numbers)}'
        return id

    # Save .csv file from dict List [{}]
    @staticmethod
    def save_file(results):
        if(len(results) > 0):
            with open(f'{filename}.csv', 'w', encoding='utf8', newline='') as output_file:
                output_file.write('sep=,\n')
                fc = csv.DictWriter(output_file, fieldnames=results[0].keys())
                fc.writeheader()
                fc.writerows(results)

    # Reduce text size to fit in prints
    @staticmethod
    def truncate(text, max=20):
        return f'{text[0:max]}...' if len(text) > max else text

    # Scrap through review pages on aliexpress product (Recursive)
    def reviews(self, product_id, page=1, version="2", start_valid_date="", i18n=False, translate=False, only_from_my_country=False, with_pictures=False, max_pages=-1):

        # Results container
        res = []

        # GET request URL parameters
        params = {
            'productId': product_id,
            'v': version,
            'ownerMemberId': self.owner_member_id,
            'companyId': self.company_id,
            'memberType': self.member_type,
            'startValidDate': start_valid_date, 
            'i18n': 'true' if i18n else 'false',
            'translate': 'Y' if translate else 'N',
            'onlyFromMyCountry':  'true' if only_from_my_country else 'false',
            'withPictures':  'true' if with_pictures else 'false',
            'page': page
        }

        # Converting parameters dict to URL enconding format ('foo': 'bar' -> foo=bar&)
        url = f"{self.feedback_uri}?{urllib.parse.urlencode(params)}"

        request = requests.get(url, headers=self.headers, cookies=self.cookies)
        soup = BeautifulSoup(request.content, 'html.parser')
        feedback_items = soup.find_all('div', class_='feedback-item')

        for item in feedback_items:

            review = {}

            fb_user_info = item.find(class_='fb-user-info')
            user_order_info = item.find(class_='user-order-info')
            buyer_feedback = item.find(class_='buyer-feedback')

            # BUYER INFO
            review['user_name'] = fb_user_info.find(class_='user-name').text.strip()
            review['user_country'] = fb_user_info.find(class_='user-country').contents[0].text.strip()

            print(review['user_country'])

            # BUYER FEEDBACK
            review['text'] = buyer_feedback.contents[1].text.strip()
            review['date'] = buyer_feedback.contents[3].text.strip()

            # STAR COUNT
            star_view_percentage = item.find(class_='star-view').contents[0]['style'].split(':')[1].replace('%', '')
            review['rating'] = math.floor(int(star_view_percentage)/20)

            # PRODUCT ATTIRBUTES (VARIATONS, SHIPS FROM, SHIPPING METHOD)
            for prop in user_order_info.find_all('span'):
                key, data = prop.text.split(':')
                review[key.strip().lower().replace(' ', '_')] = data.strip()
                pass

            # PICS
            pic_view_items = item.find_all(class_="pic-view-item")

            if(pic_view_items):
                review['pics'] = []
                for pic in pic_view_items:
                    review['pics'].append(pic['data-src'])

            res.append(review)

        if(not soup.find(class_="ui-pagination-next ui-pagination-disabled") and (max_pages < 0 or self.count < max_pages)):
            self.count += 1
            print(f'Opening page {self.count}')
            res += self.reviews(product_id, page+1, version, start_valid_date, i18n, translate, only_from_my_country, with_pictures, max_pages)

        return res

    # Scrap product page and get product-specific info
    def product(self, product_id):

        # Results container
        product = {}

        url = f'{self.item_uri}{product_id}.html'
        request = requests.get(url, headers=self.headers, cookies=self.cookies)

        target = ["title", "averageStar", "totalValidNum", "formatTradeCount"]
        match = re.search(r'data: ({.+})', request.text).group(1)
        data = json.loads(match)

        product['product_title'] = data['pageModule']['title'].strip()
        product['rating_average'] = data['titleModule']['feedbackRating']['averageStar']
        product['review_count'] = data['titleModule']['feedbackRating']['totalValidNum']
        product['orders_count'] = data['titleModule']['formatTradeCount']
        product['price'] = data['priceModule']['formatedPrice']

        return product


product_id = '1005001483534438'

crawliexpress = Crawliexpress(region='US')

crawliexpress_reviews_results = crawliexpress.reviews(product_id=product_id, translate=True, only_from_my_country=False, max_pages=40)
crawliexpress.save_csv(crawliexpress_reviews_results, f'dist/crawliexpress-reviews-{product_id}')

crawliexpress_product_result = crawliexpress.product(product_id)
print(crawliexpress_product_result)
