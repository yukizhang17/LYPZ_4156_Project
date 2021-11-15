import unittest
import os
import sys
import numpy as np

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

try:
    from application_services.price_fetching_services import \
        validate_optional_api_form_fields, reject_outliers, \
        fetch_item_amazon, fetch_keyword_amazon, fetch_item_bestbuy, \
        fetch_keyword_bestbuy, get_item_price_amazon, get_item_name_amazon, \
        get_keyword_avg_price_amazon, get_item_price_bestbuy, \
        get_item_name_bestbuy, get_keyword_avg_price_bestbuy, compare_prices
except Exception:
    raise


class Test_TestPriceFetchingServices(unittest.TestCase):

    # Testcase 1:
    def test_validate_optional_api_form_fields(self):
        form = {}
        field_lists = []

        self.assertTrue(validate_optional_api_form_fields(field_lists, form))

        field_lists.append(["keyword"])
        self.assertFalse(validate_optional_api_form_fields(field_lists, form))

        form["keyword"] = "nintendo switch"
        self.assertTrue(validate_optional_api_form_fields(field_lists, form))

        field_lists.append(["platform", "item_id"])
        self.assertTrue(validate_optional_api_form_fields(field_lists, form))

    # Testcase 2:
    def test_reject_outliers(self):
        array = [200, 20, 20, 20, 20, 20, 20, 20, 20]
        filtered_array_1 = reject_outliers(np.array(array), 1)
        self.assertEqual(len(array) - 1, len(filtered_array_1))

        filtered_array_2 = reject_outliers(np.array(filtered_array_1)).tolist()
        self.assertEqual(len(filtered_array_1), len(filtered_array_2))

    # Testcase 3:
    def test_fetch_item_amazon(self):
        sample_amazon_item_id = "B09KMXCPKP"
        res = fetch_item_amazon(sample_amazon_item_id)
        self.assertIsNotNone(res)

    # Testcase 4:
    def test_fetch_keyword_amazon(self):
        sample_keyword = "nintendo switch"
        res = fetch_keyword_amazon(sample_keyword)
        self.assertIsNotNone(res)

    # Testcase 5:
    def fetch_item_bestbuy(self):
        sample_best_buy_item_id = "6401728"
        res = fetch_item_bestbuy(sample_best_buy_item_id)
        self.assertIsNotNone(res)

    # Testcase 6:
    def fetch_keyword_bestbuy(self):
        sample_keyword = "nintendo switch"
        res = fetch_keyword_bestbuy(sample_keyword)
        self.assertIsNotNone(res)

    # Testcase 7:
    def test_get_item_price_amazon(self):
        sample_amazon_item_id = "B09KMXCPKP"
        res = fetch_item_amazon(sample_amazon_item_id)
        price = get_item_price_amazon(res)
        self.assertIsNotNone(price)

    # Testcase 8:
    def test_get_item_name_amazon(self):
        sample_amazon_item_id = "B09KMXCPKP"
        res = fetch_item_amazon(sample_amazon_item_id)
        name = get_item_name_amazon(res)
        self.assertIsNotNone(name)

    # Testcase 9:
    def test_get_keyword_avg_price_amazon(self):
        sample_keyword = "nintendo switch"
        res = fetch_keyword_amazon(sample_keyword)
        price = get_keyword_avg_price_amazon(res)
        self.assertIsNotNone(price)

    # Testcase 10:
    def test_get_item_price_bestbuy(self):
        sample_best_buy_item_id = "6401728"
        res = fetch_item_bestbuy(sample_best_buy_item_id)
        price = get_item_price_bestbuy(res)
        self.assertIsNotNone(price)

    # Testcase 11:
    def test_get_item_name_bestbuy(self):
        sample_best_buy_item_id = "6401728"
        res = fetch_item_bestbuy(sample_best_buy_item_id)
        name = get_item_name_bestbuy(res)
        self.assertIsNotNone(name)

    # Testcase 12:
    def test_get_keyword_avg_price_bestbuy(self):
        sample_keyword = "nintendo switch"
        res = fetch_keyword_bestbuy(sample_keyword)
        price = get_keyword_avg_price_bestbuy(res)
        self.assertIsNotNone(price)

    # Testcase 13:
    def test_compare_prices(self):
        sample_keyword = "nintendo switch"
        sample_amazon_item_id = "B09KMXCPKP"
        sample_best_buy_item_id = "6401728"

        res_1 = compare_prices(sample_keyword)
        self.assertIsNotNone(res_1)

        res_2 = compare_prices(None, sample_amazon_item_id, 'amazon')
        self.assertIsNotNone(res_2)

        res_3 = compare_prices(None, sample_best_buy_item_id, 'bestbuy')
        self.assertIsNotNone(res_3)


if __name__ == '__main__':
    unittest.main()
