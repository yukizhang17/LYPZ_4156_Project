from flask import Flask, render_template, request, jsonify
import sqlite3
from uuid import uuid4
from database_services.sql_service import SqliteService


def get_subscribe_input(form):
    product = form["product"]
    type = form["type"]

    # expected_price is optinal field
    if "expected_price" in form:
        expected_price = form["expected_price"]
        if expected_price:
            expected_price = float(expected_price)
    else:
        expected_price = None
    
    # subscribe with productID, platform can't be Null,
    if "platform" not in form and type == "productID":
        # print("shouldbe here")
        return (400, "missing required fields")
        # return (400, "Subscribe with productID, platform can't be Null, try again")
    elif "platform" in form:
        platform = form["platform"]
    else:
        platform = None

    return (200, {"product": product, "type": type, "platform": platform, "expected_price": expected_price})


def subscribe_product(uid, product, type, platform, expected_price):
    if type == "keyword":
        # subscirbe based on keyword
        respond = insert_by_keyword(uid, product, expected_price)
        
    elif type == "productID":
        # gengerate corresponding website
        website_message = generate_website(platform, product)
        if website_message[0] == 400:
            return website_message
        else:
            website = website_message[1]

        respond = insert_by_productID(uid, product, website, expected_price)
        
    else:
        return (200, "Incurrect type, keyword or productID.")
        
    return respond

def insert_frist_time(product, uid, expected_price, type, website):
    sid = generate_sid()

    if type == "keyword":
        subscribe_table = "subscription_keyword"
        user_subscribe_table = "user_subcription_keyword"
        respond1 = SqliteService.insert(subscribe_table, {"sid": sid, "keyword": product})
        respond2 = SqliteService.insert(user_subscribe_table, {"uid": uid, "sid": sid, "expected_price": expected_price})
    
    elif type == "productID":
        subscribe_table = "subscription_product_id"
        user_subscribe_table = "user_subcription_product_id"
        respond1 = SqliteService.insert(subscribe_table, {"sid": sid, "product_id": product, "website": website})
        respond2 = SqliteService.insert(user_subscribe_table, {"uid": uid, "sid": sid, "expected_price": expected_price})

    if respond1 == None and respond2 == None:
        return (200, "Subscribed successfully!")
    else:
        return (400, "Failed Insert product ID to db!")


def insert_by_keyword(uid, keyword, expected_price):
    if not keyword:
        return (400, "missing keyword")

    sqliteConnection = sqlite3.connect('db/LYPZ.db')
    cursor = sqliteConnection.cursor()

    sql = """ SELECT sid, keyword
    FROM subscription_keyword
    WHERE keyword = ?; """
    val = (keyword,)
    cursor.execute(sql, val)
    record = cursor.fetchall()
    print("record",record)

    if not record: # never been subscribed before 
        return insert_frist_time(keyword, uid, expected_price, "keyword", None)

    else: # found product in db, keyword been subscribed by someone before
        sid = record[0][0]

        # check if user subscribed same keyword before
        sql = """ SELECT uid, expected_price
        FROM user_subcription_keyword
        WHERE sid = ? and uid = ?; """
        val = (sid, uid)
        cursor.execute(sql, val)

        sub_record = cursor.fetchall()
        print("record", sub_record)

        if not sub_record: # no subscribe this keyword before
            SqliteService.insert("user_subcription_keyword", {"sid": sid, "uid": uid, "expected_price": expected_price})
            return (200, "Subscribed successfully!")

        elif sub_record[0][0] and sub_record[0][1] != expected_price: 
            # user sub before, now calling with different expected_price

            # update expected_price 
            SqliteService.update("user_subcription_keyword", {"expected_price": expected_price}, {"sid": sid, "uid": uid})

            return (200, "Subscripted expected price updated!")

        elif sub_record[0][0] and sub_record[0][1] == expected_price:
            # user subscribed the same product with same expected_price 
            return (400, "User has subscribed the same keyword!")

    cursor.close()
      
def insert_by_productID(uid, productID, website, expected_price):
    sqliteConnection = SqliteService.get_db()
    cursor = sqliteConnection.cursor()

    sql = """ SELECT sid, website
    FROM subscription_product_id 
    WHERE product_id = ? and website = ?; """
    val = (productID, website)
    cursor.execute(sql, val)
    record = cursor.fetchall()

    if not record: # never been subscribed before 
        return insert_frist_time(productID, uid, expected_price, "productID", website)

    else: # found product in db, product been subscribed by someone before
        sid = record[0][0]

        # check if user subscribed same thing before
        sql = """ SELECT uid, expected_price
        FROM user_subcription_product_id
        WHERE sid = ? and uid = ?; """
        val = (sid, uid)
        cursor.execute(sql, val)
        sub_record = cursor.fetchall()
        print("record", sub_record)

        if not sub_record: # user never subscribe this product before
            SqliteService.insert("user_subcription_product_id", {"uid": uid, "sid": sid, "expected_price":expected_price})
            
            return (200, "Subscribed successfully!")

        elif sub_record[0][0] and sub_record[0][1] != expected_price: # user sub before, now calling with different expected_price
            # update expected_price 
            SqliteService.update("user_subcription_product_id", {"expected_price": expected_price}, {"sid": sid, "uid": uid})

            return (200, "Subscripted expected price updated!")

        elif sub_record[0][0] and sub_record[0][1] == expected_price:
            # user subscribed the same product with same expected_price 
            return (400, "User has subscribed the same product!")

    cursor.close()

def get_unsubscribe_input(form):
    product = form["product"]
    type = form["type"]
    if "platform" in form:
        platform = form["platform"]
    else:
        platform= None
        
    if type == "productID" and not "platform" in form:
        return (400, "unsubscribe with productID, platform can't be Null")

    return (200, {"product": product, "type": type, "platform": platform})

def unsubscribe_product(uid, product, type, platform):
    if type == "keyword":
        # unsubscirbe based on keyword
        respond = delete_by_keyword(uid, product)
        
    elif type == "productID":
        # gengerate corresponding website
        website_message = generate_website(platform, product)
        if website_message[0] == 400:
            return website_message
        else:
            website = website_message[1]

        respond = delete_by_productID(uid, product, website)
        
    else:
        return (400, "Incurrect type: keyword or productID, try again.")

    return respond

def delete_by_keyword(uid, keyword):
    sqliteConnection = sqlite3.connect('db/LYPZ.db')
    cursor = sqliteConnection.cursor()

    sql = """ SELECT sid, keyword
    FROM subscription_keyword 
    WHERE keyword = ?; """
    val = (keyword,)
    cursor.execute(sql, val)
    record = cursor.fetchall()

    print("record",record)

    if not record: # never been subscribed before 
        return (200, "No record, check keyword, try again.")

    else: # found keyword in db, keyword been subscribed by someone before
        sid = record[0][0]

        # check if user subscribed this keyword before
        sql = """ SELECT uid, expected_price
        FROM user_subcription_keyword
        WHERE sid = ? and uid = ?; """
        val = (sid, uid)
        cursor.execute(sql, val)

        sub_record = cursor.fetchall()
        print("sub_record", sub_record)

        if not sub_record: # user never subscribe this keyword before
            return (400, "User never subscribe this keyword!")

        elif sub_record[0][0]: 
            return delete_record(sid, uid, "keyword")

def delete_record(sid, uid, type):
    sqliteConnection = sqlite3.connect('db/LYPZ.db')
    cursor = sqliteConnection.cursor()

    if type == "keyword":
        user_sub_table = "user_subcription_keyword"
        sub_table = "subscription_keyword"

    elif type == "productID":
        user_sub_table = "user_subcription_product_id"
        sub_table = "subscription_product_id"

    SqliteService.delete(user_sub_table, {"sid": sid, "uid":uid})

    other_sub_record =  SqliteService.select(user_sub_table, {"sid": sid})
    print("other_sub_record", other_sub_record)
    
    if not other_sub_record: # no other user subscribe, delete
        SqliteService.delete(sub_table, {"sid": sid})
    
    cursor.close()
    return (200, "Unsubscribe successfully!")

def delete_by_productID(uid, productID, website):
    sqliteConnection = sqlite3.connect('db/LYPZ.db')
    cursor = sqliteConnection.cursor()

    sql = """ SELECT sid, website
    FROM subscription_product_id 
    WHERE product_id = ? and website = ?; """
    val = (productID, website)
    cursor.execute(sql, val)
    record = cursor.fetchall()

    print("record",record)

    if not record: # never been subscribed before 
        return (400, "No record, check product_ID and platform, try again.")

    else: # found product in db, product been subscribed by someone before
        sid = record[0][0]

        # check if user subscribed same thing before
        sql = """ SELECT uid, expected_price
        FROM user_subcription_product_id
        WHERE sid = ? and uid = ?; """
        val = (sid, uid)
        cursor.execute(sql, val)

        sub_record = cursor.fetchall()
        print("record", sub_record)

        if not sub_record: # user never subscribe this product before
            return (400, "User never subscribe this product!")

        elif sub_record[0][0]: 
            # user sub before, now delete this record from user_subcription_product_id
            return delete_record(sid, uid, "productID")


def generate_website(platform, product):
    if platform == "Amazon":
        website = "https://www.amazon.com/gp/product/" + product
    elif platform == "BestBuy":
        website = "https://api.bestbuy.com/click/-/"+ product + "/pdp"
    else:
        return (400, "Incurrect platform, Amazon or BestBuy, try again.")

    return (200, website)

  
def generate_sid():
    sid = str(uuid4())

    sqliteConnection = sqlite3.connect('db/LYPZ.db')
    cursor = sqliteConnection.cursor()

    cursor.execute('SELECT COUNT(sid) FROM subscription_keyword WHERE sid = "'+ sid +'";')
    record1 = cursor.fetchall()
    print("record1",record1)
    cursor.execute('SELECT COUNT(sid) FROM subscription_product_id WHERE sid = "'+ sid +'";')
    record2 = cursor.fetchall()
    print("record2",record2)
    if record1[0][0] != 0 or record2[0][0] != 0: 
        generate_sid()

    cursor.close()
    return sid 
