import unittest
import os
import sys


currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

try:
    from application_services.notification import get_notification_interval, \
        get_all_users, get_user_subscription, get_price_history, \
        find_min_max_avg_price_product, find_min_max_avg_price_keyword, \
        send_simple_message2, collect_data, get_date
    from database_services.sql_service import SqliteService
    #   subscribe_product, generate_website, unsubscribe_product,\
    #   get_unsubscribe_input
except Exception:
    raise


class Test_Testnotification(unittest.TestCase):

    # Testcase 1: Test get all users
    def test_get_all_users(self):
        # Test input with no platform
        user_data = SqliteService.select("user", {})
        new_user_data = [list(i) for i in user_data]

        self.assertEqual(get_all_users(), new_user_data)

    # Testcase 2: Test if users are placed in corresponding mailing list
    def test_get_notification_interval(self):
        user_info = []
        user1 = [
            'uid1', 'xyan830@gmail.com',
            'f1aaa7cbc07a46b6a1edb033e2252532', 'monthly']
        user2 = [
            'uid2', 'jonathan.jsliu@gmail.com',
            'f1aaa7cbc07a46b6a1edb033e2252532', 'weekly']
        user3 = [
            'uid3', 'yz3983@columbia.edu',
            '6f074b5f90a147e78988ca4ee373191f', 'daily']
        user4 = [
            'uid4', 'zp2188@columbia.edu',
            '713349d273b54cdaaa40188038b33c3b', 'off']
        user_info = [user1, user2, user3, user4]

        monthly_list = {
                'uid1': {
                    "email": 'xyan830@gmail.com',
                    "api_key": 'f1aaa7cbc07a46b6a1edb033e2252532'}}
        daily_list = {
            'uid3': {
                "email": 'yz3983@columbia.edu',
                "api_key": '6f074b5f90a147e78988ca4ee373191f'}}
        weekly_list = {
            'uid2': {
                "email": 'jonathan.jsliu@gmail.com',
                "api_key": 'f1aaa7cbc07a46b6a1edb033e2252532'}}

        m_list, d_list, w_list = get_notification_interval(user_info)
        self.assertEqual(m_list, monthly_list)
        self.assertEqual(d_list, daily_list)
        self.assertEqual(w_list, weekly_list)

    # Testcase 3: Test get user subscription correctly
    def test_get_user_subscription(self):
        user_data = SqliteService.select("user", {})
        if user_data != []:
            uid = user_data[0][0]

            user_data_product = SqliteService.select(
                "user_subcription_product_id", {"uid": uid})
            user_data_keyword = SqliteService.select(
                "user_subcription_keyword", {"uid": uid})

            new_user_data_product = [list(i) for i in user_data_product]
            new_data_keyword = [list(i) for i in user_data_keyword]

            user_pid_list, user_keyword_list = get_user_subscription(uid)

            self.assertEqual(user_pid_list, new_user_data_product)
            self.assertEqual(user_keyword_list, new_data_keyword)

    # Test case : test get product's price history
    def test_get_price_history(self):
        user_data_product = SqliteService.select(
            "user_subcription_product_id", {})
        sub_info = []
        if user_data_product != []:
            new_user_data_product = [list(i) for i in user_data_product]

            sid_list = new_user_data_product[0][1]
            print(sid_list)
            sub_info_fetch = SqliteService.select(
                "subscription_product_id", {"sid": sid_list})
            new_sub_info_fetch = [list(i) for i in sub_info_fetch]
        result = get_price_history(
            [["test", sid_list]], "subscription_product_id", sub_info)
        self.assertEqual([new_sub_info_fetch], result)

    # Test case : find min, max, avg price from a list of price
    def test_min_max_avg_price_product(self):
        price_history = '2021/11/01-100.00,2021/11/02-100.00,' + \
            '2021/11/03-100.00,2021/11/04-100.00,2021/11/05-100.00,' + \
            '2021/11/06-100.00,2021/11/07-100.00,2021/11/08-100.00,' + \
            '2021/11/09-100.00,2021/11/10-100.00,2021/11/11-100.00,' + \
            '2021/11/12-None,2021/11/13-100.00,2021/11/14-100.00,' + \
            '2021/11/15-100.00,2021/11/16-100.00,2021/11/17-100.00,' + \
            '2021/11/18-100.00,2021/11/19-100.00,2021/11/20-100.00,' + \
            '2021/11/21-100.00,2021/11/22-100.00,2021/11/23-100.00,' + \
            '2021/11/24-99.00,2021/11/25-101.00,2021/11/26-99.00,' + \
            '2021/11/27-102.00,2021/11/28-99.00,2021/11/29-100.00,' + \
            '2021/11/30-100.00'

        notification = "daily"
        interval = " (2021/11/30) "
        min_price = 100.00

        min_price_get, max_price_get, avg_price_get, interval_get = \
            find_min_max_avg_price_product(price_history, notification)

        self.assertEqual(min_price, min_price_get)
        self.assertEqual(max_price_get, None)
        self.assertEqual(avg_price_get, None)
        self.assertEqual(interval_get, interval)

        notification = "weekly"
        interval = " (2021/11/24 - 2021/11/30) "
        max_price = 102.00
        min_price = 99
        avg_price = 100.00
        min_price_get, max_price_get, avg_price_get, interval_get = \
            find_min_max_avg_price_product(price_history, notification)

        self.assertEqual(min_price, min_price_get)
        self.assertEqual(max_price_get, max_price)
        self.assertEqual(avg_price_get, avg_price)
        self.assertEqual(interval_get, interval)

        notification = "monthly"
        interval = " (2021/11/01 - 2021/11/30) "
        max_price = 102.00
        min_price = 99
        avg_price = 100.00
        min_price_get, max_price_get, avg_price_get, interval_get = \
            find_min_max_avg_price_product(price_history, notification)

        self.assertEqual(min_price, min_price_get)
        self.assertEqual(max_price_get, max_price)
        self.assertEqual(avg_price_get, avg_price)
        self.assertEqual(interval_get, interval)

        # test no price logged
        price_history = '2021/11/01-None,2021/11/02-None,' + \
            '2021/11/03-None,2021/11/04-None,2021/11/05-None,' + \
            '2021/11/06-None,2021/11/07-None,2021/11/08-None,' + \
            '2021/11/09-None,2021/11/10-None,2021/11/11-None,' + \
            '2021/11/12-None,2021/11/13-None,2021/11/14-None,' + \
            '2021/11/15-None,2021/11/16-None,2021/11/17-None,' + \
            '2021/11/18-None,2021/11/19-None,2021/11/20-None,' + \
            '2021/11/21-None,2021/11/22-None,2021/11/23-None,' + \
            '2021/11/24-None,2021/11/25-None,2021/11/26-None,' + \
            '2021/11/27-None,2021/11/28-None,2021/11/29-None,' + \
            '2021/11/30-None'

        notification = "weekly"
        interval = " (2021/11/24 - 2021/11/30) "
        max_price = "No price logged"
        min_price = "No price logged"
        avg_price = "No price logged"
        min_price_get, max_price_get, avg_price_get, interval_get = \
            find_min_max_avg_price_product(price_history, notification)

        self.assertEqual(min_price, min_price_get)
        self.assertEqual(max_price_get, max_price)
        self.assertEqual(avg_price_get, avg_price)
        self.assertEqual(interval_get, interval)

        notification = "monthly"
        interval = " (2021/11/01 - 2021/11/30) "
        max_price = "No price logged"
        min_price = "No price logged"
        avg_price = "No price logged"
        min_price_get, max_price_get, avg_price_get, interval_get = \
            find_min_max_avg_price_product(price_history, notification)

        self.assertEqual(min_price, min_price_get)
        self.assertEqual(max_price_get, max_price)
        self.assertEqual(avg_price_get, avg_price)
        self.assertEqual(interval_get, interval)

# Test case : find min, max, avg price from a list of price for keyword
    def test_min_max_avg_price_keyword(self):
        price_list = 'amazon-2021/11/01-110.00,bestbuy-2021/11/01-102.00,' + \
            'amazon-2021/11/02-110.00,bestbuy-2021/11/02-102.00,' + \
            'amazon-2021/11/03-110.00,bestbuy-2021/11/03-102.00,' + \
            'amazon-2021/11/04-110.00,bestbuy-2021/11/04-102.00,' + \
            'amazon-2021/11/05-110.00,bestbuy-2021/11/05-102.00,' + \
            'amazon-2021/11/06-110.00,bestbuy-2021/11/06-102.00,' + \
            'amazon-2021/11/07-110.00,bestbuy-2021/11/07-102.00,' + \
            'amazon-2021/11/08-110.00,bestbuy-2021/11/08-102.00,' + \
            'amazon-2021/11/09-110.00,bestbuy-2021/11/09-102.00,' + \
            'amazon-2021/11/10-100.00,bestbuy-2021/11/10-102.00,' + \
            'amazon-2021/11/11-100.00,bestbuy-2021/11/11-102.00,' + \
            'amazon-2021/11/12-120.00,bestbuy-2021/11/12-102.00,' + \
            'amazon-2021/11/13-110.00,bestbuy-2021/11/13-102.00,' + \
            'amazon-2021/11/14-120.00,bestbuy-2021/11/14-102.00,' + \
            'amazon-2021/11/15-110.00,bestbuy-2021/11/15-102.00,' + \
            'amazon-2021/11/16-120.00,bestbuy-2021/11/16-102.00,' + \
            'amazon-2021/11/17-100.00,bestbuy-2021/11/17-102.00,' + \
            'amazon-2021/11/18-110.00,bestbuy-2021/11/18-102.00,' + \
            'amazon-2021/11/19-110.00,bestbuy-2021/11/19-102.00,' + \
            'amazon-2021/11/20-110.00,bestbuy-2021/11/20-102.00,' + \
            'amazon-2021/11/21-110.00,bestbuy-2021/11/21-102.00,' + \
            'amazon-2021/11/22-110.00,bestbuy-2021/11/22-102.00,' + \
            'amazon-2021/11/23-110.00,bestbuy-2021/11/23-102.00,' + \
            'amazon-2021/11/24-110.00,bestbuy-2021/11/24-104.00,' + \
            'amazon-2021/11/25-110.00,bestbuy-2021/11/25-102.00,' + \
            'amazon-2021/11/26-120.00,bestbuy-2021/11/26-102.00,' + \
            'amazon-2021/11/27-110.00,bestbuy-2021/11/27-102.00,' + \
            'amazon-2021/11/28-110.00,bestbuy-2021/11/28-102.00,' + \
            'amazon-2021/11/29-110.00,bestbuy-2021/11/29-102.00,' + \
            'amazon-2021/11/30-100.00,bestbuy-2021/11/30-100.00'
        notification = "daily"
        interval = " (2021/11/30) "
        min_price_amazon = 100.00
        max_price_amazon = None
        avg_price_amazon = None
        min_price_bestbuy = 100.00
        max_price_bestbuy = None
        avg_price_bestbuy = None

        return_dic = \
            find_min_max_avg_price_keyword(price_list, notification)
        return_dic["min_price_amazon"]
        return_dic["max_price_amazon"]
        return_dic["avg_price_amazon"]
        return_dic["min_price_bestbuy"]
        return_dic["max_price_bestbuy"]
        return_dic["avg_price_bestbuy"]
        return_dic["interval"]

        self.assertEqual(return_dic["min_price_amazon"], min_price_amazon)
        self.assertEqual(return_dic["max_price_amazon"], max_price_amazon)
        self.assertEqual(return_dic["avg_price_amazon"], avg_price_amazon)
        self.assertEqual(return_dic["min_price_bestbuy"], min_price_bestbuy)
        self.assertEqual(return_dic["max_price_bestbuy"], max_price_bestbuy)
        self.assertEqual(return_dic["avg_price_bestbuy"], avg_price_bestbuy)
        self.assertEqual(return_dic["interval"], interval)

        notification = "weekly"
        interval = " (2021/11/24 - 2021/11/30) "
        min_price_amazon = 100.00
        max_price_amazon = 120.00
        avg_price_amazon = 110.00
        min_price_bestbuy = 100.00
        max_price_bestbuy = 104.00
        avg_price_bestbuy = 102.00

        return_dic = \
            find_min_max_avg_price_keyword(price_list, notification)

        self.assertEqual(return_dic["min_price_amazon"], min_price_amazon)
        self.assertEqual(return_dic["max_price_amazon"], max_price_amazon)
        self.assertEqual(return_dic["avg_price_amazon"], avg_price_amazon)
        self.assertEqual(return_dic["min_price_bestbuy"], min_price_bestbuy)
        self.assertEqual(return_dic["max_price_bestbuy"], max_price_bestbuy)
        self.assertEqual(return_dic["avg_price_bestbuy"], avg_price_bestbuy)
        self.assertEqual(return_dic["interval"], interval)

        notification = "monthly"
        interval = " (2021/11/01 - 2021/11/30) "
        min_price_amazon = 100.00
        max_price_amazon = 120.00
        avg_price_amazon = 110.00
        min_price_bestbuy = 100.00
        max_price_bestbuy = 104.00
        avg_price_bestbuy = 102.00

        return_dic = \
            find_min_max_avg_price_keyword(price_list, notification)

        self.assertEqual(return_dic["min_price_amazon"], min_price_amazon)
        self.assertEqual(return_dic["max_price_amazon"], max_price_amazon)
        self.assertEqual(return_dic["avg_price_amazon"], avg_price_amazon)
        self.assertEqual(return_dic["min_price_bestbuy"], min_price_bestbuy)
        self.assertEqual(return_dic["max_price_bestbuy"], max_price_bestbuy)
        self.assertEqual(return_dic["avg_price_bestbuy"], avg_price_bestbuy)
        self.assertEqual(return_dic["interval"], interval)

        # test no price logged
        price_list = 'amazon-2021/11/01-None,bestbuy-2021/11/01-None,' + \
            'amazon-2021/11/02-None,bestbuy-2021/11/02-None,' + \
            'amazon-2021/11/03-None,bestbuy-2021/11/03-None,' + \
            'amazon-2021/11/04-None,bestbuy-2021/11/04-None,' + \
            'amazon-2021/11/05-None,bestbuy-2021/11/05-None,' + \
            'amazon-2021/11/06-None,bestbuy-2021/11/06-None,' + \
            'amazon-2021/11/07-None,bestbuy-2021/11/07-None,' + \
            'amazon-2021/11/08-None,bestbuy-2021/11/08-None,' + \
            'amazon-2021/11/09-None,bestbuy-2021/11/09-None,' + \
            'amazon-2021/11/10-None,bestbuy-2021/11/10-None,' + \
            'amazon-2021/11/11-None,bestbuy-2021/11/11-None,' + \
            'amazon-2021/11/12-None,bestbuy-2021/11/12-None,' + \
            'amazon-2021/11/13-None,bestbuy-2021/11/13-None,' + \
            'amazon-2021/11/14-None,bestbuy-2021/11/14-None,' + \
            'amazon-2021/11/15-None,bestbuy-2021/11/15-None,' + \
            'amazon-2021/11/16-None,bestbuy-2021/11/16-None,' + \
            'amazon-2021/11/17-None,bestbuy-2021/11/17-None,' + \
            'amazon-2021/11/18-None,bestbuy-2021/11/18-None,' + \
            'amazon-2021/11/19-None,bestbuy-2021/11/19-None,' + \
            'amazon-2021/11/20-None,bestbuy-2021/11/20-None,' + \
            'amazon-2021/11/21-None,bestbuy-2021/11/21-None,' + \
            'amazon-2021/11/22-None,bestbuy-2021/11/22-None,' + \
            'amazon-2021/11/23-None,bestbuy-2021/11/23-None,' + \
            'amazon-2021/11/24-None,bestbuy-2021/11/24-None,' + \
            'amazon-2021/11/25-None,bestbuy-2021/11/25-None,' + \
            'amazon-2021/11/26-None,bestbuy-2021/11/26-None,' + \
            'amazon-2021/11/27-None,bestbuy-2021/11/27-None,' + \
            'amazon-2021/11/28-None,bestbuy-2021/11/28-None,' + \
            'amazon-2021/11/29-None,bestbuy-2021/11/29-None,' + \
            'amazon-2021/11/30-None,bestbuy-2021/11/30-None'

        notification = "weekly"
        interval = " (2021/11/24 - 2021/11/30) "
        min_price_amazon = "No price logged"
        max_price_amazon = "No price logged"
        avg_price_amazon = "No price logged"
        min_price_bestbuy = "No price logged"
        max_price_bestbuy = "No price logged"
        avg_price_bestbuy = "No price logged"

        return_dic = \
            find_min_max_avg_price_keyword(price_list, notification)
        return_dic["min_price_amazon"]
        return_dic["max_price_amazon"]
        return_dic["avg_price_amazon"]
        return_dic["min_price_bestbuy"]
        return_dic["max_price_bestbuy"]
        return_dic["avg_price_bestbuy"]
        return_dic["interval"]

        self.assertEqual(return_dic["min_price_amazon"], min_price_amazon)
        self.assertEqual(return_dic["max_price_amazon"], max_price_amazon)
        self.assertEqual(return_dic["avg_price_amazon"], avg_price_amazon)
        self.assertEqual(return_dic["min_price_bestbuy"], min_price_bestbuy)
        self.assertEqual(return_dic["max_price_bestbuy"], max_price_bestbuy)
        self.assertEqual(return_dic["avg_price_bestbuy"], avg_price_bestbuy)
        self.assertEqual(return_dic["interval"], interval)

        notification = "monthly"
        interval = " (2021/11/01 - 2021/11/30) "

        return_dic = \
            find_min_max_avg_price_keyword(price_list, notification)
        return_dic["min_price_amazon"]
        return_dic["max_price_amazon"]
        return_dic["avg_price_amazon"]
        return_dic["min_price_bestbuy"]
        return_dic["max_price_bestbuy"]
        return_dic["avg_price_bestbuy"]
        return_dic["interval"]

        self.assertEqual(return_dic["min_price_amazon"], min_price_amazon)
        self.assertEqual(return_dic["max_price_amazon"], max_price_amazon)
        self.assertEqual(return_dic["avg_price_amazon"], avg_price_amazon)
        self.assertEqual(return_dic["min_price_bestbuy"], min_price_bestbuy)
        self.assertEqual(return_dic["max_price_bestbuy"], max_price_bestbuy)
        self.assertEqual(return_dic["avg_price_bestbuy"], avg_price_bestbuy)
        self.assertEqual(return_dic["interval"], interval)

# Test case : send email
    def test_send_simple_message(self):
        response = send_simple_message2(
            "xyan830@gmail.com",
            "daily", "product_detail", "keyword_detail")

        self.assertEqual(response.status_code, 200)

# Testcase : collect user's subscribed item's price status
    def test_collect_data(self):
        user_data = SqliteService.select("user", {})
        if user_data != []:
            if user_data[0][3] != "off":

                notification_list = {
                    user_data[0][0]: {
                        "email": user_data[0][1], "api_key": user_data[0][2]}}
                print(notification_list)
                notification_interval = user_data[0][3]

            result = collect_data(notification_interval, notification_list)
            print(result)
            self.assertEqual(result.status_code, 200)

# Testcase 4: get current date and trigger corresponding mailing list
    def test_get_date(self):
        user_info = get_all_users()
        monthly_list, daily_list, weekly_list = \
            get_notification_interval(user_info)
        result = get_date(monthly_list, daily_list, weekly_list)
        self.assertEqual(result.status_code, 200)
