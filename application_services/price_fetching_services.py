import requests
import json
import numpy as np
import traceback
from bs4 import BeautifulSoup
from datetime import datetime, date
from selenium import webdriver
import os


# local host config
# PANTHOMJS_PATH = 'C://software//phantomjs-2.1.1-windows//bin//phantomjs.exe'
# driver = webdriver.PhantomJS(
#     executable_path=PANTHOMJS_PATH, 
#     service_log_path=os.path.devnull
# )

# aws lambda config
# PANTHOMJS_PATH = '/opt/phantomjs-2.1.1-linux-x86_64/bin/phantomjs'
# driver = webdriver.PhantomJS(
#     executable_path=PANTHOMJS_PATH, 
#     service_log_path=os.path.devnull
# )

# github CI config
print(os.getcwd())
PANTHOMJS_PATH = '/home/runner/work/LYPZ_4156_Project/LYPZ_4156_Project/lib/phantomjs-2.1.1-linux-x86_64/bin/phantomjs'
driver = webdriver.PhantomJS(
    executable_path=PANTHOMJS_PATH, 
    service_log_path=os.path.devnull
)


AMAZON_DOMAIN = "https://www.amazon.com"
BESTBUY_DOMAIN = "https://www.bestbuy.com/site"
BESTBUY_API_BASE = "https://api.bestbuy.com/v1/products"
BESTBUY_API_KEY = "nU3Uo9RMMpqKmrhpm2if81bl"


# local host config
# DB_URL = "http://127.0.0.1:5000/"


# aws lambda & github CI config
DB_URL = "https://whispering-peak-99211.herokuapp.com/"


DB_SELECT_URL = DB_URL + 'query-select'
DB_UPDATE_URL = DB_URL + 'query-update'


# check if at least one list of fields are included in the api form
def validate_optional_api_form_fields(field_lists, form):
    if len(field_lists) == 0:
        return True
    for fields in field_lists:
        all_included = True
        for field in fields:
            if field not in form:
                all_included = False
        if all_included is True:
            return True
    return False


# reject outlier data points which are likely not the target product
def reject_outliers(data, m=2.):
    # choose the median of the first 10 items as reference sample
    d = np.abs(data - np.median(data[:10]))
    mdev = np.median(d)
    s = d / (mdev if mdev else 1.)
    res = data[s < m]
    if len(res) > 0 and isinstance(res[0], np.ndarray):
        res = res[0]
    return res


# get amazon product web page
def fetch_item_amazon(item_id):
    try:
        url = AMAZON_DOMAIN + "/dp/{}/".format(item_id)
        # print(url)
        driver.get(url)
        response = driver.page_source
        return response
    except Exception as e:
        print(e)
        traceback.print_exc()
        return None


# get amazon keyword search web page
def fetch_keyword_amazon(keyword):
    try:
        keyword = '+'.join(keyword.split(' '))
        url = AMAZON_DOMAIN + "/s?k={}".format(keyword)
        # print(url)
        driver.get(url)
        response = driver.page_source
        return response
    except Exception as e:
        print(e)
        traceback.print_exc()
        return None


# get bestbuy product information
def fetch_item_bestbuy(item_id):
    try:
        url = BESTBUY_API_BASE + "/{}.json?apiKey={}".format(
            item_id, BESTBUY_API_KEY
        )
        headers = {
            "User-Agent": "PostmanRuntime/7.28.4",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept": "*/*",
            "Connection": "close",
        }
        # print(url)
        response = requests.get(url, headers=headers)
        return response
    except Exception as e:
        print(e)
        traceback.print_exc()
        return None


# get bestbuy keyword search web page
def fetch_keyword_bestbuy(keyword):
    try:
        keyword = '+'.join(keyword.split(' '))
        url = BESTBUY_DOMAIN + "/searchpage.jsp?st={}".format(keyword)
        # print(url)
        headers = {
			"User-Agent": "PostmanRuntime/7.28.4", 
			"Accept-Encoding": "gzip, deflate, br", 
			"Accept": "*/*", 
			"Connection": "close", 
		}
        response = requests.get(url, headers=headers)
        
        # driver.get(url)
        # response = driver.page_source

        return response
    except Exception as e:
        print(e)
        traceback.print_exc()
        return None


# get product price from amazon product web page
def get_item_price_amazon(response):
    try:
        content = response
        soup = BeautifulSoup(content, 'html.parser')
        info = soup.find('div', {'class': 'cardRoot'})

        if info is None:
            return None

        data = json.loads(info['data-components'])
        price_string = data['1']['price']['displayString']
        price = float(price_string[1:].replace(',', ''))
        return price
    except Exception as e:
        print(e)
        traceback.print_exc()
        return None


# get product name from amazon product web page
def get_item_name_amazon(response):
    try:
        content = response
        soup = BeautifulSoup(content, 'html.parser')
        title_span = soup.find('span', {'id': 'productTitle'})

        if title_span is None:
            return None

        full_title = title_span.text.strip()
        general_title = full_title.split(',')[0]

        return general_title
    except Exception as e:
        print(e)
        traceback.print_exc()
        return None


# get average product price from amazon keyword search web page
def get_keyword_avg_price_amazon(response, keyword=None):
    try:
        content = response
        soup = BeautifulSoup(content, 'html.parser')
        search_results = soup.select('div.s-result-item.s-asin')
        prices = []
        for i, item_div in enumerate(search_results):
            # item_id = item_div['data-asin']

            if keyword is not None:
                name_span = item_div.find(
                    'span', class_='a-size-medium a-color-base a-text-normal'
                )
                if name_span is None:
                    continue
                name = name_span.text
                # skip if the item is a complementary product
                complementary_str = 'for ' + keyword.split(' ')[0]
                if complementary_str in name:
                    continue

            outer_price_span = item_div.find('span', class_='a-price')
            if outer_price_span is None:
                continue
            inner_price_span = outer_price_span.find(
                'span', class_='a-offscreen'
            )
            price = float(inner_price_span.text[1:].replace(',', ''))
            prices.append(price)

            # get the top 20 products if there are more than 20
            if len(prices) == 20:
                break

        if len(prices) == 0:
            return None
        # print(prices)
        filtered_prices = reject_outliers(np.array(prices), 3)
        avg_price = round(np.mean(filtered_prices), 2)
        return avg_price
    except Exception as e:
        print(e)
        traceback.print_exc()
        return None


# get product price from bestbuy product information
def get_item_price_bestbuy(response):
    try:
        response_json = json.loads(response.content)
        if response_json['onSale'] is False:
            price = response_json['regularPrice']
        else:
            price = response_json['salePrice']
        return price
    except Exception as e:
        print(e)
        traceback.print_exc()
        return None


# get product name from bestbuy product information
def get_item_name_bestbuy(response):
    try:
        response_json = json.loads(response.content)
        name = response_json['name']
        return name
    except Exception as e:
        print(e)
        traceback.print_exc()
        return None


# get average product price from bestbuy keyword search web page
def get_keyword_avg_price_bestbuy(response, keyword=None):
    try:
        content = response.content
        #content = response
        soup = BeautifulSoup(content, 'html.parser')
        search_results = soup.select('li.sku-item')

        prices = []
        for i, item_li in enumerate(search_results):
            # item_id = item_li['data-sku-id']

            if keyword is not None:
                header_h4 = item_li.find('h4', class_='sku-header')
                if header_h4 is None:
                    continue
                name_link = header_h4.find('a')
                if name_link is None:
                    continue
                name = name_link.text
                # skip if the item is a complementary product
                complementary_str = 'for ' + keyword.split(' ')[0]
                if complementary_str in name:
                    continue

            price_div = item_li.find('div', class_='priceView-customer-price')
            if price_div is None:
                continue
            price_span = price_div.find('span')
            price = float(price_span.text[1:].replace(',', ''))
            prices.append(price)

            # get the top 20 products if there are more than 20
            if len(prices) == 20:
                break

        if len(prices) == 0:
            return None

        filtered_prices = reject_outliers(np.array(prices), 1)
        avg_price = round(np.mean(filtered_prices), 2)

        return avg_price
    except Exception as e:
        print(e)
        traceback.print_exc()
        return None


# comare prices of a product or a keyword
# def compare_prices(keyword, item_id=None, platform=None):
#     try:
#         result = {}

#         # if the price of a keyword is to be compared
#         if keyword is not None:
#             # get amazon average price of products from the search results
#             # of the keyword
#             keyword_res_amazon = fetch_keyword_amazon(keyword)
#             amazon_price = get_keyword_avg_price_amazon(keyword_res_amazon)

#             # get bestbuy average price of products from the search results
#             # of the keyword
#             keyword_res_bestbuy = fetch_keyword_bestbuy(keyword)
#             bestbuy_price = get_keyword_avg_price_bestbuy(keyword_res_bestbuy)

#         # if the price of a product is to be compared
#         if item_id is not None and platform is not None:
#             # if the product to be compared is from amazon
#             if platform == 'amazon':
#                 # get amazon price of the product
#                 item_res = fetch_item_amazon(item_id)
#                 amazon_price = get_item_price_amazon(item_res)

#                 # use the product name as keyword
#                 keyword = get_item_name_amazon(item_res)

#                 # get bestbuy average price of products from the search results
#                 # of the keyword
#                 keyword_res_bestbuy = fetch_keyword_bestbuy(keyword)
#                 bestbuy_price = get_keyword_avg_price_bestbuy(
#                     keyword_res_bestbuy, keyword
#                 )
#             # if the product to be compared is from bestbuy
#             elif platform == 'bestbuy':
#                 # get bestbuy price of the product
#                 item_res = fetch_item_bestbuy(item_id)
#                 bestbuy_price = get_item_price_bestbuy(item_res)

#                 # use the product name as keyword
#                 keyword = get_item_name_bestbuy(item_res)

#                 # get bestbuy average price of products from the search results
#                 # of the keyword
#                 keyword_res_amazon = fetch_keyword_amazon(keyword)
#                 amazon_price = get_keyword_avg_price_amazon(
#                     keyword_res_amazon, keyword
#                 )

#         if amazon_price is None and bestbuy_price is None:
#             return None

#         timestamp = str(datetime.utcnow())

#         result['amazon_price'] = amazon_price
#         result['bestbuy_price'] = bestbuy_price
#         result['timestamp'] = timestamp

#         return result

#     except Exception as e:
#         print(e)
#         traceback.print_exc()
#         return None


# log product prices
def log_product_prices():

    form = {
        'access_token': 'NizHtF)sqL*{#[Cc#sp30um!Kt6pu!',
        'table': 'subscription_product_id'
    }
    
    # get subscribed product ids from db
    res = requests.get(DB_SELECT_URL, data=form)
    subscribed_items = res.json()

    if subscribed_items is None:
        return 0

    count = 0
    # for each subsribed item, fetch price
    for item_record in subscribed_items:
        try:
            sid = item_record[0]
            item_id = item_record[1]
            url = item_record[2]
            price_history = item_record[3]

            # check if the item is from amazon or bestbuy and fetch price
            price = None
            if 'amazon' in url:
                item_res = fetch_item_amazon(item_id)
                price = get_item_price_amazon(item_res)
            elif 'bestbuy' in url:
                item_res = fetch_item_bestbuy(item_id)
                price = get_item_price_bestbuy(item_res)

            # if price is None, log nothing
            if price is None:
                price = 'None'
            
            # format today's date
            today = str(date.today()).replace('-', '/')

            # create price record
            record = today + '-' + str(price)

            if price_history is None or price_history == '':
                price_history = record

            price_history += ',' + record

            form['where_sid'] = sid
            form['update_price_history'] = price_history

            # log price history
            res = requests.post(DB_UPDATE_URL, data=form)
            count += 1
        except Exception as e:
            print(e)
            traceback.print_exc()
            return count
    
    return count

# log keyword prices
def log_keyword_prices():
    
    form = {
        'access_token': 'NizHtF)sqL*{#[Cc#sp30um!Kt6pu!',
        'table': 'subscription_keyword'
    }
    
    # get subscribed keywords from db
    res = requests.get(DB_SELECT_URL, data=form)
    subscribed_keywords = res.json()

    if subscribed_keywords is None:
        return 0

    count = 0
    # for each subsribed keyword, fetch price from amazon and bestbuy
    for keyword_record in subscribed_keywords:
        try:
            sid = keyword_record[0]
            keyword = keyword_record[1]
            price_history = keyword_record[2]

            # fetch keyword average price from amazon and bestbuy
            amazon_keyword_res = fetch_keyword_amazon(keyword)
            amazon_price = get_keyword_avg_price_amazon(amazon_keyword_res)

            bestbuy_keyword_res = fetch_keyword_bestbuy(keyword)
            bestbuy_price = get_keyword_avg_price_bestbuy(bestbuy_keyword_res)

            # format today's date
            today = str(date.today()).replace('-', '/')

            # create price records
            if amazon_price is None:
                amazon_price = 'None'
            amazon_record = 'amazon' + '-' + today + '-' + str(amazon_price)

            if bestbuy_price is None:
                bestbuy_price = 'None'
            bestbuy_record = 'bestbuy' + '-' + today + '-' + str(bestbuy_price)

            if price_history is None or price_history == '':
                price_history = amazon_record + ',' + bestbuy_record

            price_history += ',' + amazon_record + ',' + bestbuy_record

            form['where_sid'] = sid
            form['update_price_history'] = price_history

            # log price history
            res = requests.post(DB_UPDATE_URL, data=form)
            count += 1
        except Exception as e:
            print(e)
            traceback.print_exc()
            return count
    
    return count

if __name__ == '__main__':
    # Nintendo Switch (Grey)
    sample_amazon_item_id = "B09KMXCPKP"
    # Nintendo - Switch - Animal Crossing: New Horizons Edition 32GB Console
    # - Multi
    sample_best_buy_item_id = "6401728"
    sample_keyword = "yeezy"

    # amazon
    # item_res_amazon = fetch_item_amazon(sample_amazon_item_id)
    # keyword_res_amazon = fetch_keyword_amazon(sample_keyword)

    # amazon_item_price = get_item_price_amazon(sample_amazon_item_id)
    # amazon_item_name = get_item_name_amazon(item_res_amazon)
    # amazon_keyword_price = get_keyword_avg_price_amazon(keyword_res_amazon)

    # print(amazon_item_price)
    # print(amazon_item_name)
    # print(amazon_keyword_price)

    # bestbuy
    # item_res_bestbuy = fetch_item_bestbuy(sample_best_buy_item_id)
    # keyword_res_bestbuy = fetch_keyword_bestbuy(sample_keyword)

    # get_item_price_bestbuy(item_res_bestbuy)
    # get_item_name_bestbuy(item_res_bestbuy)
    # avg_price = get_keyword_avg_price_bestbuy(keyword_res_bestbuy)

    # compare price keyword
    # res = compare_prices(sample_keyword)
    # # print(res)

    # compare price item amazon
    # res = compare_prices(None, sample_amazon_item_id, 'amazon')
    # # print(res)

    # compare price item bestbuy
    # res = compare_prices(None, sample_best_buy_item_id, 'bestbuy')
    # print(res)

    # log_product_prices()
    # log_keyword_prices()