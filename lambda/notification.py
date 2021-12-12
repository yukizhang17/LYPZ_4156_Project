import json
import requests
import datetime
import calendar

# for unit test test
# web = 'http://127.0.0.1:5000/'
web = 'https://whispering-peak-99211.herokuapp.com/'
access_token = "NizHtF)sqL*{#[Cc#sp30um!Kt6pu!"
LOWEST = " lowest price: "
HIGHEST = ", highest price: "
AVG = ", average price: "
NO_PRICE_LOG = "No price logged"


def get_all_users():
    # get all users in user table
    dic = {
        "access_token": access_token,
        "table": "user"
    }
    url = web + 'query-select'

    response = requests.get(url, data=dic)

    user_info = json.loads(response.content)

    return user_info


# create mailing lists
def get_notification_interval(user_info):

    monthly_list = {}
    daily_list = {}
    weekly_list = {}

    for i in user_info:
        if i[3] == "daily":
            daily_list[i[0]] = {"email": i[1], "api_key": i[2]}
        elif i[3] == "weekly":
            weekly_list[i[0]] = {"email": i[1], "api_key": i[2]}
        elif i[3] == "monthly":
            monthly_list[i[0]] = {"email": i[1], "api_key": i[2]}
    return monthly_list, daily_list, weekly_list


# get product or keyword price history
def get_price_history(sid_list, table, sub_info):

    for sid_record in sid_list:
        dic_pid = {
            "access_token": access_token,
            "table": table,
            "sid": sid_record[1]
        }
        url = web + 'query-select'
        response = requests.get(url, data=dic_pid)
        subscription_record = json.loads(response.content)

        sub_info.append(subscription_record)
    return sub_info


# get user's subscription list
def get_user_subscription(uid):
    # get product id subscription list
    dic_pid = {
        "access_token": access_token,
        "table": "user_subcription_product_id",
        "uid": uid
    }
    url = web + 'query-select'

    response_pid = requests.get(url, data=dic_pid)
    # get keyword subscription list
    dic_keyword = {
        "access_token": access_token,
        "table": "user_subcription_keyword",
        "uid": uid
    }
    url = web + 'query-select'

    response_keyword = requests.get(url, data=dic_keyword)

    user_pid_list = json.loads(response_pid.content)
    user_keyword_list = json.loads(response_keyword.content)

    return user_pid_list, user_keyword_list


# generate email content
def generate_email(user_pid_list, user_keyword_list, notification):
    email = user_pid_list[0][2]
    product_num = 0
    keyword_num = 0

    product_detail = ""
    keyword_detail = ""

    length_product = len(user_pid_list)
    length_keyword = len(user_keyword_list)
    # generate user's product subscription detail content
    for i in range(1, length_product):
        product_num += 1
        min_price, max_price, avg_price, interval = \
            find_min_max_avg_price_product(
                user_pid_list[i][0][3], notification)

        product_detail += str(product_num) + ". Product ID: " + \
            user_pid_list[i][0][1] + ", Website: " + \
            user_pid_list[i][0][2] + " \n"
        if notification == "daily":
            product_detail += "Yesterday's price: " + str(min_price) + ". \n"
        elif notification == "weekly":
            product_detail += "Last week's " + interval + \
                LOWEST + str(min_price) + \
                HIGHEST + str(max_price) + \
                AVG + str(avg_price) + ". \n"
        elif notification == "monthly":
            product_detail += "Last month's " + interval + \
                LOWEST + str(min_price) + \
                HIGHEST + str(max_price) + \
                AVG + str(avg_price) + ". \n"

    if product_detail == "":
        product_detail = "No product id subscribed."

    # generate user's keyword subscription detail content
    for i in range(1, length_keyword):
        keyword_num += 1
        price_dic = find_min_max_avg_price_keyword(
            user_keyword_list[i][0][2], notification)
        keyword_detail += str(keyword_num) + ". Keyword: " + \
            user_keyword_list[i][0][1] + ", on Amazon, "

        if notification == "daily":
            keyword_detail += "Yesterday's price: " + \
                str(price_dic["min_price_amazon"]) + "."

            keyword_detail += "on BestBuy, Yesterday's price: " + \
                str(price_dic["min_price_bestbuy"]) + ". "

        elif notification == "weekly":
            keyword_detail += "Last week's" + price_dic["interval"] + \
                LOWEST + str(price_dic["min_price_amazon"]) + \
                HIGHEST + str(price_dic["max_price_amazon"]) + \
                AVG + str(price_dic["avg_price_amazon"]) + "."

            keyword_detail += "on BestBuy, Last week's" + \
                price_dic["interval"] + \
                LOWEST + str(price_dic["min_price_bestbuy"]) + \
                HIGHEST + str(price_dic["max_price_bestbuy"]) + \
                AVG + str(price_dic["avg_price_bestbuy"]) + "."

        elif notification == "monthly":
            keyword_detail += "Last month's" + price_dic["interval"] + \
                LOWEST + \
                str(price_dic["min_price_amazon"]) + \
                HIGHEST + str(price_dic["max_price_amazon"]) + \
                AVG + str(price_dic["avg_price_amazon"]) + "."

            keyword_detail += "on BestBuy, Last month's" + \
                price_dic["interval"] + \
                LOWEST + str(price_dic["min_price_bestbuy"]) + \
                HIGHEST + str(price_dic["max_price_bestbuy"]) + \
                AVG + str(price_dic["avg_price_bestbuy"]) + "."

    if keyword_detail == "":
        keyword_detail = "No keyword subscribed."

    return email, product_detail, keyword_detail


# find min, max, average price from keyword price history
def find_min_max_avg_price_keyword(price_history, notification):
    price_history_list = price_history.split(",")
    price_history_dic = []
    # convert price to list
    for item in price_history_list:
        platform, date, price = item.split("-")
        if price != "None":
            price = float(price)
        else:
            price = NO_PRICE_LOG
        price_history_dic.append([platform, date, price])

    if notification == "daily":
        interval = " (" + price_history_dic[-1][1] + ") "
        return {"min_price_amazon": price_history_dic[-2][2],
                "max_price_amazon": None,
                "avg_price_amazon": None,
                "min_price_bestbuy": price_history_dic[-1][2],
                "max_price_bestbuy": None,
                "avg_price_bestbuy": None, "interval": interval}

    elif notification == "weekly":

        min_price_amazon, max_price_amazon, avg_price_amazon, \
            min_price_bestbuy, max_price_bestbuy, avg_price_bestbuy, \
            interval = track_record_keyword(14, price_history_dic)

    elif notification == "monthly":
        # calculate number of days need to track
        month = datetime.datetime.today().month
        year = datetime.datetime.today().year
        if month == 1:
            year -= 1
            month = 12
        else:
            month -= 1
        number_of_day = calendar.monthrange(year, month)[1]

        num_record = number_of_day * 2

        min_price_amazon, max_price_amazon, avg_price_amazon, \
            min_price_bestbuy, max_price_bestbuy, avg_price_bestbuy, \
            interval = track_record_keyword(num_record, price_history_dic)

    return {"min_price_amazon": min_price_amazon,
            "max_price_amazon": max_price_amazon,
            "avg_price_amazon": avg_price_amazon,
            "min_price_bestbuy": min_price_bestbuy,
            "max_price_bestbuy": max_price_bestbuy,
            "avg_price_bestbuy": avg_price_bestbuy,
            "interval": interval}


# caclulate amazon and bestbuy's min, average, max price
def track_record_keyword(num_record, price_history_dic):
    min_price_amazon, max_price_amazon, avg_price_amazon = None, None, None
    min_price_bestbuy, max_price_bestbuy, avg_price_bestbuy = None, None, None

    sub_list = price_history_dic[-num_record:]
    interval = " (" + sub_list[0][1] + " - " + sub_list[-1][1] + ") "
    # seperate data to two lists
    amazon_list = []
    bestbuy_list = []
    for i in range(num_record):
        if i % 2 == 0:
            amazon_list.append(sub_list[i])
        else:
            bestbuy_list.append(sub_list[i])
    # amazon list
    length_list = len(amazon_list) - 1
    while length_list >= 0:
        if amazon_list[length_list][2] == NO_PRICE_LOG:
            amazon_list.remove(amazon_list[length_list])
        if bestbuy_list[length_list][2] == NO_PRICE_LOG:
            bestbuy_list.remove(bestbuy_list[length_list])
        length_list -= 1
    if len(amazon_list) == 0:
        min_price_amazon = NO_PRICE_LOG
        max_price_amazon = NO_PRICE_LOG
        avg_price_amazon = NO_PRICE_LOG
    else:
        min_price_amazon = min(amazon_list, key=lambda x: x[2])[2]
        max_price_amazon = max(amazon_list, key=lambda x: x[2])[2]

        avg_price_amazon = sum(n for _, _, n in amazon_list)/len(amazon_list)
        avg_price_amazon = round(avg_price_amazon, 2)
    # bestbuy list
    if len(bestbuy_list) == 0:
        min_price_bestbuy = NO_PRICE_LOG
        max_price_bestbuy = NO_PRICE_LOG
        avg_price_bestbuy = NO_PRICE_LOG
    else:
        min_price_bestbuy = min(bestbuy_list, key=lambda x: x[2])[2]
        max_price_bestbuy = max(bestbuy_list, key=lambda x: x[2])[2]

        avg_price_bestbuy = \
            sum(n for _, _, n in bestbuy_list)/len(bestbuy_list)
        avg_price_bestbuy = round(avg_price_bestbuy, 2)

    return min_price_amazon, max_price_amazon, avg_price_amazon, \
        min_price_bestbuy, max_price_bestbuy, avg_price_bestbuy, interval


# find min, max, average price from product price history
def find_min_max_avg_price_product(price_history, notification):
    price_history_list = price_history.split(",")

    price_history_dic = []
    for item in price_history_list:
        key, val = item.split("-", 1)
        if val != "None":
            val = float(val)
        else:
            val = NO_PRICE_LOG
        price_history_dic.append([key, val])

    min_price, max_price, avg_price, interval = None, None, None, ""

    if notification == "daily":
        interval = " (" + price_history_dic[-1][0] + ") "
        return price_history_dic[-1][1], None, None, interval

    elif notification == "weekly":
        week_list = price_history_dic[-7:]
        interval = " (" + week_list[0][0] + " - " + week_list[6][0] + ") "

        length_list = len(week_list) - 1
        while length_list >= 0:
            if week_list[length_list][1] == NO_PRICE_LOG:
                week_list.remove(week_list[length_list])
            length_list -= 1

        if len(week_list) == 0:
            min_price = NO_PRICE_LOG
            max_price = NO_PRICE_LOG
            avg_price = NO_PRICE_LOG
        else:
            min_price = min(week_list, key=lambda x: x[1])[1]
            max_price = max(week_list, key=lambda x: x[1])[1]

            avg_price = sum(n for _, n in week_list)/len(week_list)
            avg_price = round(avg_price, 2)
    elif notification == "monthly":
        # calculate number of date need to count
        month = datetime.datetime.today().month
        year = datetime.datetime.today().year
        if month == 1:
            year -= 1
            month = 12
        else:
            month -= 1
        number_of_day = calendar.monthrange(year, month)[1]
        month_list = price_history_dic[-number_of_day:]
        interval = " (" + month_list[0][0] + " - " + month_list[-1][0] + ") "

        length_list = len(month_list) - 1
        while length_list >= 0:
            if month_list[length_list][1] == NO_PRICE_LOG:
                month_list.remove(month_list[length_list])
            length_list -= 1

        if len(month_list) == 0:
            min_price = NO_PRICE_LOG
            max_price = NO_PRICE_LOG
            avg_price = NO_PRICE_LOG
        else:
            min_price = min(month_list, key=lambda x: x[1])[1]
            max_price = max(month_list, key=lambda x: x[1])[1]

            avg_price = sum(n for _, n in month_list)/len(month_list)
            avg_price = round(avg_price, 2)
    return min_price, max_price, avg_price, interval


# collect user, price data from database
def collect_data(notification_interval, notification_list):

    keyword_sub_info = []
    product_sub_info = []

    for uid in notification_list:
        # for each user, find user's subscribe info
        # generate email, send email
        api_key = notification_list[uid]["api_key"]
        email = notification_list[uid]["email"]
        keyword_sub_info = [[uid, api_key, email]]
        product_sub_info = [[uid, api_key, email]]

        # get uid in user_sub_pid and user_sub_key table
        user_pid_list, user_keyword_list = get_user_subscription(uid)

        # find record
        user_pid_list = get_price_history(
            user_pid_list, "subscription_product_id", product_sub_info)

        user_keyword_list = get_price_history(
            user_keyword_list, "subscription_keyword", keyword_sub_info)

        email, product_detail, keyword_detail = generate_email(
            user_pid_list, user_keyword_list, notification_interval)

    return "success"


# get current date, decide which mailing list to call
def get_date(monthly_list, daily_list, weekly_list):
    # Monday is 0 and Sunday is 6
    week = datetime.datetime.today().weekday()
    day = datetime.datetime.today().day
    if week == 0:
        collect_data("weekly", weekly_list)
    if day == 1:
        collect_data("monthly", monthly_list)

    collect_data("daily", daily_list)
    return "success"


# lambda function
def lambda_handler(event, context):

    user_info = get_all_users()
    monthly_list, daily_list, weekly_list = \
        get_notification_interval(user_info)
    get_date(monthly_list, daily_list, weekly_list)

    return {
        'statusCode': 200,
        'body': json.dumps("hello")
    }
