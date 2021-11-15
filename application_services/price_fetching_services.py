import requests
import json
import numpy as np
import traceback
from bs4 import BeautifulSoup
from datetime import datetime

# use selenium to fetch web page when it is fully loaded
from selenium import webdriver
import undetected_chromedriver as uc

options = webdriver.ChromeOptions() 
options.headless = True
driver = uc.Chrome(options=options)

#driver = webdriver.PhantomJS(executable_path='/usr/local/lib/node_modules/phantomjs-prebuilt/lib/phantom/bin/phantomjs') # or add to your PATH
# driver = webdriver.PhantomJS()

#options = webdriver.ChromeOptions()
#options.add_argument('--headless')
#chrome_service = Service(ChromeDriverManager().install())
#driver = webdriver.Chrome(service=chrome_service, options=options)

AMAZON_DOMAIN = "https://www.amazon.com"
BESTBUY_DOMAIN = "https://www.bestbuy.com/site"
BESTBUY_API_BASE = "https://api.bestbuy.com/v1/products"
BESTBUY_API_KEY = "nU3Uo9RMMpqKmrhpm2if81bl"


# check if at least one list of fields are included in the api form
def validate_optional_api_form_fields(field_lists, form):
	for fields in field_lists:
		all_included = True
		for field in fields:
			if field not in form:
				all_included = False
		if all_included is True:
			return True
	return False

# reject outlier data points which are likely not the target product 
def reject_outliers(data, m=2):
	# choose the median of the first 10 items as reference sample
	d = np.abs(data - np.median(data[:10]))
	mdev = np.median(d)
	s = d/mdev if mdev else 0.
	return data[s<m]

# get amazon product web page
def fetch_item_amazon(item_id):
	try:
		url = AMAZON_DOMAIN + "/dp/{}/".format(item_id)
		# print(url)
		driver.get(url)
		response = driver.page_source
		return response
	except Exception as e:
		# print(e)
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
		# print(e)
		traceback.print_exc()
		return None

# get bestbuy product information
def fetch_item_bestbuy(item_id):
	try:
		url = BESTBUY_API_BASE + "/{}.json?apiKey={}".format(item_id, BESTBUY_API_KEY)
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
		# print(e)
		traceback.print_exc()
		return None

# get bestbuy keyword search web page
def fetch_keyword_bestbuy(keyword):
	try:
		keyword = '+'.join(keyword.split(' '))
		url = BESTBUY_DOMAIN + "/searchpage.jsp?st={}".format(keyword)
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
		# print(e)
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
		price = float(price_string[1:])
		return price
	except Exception as e:
		# print(e)
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
		# print(e)
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
			item_id = item_div['data-asin']

			if keyword is not None:
				name_span = item_div.find('span', class_= 'a-size-medium a-color-base a-text-normal')
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
			inner_price_span = outer_price_span.find('span', class_='a-offscreen')
			price = float(inner_price_span.text[1:])
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
		# print(e)
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
		# print(e)
		traceback.print_exc()
		return None

# get product name from bestbuy product information
def get_item_name_bestbuy(response):
	try:
		response_json = json.loads(response.content)
		name = response_json['name']
		return name
	except Exception as e:
		# print(e)
		traceback.print_exc()
		return None

# get average product price from bestbuy keyword search web page
def get_keyword_avg_price_bestbuy(response, keyword=None):
	try:
		content = response.content
		soup = BeautifulSoup(content, 'html.parser')
		search_results = soup.select('li.sku-item')

		prices = []
		for i, item_li in enumerate(search_results):
			item_id = item_li['data-sku-id']

			if keyword is not None:
				header_h4 = item_li.find('h4', class_= 'sku-header')
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
			price = float(price_span.text[1:])
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
		# print(e)
		traceback.print_exc()
		return None

# comare prices of a product or a keyword
def compare_prices(keyword, item_id=None, platform=None):
	try:
		result = {}

		# if the price of a keyword is to be compared
		if keyword is not None:
			# get amazon average price of products from the search results
			# of the keyword
			keyword_res_amazon = fetch_keyword_amazon(keyword)
			amazon_price = get_keyword_avg_price_amazon(keyword_res_amazon)

			# get bestbuy average price of products from the search results
			# of the keyword
			keyword_res_bestbuy = fetch_keyword_bestbuy(keyword)
			bestbuy_price = get_keyword_avg_price_bestbuy(keyword_res_bestbuy)

		# if the price of a product is to be compared
		if item_id is not None and platform is not None:
			# if the product to be compared is from amazon
			if platform == 'amazon':
				# get amazon price of the product
				item_res = fetch_item_amazon(item_id)
				amazon_price = get_item_price_amazon(item_res) 
				
				# use the product name as keyword
				keyword = get_item_name_amazon(item_res)

				# get bestbuy average price of products from the search results
				# of the keyword
				keyword_res_bestbuy = fetch_keyword_bestbuy(keyword)
				bestbuy_price = get_keyword_avg_price_bestbuy(keyword_res_bestbuy, keyword)
			# if the product to be compared is from bestbuy
			elif platform == 'bestbuy':
				# get bestbuy price of the product
				item_res = fetch_item_bestbuy(item_id)
				bestbuy_price = get_item_price_bestbuy(item_res)
				
				# use the product name as keyword
				keyword = get_item_name_bestbuy(item_res)

				# get bestbuy average price of products from the search results
				# of the keyword
				keyword_res_amazon = fetch_keyword_amazon(keyword)
				amazon_price = get_keyword_avg_price_amazon(keyword_res_amazon, keyword)

		if amazon_price is None and bestbuy_price is None:
			return None

		timestamp = str(datetime.utcnow())

		result['amazon_price'] = amazon_price
		result['bestbuy_price'] = bestbuy_price
		result['timestamp'] = timestamp

		return result

	except Exception as e:
		# print(e)
		traceback.print_exc()
		return None

if __name__ == '__main__':
	# Nintendo Switch (Grey)
	sample_amazon_item_id = "B09KMXCPKP"
	# Nintendo - Switch - Animal Crossing: New Horizons Edition 32GB Console - Multi
	sample_best_buy_item_id = "6401728"
	sample_keyword = "nintendo switch"

	# amazon
	# item_res_amazon = fetch_item_amazon(sample_amazon_item_id)
	# keyword_res_amazon = fetch_keyword_amazon(sample_keyword)
	
	# get_item_price_amazon(sample_amazon_item_id)
	# get_item_name_amazon(item_res_amazon)
	# get_keyword_avg_price_amazon(keyword_res_amazon)
	
	# bestbuy
	# item_res_bestbuy = fetch_item_bestbuy(sample_best_buy_item_id)
	# keyword_res_bestbuy = fetch_keyword_bestbuy(sample_keyword)

	# get_item_price_bestbuy(item_res_bestbuy)
	# get_item_name_bestbuy(item_res_bestbuy)
	# get_keyword_avg_price_bestbuy(keyword_res_bestbuy)

	# compare price keyword
	# res = compare_prices(sample_keyword)
	# # print(res)
	
	# compare price item amazon
	# res = compare_prices(None, sample_amazon_item_id, 'amazon')
	# # print(res)
	
	# compare price item bestbuy
	# res = compare_prices(None, sample_best_buy_item_id, 'bestbuy')
	# print(res)


 