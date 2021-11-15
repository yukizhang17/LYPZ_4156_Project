import unittest
import os
import sys

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from application_services.subscribe import get_subscribe_input
from application_services.subscribe import subscribe_product, generate_website
from application_services.subscribe import unsubscribe_product
from application_services.subscribe import get_unsubscribe_input

class Test_Testsubscribe(unittest.TestCase):

    # Testcase 1: Test get subscribe input with keyword, product id
    def test_get_subscribe_input(self):
        # Test input with no platform
        form1 = {
            "product": "ps5", "type": "keyword", "expected_price": "10.99"}
        respond1 = (200, {
            "product": "ps5", "type": "keyword", "platform": None,
            "expected_price": 10.99})
        self.assertEqual(get_subscribe_input(form1), respond1)

        # Test input with no platform, no expected_price
        form2 = {"product": "ps5", "type": "keyword"}
        respond2 = (200, {
            "product": "ps5", "type": "keyword",
            "platform": None, "expected_price": None})
        self.assertEqual(get_subscribe_input(form2), respond2)

        # Test missing required platform
        form3 = {"product": "B07H39W49R", "type": "productID"}
        respond3 = (400, "missing required fields")
        self.assertEqual(get_subscribe_input(form3), respond3)

        # Test correct input
        form4 = {
            "product": "B07H39W49R", "type": "productID", "platform": "Amazon"}
        respond4 = (200, {
            "product": "B07H39W49R", "type": "productID",
            "platform": "Amazon", "expected_price": None})
        self.assertEqual(get_subscribe_input(form4), respond4)

    # Testcase 2: Test subscribe with keyword
    def test_subscribe_product_keyword(self):
        # Test regular subscribe
        product = "ps5"
        type = "keyword"
        expected_price = 10.99
        platform = None
        uid = "1111"
        respond1 = (200, "Subscribed successfully!")
        self.assertEqual(
            subscribe_product(
                uid, product, type, platform, expected_price), respond1)

        # Test update price
        expected_price = 12.99
        respond2 = (200, "Subscripted expected price updated!")
        self.assertEqual(
            subscribe_product(
                uid, product, type, platform, expected_price), respond2)

        # Test repeated subscribe
        respond3 = (400, "User has subscribed the same keyword!")
        self.assertEqual(
            subscribe_product(
                uid, product, type, platform, expected_price), respond3)

        # Test another user subscribe the same keyword
        uid2 = "3333"
        respond4 = (200, "Subscribed successfully!")
        self.assertEqual(
            subscribe_product(
                uid2, product, type, platform, expected_price), respond4)

        # Test missing keyword
        product = None
        respond5 = (400, "missing keyword")
        self.assertEqual(
            subscribe_product
            (uid, product, type, platform, expected_price), respond5)

    # Testcase 3: Test subscribe with productID
    def test_subscribe_product_productID(self):
        product = "B07H39W49R"
        type = "productID"
        platform = "Amazon"
        expected_price = 10.99
        uid = "1111"

        # Test regular subscribe
        respond1 = (200, "Subscribed successfully!")
        self.assertEqual(subscribe_product(
            uid, product, type, platform, expected_price), respond1)

        # Test subscribe with incurrect platform
        respond2 = (400, "Incurrect platform, Amazon or BestBuy, try again.")
        self.assertEqual(subscribe_product(
            uid, product, type, "Amazon1", expected_price), respond2)

    # Testcase 4: Test generate_website currectly
    def test_generate_website(self):
        platform1 = "BestBuy"
        product1 = "1111111"
        platform2 = "Amazon"
        product2 = "2222222"

        respond1 = (200, "https://api.bestbuy.com/click/-/1111111/pdp")
        self.assertEqual(generate_website(platform1, product1), respond1)

        respond2 = (200, "https://www.amazon.com/gp/product/2222222")
        self.assertEqual(generate_website(platform2, product2), respond2)

        platform3 = "Target"
        respond3 = (400, "Incurrect platform, Amazon or BestBuy, try again.")
        self.assertEqual(generate_website(platform3, product2), respond3)

    # Testcase 5: Test get unsubscribe input with keyword, product id
    def test_get_unsubscribe_input(self):
        # Test input with no platform
        form1 = {"product": "ps5", "type": "keyword"}
        respond1 = (200, {
            "product": "ps5", "type": "keyword", "platform": None})
        self.assertEqual(get_unsubscribe_input(form1), respond1)

        # Test input unsubscribe productID with no platform
        form2 = {"product": "B07H39W49R", "type": "productID"}
        respond2 = (400, "unsubscribe with productID, platform can't be Null")
        self.assertEqual(get_unsubscribe_input(form2), respond2)

        # Test correct input
        form4 = {
            "product": "B07H39W49R", "type": "productID", "platform": "Amazon"}
        respond4 = (
            200,
            {
                "product": "B07H39W49R",
                "type": "productID",
                "platform": "Amazon"
            }
            )
        self.assertEqual(get_unsubscribe_input(form4), respond4)

    # Testcase 6: Test unsubscribe with keyword
    def test_unsubscribe_product_keyword(self):
        product = "ps5"
        type = "keyword"
        expected_price = 10.99
        platform = None
        uid = "1111"

        subscribe_product(uid, product, type, platform, expected_price)

        # Test wrong keyword
        respond1 = (200, "No record, check keyword, try again.")
        self.assertEqual(
            unsubscribe_product(uid, "ps7", type, platform), respond1)

        # Test user never subscribe this keyword
        respond2 = (400, "User never subscribe this keyword!")
        self.assertEqual(
            unsubscribe_product("2222", product, type, platform), respond2)

        # Test currect unsubscribe
        respond3 = (200, "Unsubscribe successfully!")
        self.assertEqual(
            unsubscribe_product(uid, product, type, platform), respond3)

    # Testcase 7: Test unsubscribe with productID
    def test_unsubscribe_product_productID(self):
        product = "B1234567"
        type = "productID"
        platform = "Amazon"
        expected_price = 10.99
        uid = "1111"

        subscribe_product(uid, product, type, platform, expected_price)

        # Test wrong type subscribe
        respond1 = (400, "Incurrect type: keyword or productID, try again.")
        self.assertEqual(
            unsubscribe_product(
                uid, product, "productName", platform), respond1)

        # Test unsubscribe with incurrect platform
        respond2 = (400, "Incurrect platform, Amazon or BestBuy, try again.")
        self.assertEqual(
            unsubscribe_product(uid, product, type, "Amazon1"), respond2)

        # Test unsubscribe incurrect product_ID
        respond3 = (
            400, "No record, check product_ID and platform, try again.")
        self.assertEqual(
            unsubscribe_product(uid, "B00000000", type, platform), respond3)

        # Test user never subscribe this product
        uid = "2222"
        respond4 = (400, "User never subscribe this product!")
        self.assertEqual(
            unsubscribe_product(uid, product, type, platform), respond4)

        # Test another user subscribe the same product
        uid2 = "1111"
        respond5 = (200, "Unsubscribe successfully!")
        self.assertEqual(
            unsubscribe_product(uid2, product, type, platform), respond5)

    # Testcase 8: Test subscribed productID has been subscribed before
    def test_subscribe_productID(self):
        product = "B2345678"
        type = "productID"
        platform = "Amazon"
        expected_price = 20.99
        uid = "8000"

        subscribe_product(uid, product, type, platform, expected_price)

        # Test update price
        expected_price = 18.99
        respond3 = (200, "Subscripted expected price updated!")
        self.assertEqual(
            subscribe_product(
                uid, product, type, platform, expected_price), respond3)

        # Test repeated subscribe
        respond4 = (400, "User has subscribed the same product!")
        self.assertEqual(
            subscribe_product(
                uid, product, type, platform, expected_price), respond4)

        # Test another user subscribe the same product
        uid2 = "9000"
        respond5 = (200, "Subscribed successfully!")
        self.assertEqual(
            subscribe_product(
                uid2, product, type, platform, expected_price), respond5)


if __name__ == '__main__':
    unittest.main()
