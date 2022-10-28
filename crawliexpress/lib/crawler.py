import csv
import math
import requests
import urllib.parse
import random
import time
import json
import re

from bs4 import BeautifulSoup

class AliexpressCrawler:
    
    # Set default request parameters
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36', 
    }
    cookies = {
        "intl_locale": "",
        "aep_usuc_f": "",
    }
    item_uri = 'https://www.aliexpress.com/item/'
    feedback_uri = "https://feedback.aliexpress.com/display/productEvaluation.htm"

    def __init__(self, owner_member_id="", company_id="", member_type="seller", region="US", locale="en_US", currency="USD", country="usa"):

        self.owner_member_id = owner_member_id or self.generate_id()
        self.company_id = company_id or self.generate_id()
        self.cookies['intl_locale'] = f'{locale}'
        self.cookies['aep_usuc_f'] = f'isfm=y&site={country}&c_tp={currency}&region={region}&b_locale={locale}'
        self.member_type = member_type
        self.count = 1

        print(f'Crawliexpress - Region: {region} | Country: {country} | Locale: {locale} | Currency: {currency} | Member ID: {self.owner_member_id} | Company ID: {self.company_id}')

    # Generate random ID
    @staticmethod
    def generate_id(length=9, suffix =2):
        numbers =  range(0,10)
        id = f'{suffix}'
        for i in range(0, length-1):
            id = f'{id}{random.choice(numbers)}'
        return id

    # Reduce text size to fit in prints
    @staticmethod
    def truncate(text, max=20):
        return f'{text[0:max]}...' if len(text) > max else text

    def search(self, search_text, page=1, sort_type="default"):

        request = requests.get(
        f"https://www.aliexpress.com/wholesale?SearchText={search_text}&page={page}&SortType={sort_type}")

        # Find all products
        match = re.search(r'window.runParams = ({.+})', request.text).group(1)
        products = json.loads(match)['mods']['itemList']['content']

        return products

    def review_count(self, product_id, page=1, version="2", start_valid_date="", i18n=False, translate=False, only_from_my_country=False, with_pictures=False, max_pages=-1, exists=False):

        params = {
            'productId': product_id,
            'v': version,
            'ownerMemberId': self.owner_member_id,
            'companyId': self.company_id,
            'memberType': self.member_type,
            'evaStarFilterValue': 'all Stars',
            'evaSortValue': 'sortdefault@feedback',
            'page': page,
            'currentPage': page,
            'startValidDate': None, 
            'i18n': 'true' if i18n else 'false',
            'withPictures':  'true' if with_pictures else 'false',
            'withAdditionalFeedback': 'false',
            'onlyFromMyCountry':  'true' if only_from_my_country else 'false',
            'version': None,
            'isOpened': 'true',
            'translate': 'Y' if translate else 'N',
            'jumpToTop': 'false'
        }

        url = f"{self.feedback_uri}?{urllib.parse.urlencode(params)}"

        request = requests.get(url, headers=self.headers, cookies=self.cookies)
        review_count = 0

        try:
            soup = BeautifulSoup(request.content, 'html.parser')
            all_stars = soup.find(class_='fb-star-selector')
            review_count = int(all_stars.find('em').text)
        except:
            pass

        return review_count

    # Find all products that include reviews
    def with_reviews(self, search_text, with_pictures=False, max_pages=1):

        products_with_reviews = []
        self.count = 0

        while self.count < max_pages:
            print(f'Crawliexpress - With reviews | Page: {self.count}')
            products = self.search(search_text, page=self.count)
            for product in products:

                product_id = product['productId']
                product_url = f"{self.item_uri}{product_id}.html"
                review_count_nsfw = self.review_count(product_id=product_id, with_pictures=with_pictures)

                print(f'Crawliexpress - With reviews | Product ID: {product_id} | Review count: {review_count_nsfw} | URL: {product_url}')

                if(review_count_nsfw > 0):
                    products_with_reviews.append(product)

            self.count += 1
            
            
        return products_with_reviews

    # Scrap through review pages on aliexpress product (Recursive)
    def reviews(self, product_id, page=1, version="2", start_valid_date="", i18n=False, translate=False, only_from_my_country=False, with_pictures=False, max_pages=-1, exists=False):

        if (not exists):
            product_listing = self.product(product_id)
            if (product_listing):
                print(json.dumps(product_listing, indent=2))
                exists = True
            else:
                print('Crawliexpress - Reviews | Error: Invalid Product ID')
                return False 

        print(f'Crawliexpress - Reviews | Product ID: {product_id} - Page: {page}')

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

            # BUYER FEEDBACK
            review['text'] = buyer_feedback.contents[1].text.strip()
            review['date'] = buyer_feedback.contents[3].text.strip()

            # STAR COUNT
            star_view_percentage = item.find(class_='star-view').contents[0]['style'].split(':')[1].replace('%', '')
            review['rating'] = math.floor(int(star_view_percentage)/20)

            # PRODUCT ATTRIBUTES (VARIATONS, SHIPS FROM, SHIPPING METHOD)
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
            res += self.reviews(product_id, page+1, version, start_valid_date, i18n, translate, only_from_my_country, with_pictures, max_pages, exists)

        return res
            
    # Scrap product page and get product-specific info
    def product(self, product_id):

        print(f'Crawliexpress - Product listing info | Product ID: {product_id}')

        # Results container
        product = {}

        url = f'{self.item_uri}{product_id}.html'
        request = requests.get(url, headers=self.headers, cookies=self.cookies)

        if(request.status_code != 200):
            print('- Error: Invalid Product ID')
            return False

        match = re.search(r'data: ({.+})', request.text).group(1)
        data = json.loads(match)

        product['product_title'] = data['pageModule']['title'].strip()
        product['rating_average'] = data['titleModule']['feedbackRating']['averageStar']
        product['review_count'] = data['titleModule']['feedbackRating']['totalValidNum']
        product['orders_count'] = data['titleModule']['formatTradeCount']
        product['price'] = data['priceModule']['formatedPrice']

        return product

    def categories(self):
      
        # Results container
        res = []
        categories = None
        count = 0
        timeout = False
        
        with open('./utils/categories.json') as fp:
            categories = json.load(fp)

        for key in categories:

            count += 1

            # if(count > 10):
            #     break

            url = f'{categories[key]}?SortType=total_tranpro_desc'
            print(f'Crawliexpress - Categories | Url {url} - {count}/{len(categories)}')

            request = requests.get(url, headers=self.headers, cookies=self.cookies)

            if(request.status_code != 200):
                print('- Error: Invalid category page')

            try:
                match = re.search(r'window.runParams = ({.+})', request.text).group(1)
                items = json.loads(match)['items']
                timeout = False
            except:
                print(f'- Error: No search results')
                if(timeout):
                    pass
                    # print('- Warning: Too much requests, waiting for 10 seconds before next request')
                    # time.sleep(10)
                timeout = True
                continue

            for item in items:

                aux = {}
                
                aux['product_id'] = item['productDetailUrl'].split('item/')[1].split('.html')[0]
                aux['image_url'] = item['imageUrl']
                aux['price'] = item['price']
                aux['title'] = item['title']
                if 'tradeDesc' in item:
                    aux['order_count'] = int((item['tradeDesc']).split(' ')[0])
                else:
                    aux['order_count'] = 0

                res.append(aux)
        
        res.sort(key=lambda x: x.get('order_count'))

        return res     