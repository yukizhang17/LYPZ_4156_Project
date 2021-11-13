from flask import Flask, render_template, request, jsonify
import json
import sqlite3
from uuid import uuid4

app = Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    return 'Hello, World'


# /unsubscribe/xy123token/product/type/platform
@app.route('/unsubscribe', methods=['POST'])
def unsubscribe():
    access_token = request.args.get("access_token", None)
    product = request.args.get("product", None)
    type = request.args.get("type", None)
    platform = request.args.get("platform", None)

    if not access_token or not product or not type: 
        return "access_token, product, type can't be Null, try again"
    if not platform and type == "productID":
        return "unsubscribe with productID, platform can't be Null, try again"
  

#!!!!!!!!!!!change later use userinfo function !!!!!!!!!
    # check user exists in user table 
    sqliteConnection = sqlite3.connect('db/LYPZ.db')
    cursor = sqliteConnection.cursor()
    
    cursor.execute('SELECT COUNT(uid), uid FROM user WHERE access_token = "'+ access_token +'";')
    record = cursor.fetchall()
    print(record)
    if record[0][0] == 1: # user exists
        uid = record[0][1]
    elif record[0][0] == 0:
        return jsonify("Invalid access_token")
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    if type == "keyword":
        # unsubscirbe based on keyword
        respond = delete_by_keyword(uid, product)
        
    elif type == "productID":
        # gengerate corresponding website
        if platform == "Amazon":
            website = "https://www.amazon.com/gp/product/" + product
        elif platform == "BestBuy":
            website = "https://api.bestbuy.com/click/-/"+ product + "/pdp"
        else:
            return "Incurrect platform, Amazon or BestBuy, try again."

        respond = delete_by_productID(uid, product, website)
        
    else:
        return "Incurrect type: keyword or productID, try again."

    return jsonify(respond)

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
        return "No record, check keyword, try again."

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
            return "User never subscribe this keyword!"

        elif sub_record[0][0]: 
            # user sub before, now delete this record from user_subcription_keyword

            sql = """ DELETE FROM user_subcription_keyword where sid = ? and uid = ?; """
            val = (sid, uid)
            cursor.execute(sql, val)
            sqliteConnection.commit()
            
            # check if other user subscribed the same keyword,
            # if not, delete it from subscription_keyword as well 

            sql = """ SELECT uid, expected_price
            FROM user_subcription_keyword
            WHERE sid = ?; """
            val = (sid, )
            cursor.execute(sql, val)
            other_sub_record = cursor.fetchall()
            print("other_sub_record", other_sub_record)
            
            if not other_sub_record: # no other user subscribe, delete
                sql = """ DELETE FROM subscription_keyword where sid = ?; """
                val = (sid, )
                cursor.execute(sql, val)
                sqliteConnection.commit()

            cursor.close()
            return "Unsubscribe successfully!"


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
        return "No record, check product_ID and platform, try again."

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
            return "User never subscribe this product!"

        elif sub_record[0][0]: 
            # user sub before, now delete this record from user_subcription_product_id

            sql = """ DELETE FROM user_subcription_product_id where sid = ? and uid = ?; """
            val = (sid, uid)
            cursor.execute(sql, val)
            sqliteConnection.commit()
            
            # check if other user subscribed the same product,
            # if not, delete it from subscription_product_id as well 


            sql = """ SELECT uid, expected_price
            FROM user_subcription_product_id
            WHERE sid = ?; """
            val = (sid, )
            cursor.execute(sql, val)
            other_sub_record = cursor.fetchall()
            print("other_sub_record", other_sub_record)
            
            if not other_sub_record: # no other user subscribe, delete
                sql = """ DELETE FROM subscription_product_id where sid = ?; """
                val = (sid, )
                cursor.execute(sql, val)
                sqliteConnection.commit()

            cursor.close()
            return "Unsubscribe successfully!"



@app.route('/subscribe', methods=['POST'])
def subscribe():
    access_token = request.args.get("access_token", None)
    product = request.args.get("product", None)
    type = request.args.get("type", None)
    platform = request.args.get("platform", None)
    expected_price = request.args.get("expected_price", None)

    if expected_price:
        expected_price = float(expected_price)

    if not access_token or not product or not type: 
        return "access_token, product, type can't be Null, try again"
    if not platform and type == "productID":
        return "Subscribe with productID, platform can't be Null, try again"
  

    # BBAPI_KEY = "nU3Uo9RMMpqKmrhpm2if81bl"
    # bb_url = "https://api.bestbuy.com/v1/products/"


    
#!!!!!!!!!!!change later use userinfo function !!!!!!!!!
    # check user exists in user table 
    sqliteConnection = sqlite3.connect('db/LYPZ.db')
    cursor = sqliteConnection.cursor()
    
    cursor.execute('SELECT COUNT(uid), uid FROM user WHERE access_token = "'+ access_token +'";')
    record = cursor.fetchall()
    print(record)
    if record[0][0] == 1: # user exists
        uid = record[0][1]
    elif record[0][0] == 0:
        return jsonify("Invalid access_token")
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    if type == "keyword":
        # subscirbe based on keyword
        respond = insert_by_keyword(uid, product, expected_price)
        
    elif type == "productID":
        # gengerate corresponding website
        if platform == "Amazon":
            website = "https://www.amazon.com/gp/product/" + product
        elif platform == "BestBuy":
            website = "https://api.bestbuy.com/click/-/"+ product + "/pdp"
        else:
            return "Incurrect platform, Amazon or BestBuy, try again."

        respond = insert_by_productID(uid, product, website, expected_price)
        
    else:
        return "Incurrect type, keyword or productID, try again."
        

    return jsonify(respond)


def insert_by_keyword(uid, keyword, expected_price):
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
        sid = generate_sid()

        cursor.execute('INSERT INTO subscription_keyword'+ 
        '(sid, keyword)' +
        'VALUES("'+ sid + '","' + keyword + '");')
    
        respond1 = sqliteConnection.commit()   
        if expected_price:
            cursor.execute('INSERT INTO user_subcription_keyword (uid, sid, expected_price)' 
                            'VALUES(?, ?, ?)', (uid, sid, expected_price))
            # print("type", type(expected_price))
        else:
            cursor.execute('INSERT INTO user_subcription_keyword'+ 
            '(uid, sid)' +
            'VALUES("'+ uid + '","' + sid + '");')
        respond2 = sqliteConnection.commit()   
        
        cursor.close()
        if respond1 == None and respond2 == None:
            return "Subscribed successfully!"
        else:
            return "Failed Insert product ID to db!"

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

        if not sub_record: # user never subscribe this keyword before
            if expected_price:
                cursor.execute('INSERT INTO user_subcription_keyword'
                '(uid, sid, expected_price)' 
                'VALUES(?, ?, ?)', 
                (uid, sid, expected_price))
            else:
                cursor.execute('INSERT INTO user_subcription_keyword'
                '(uid, sid)'
                'VALUES(?, ?)', 
                (uid, sid))
            sqliteConnection.commit()   
            cursor.close()
            return "Subscribed successfully!"

        elif sub_record[0][0] and sub_record[0][1] != expected_price: 
            # user sub before, now calling with different expected_price

            # update expected_price 
            sql = """ UPDATE user_subcription_keyword set expected_price = ? where sid = ? and uid = ?; """
            val = (expected_price, sid, uid)
            cursor.execute(sql, val)
            sqliteConnection.commit()
            cursor.close()
            return "Subscripted expected price updated!"

        elif sub_record[0][0] and sub_record[0][1] == expected_price:
            # user subscribed the same product with same expected_price 
            return "User has subscribed the same keyword!"


def insert_by_productID(uid, productID, website, expected_price):
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
        sid = generate_sid()

        cursor.execute('INSERT INTO subscription_product_id'+ 
        '(sid, product_id, website)' +
        'VALUES("'+ sid + '","' + productID + '","' + website + '");')
    
        respond1 = sqliteConnection.commit()   
        if expected_price:
            cursor.execute('INSERT INTO user_subcription_product_id (uid, sid, expected_price)' 
                            'VALUES(?, ?, ?)', (uid, sid, expected_price))
            # print("type", type(expected_price))
        else:
            cursor.execute('INSERT INTO user_subcription_product_id'+ 
            '(uid, sid)' +
            'VALUES("'+ uid + '","' + sid + '");')
        respond2 = sqliteConnection.commit()   
        
        cursor.close()
        if respond1 == None and respond2 == None:
            return "Subscribed successfully!"
        else:
            return "Failed Insert product ID to db!"

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
            if expected_price:
                cursor.execute('INSERT INTO user_subcription_product_id'
                '(uid, sid, expected_price)' 
                'VALUES(?, ?, ?)', 
                (uid, sid, expected_price))
            else:
                cursor.execute('INSERT INTO user_subcription_product_id'
                '(uid, sid)'
                'VALUES(?, ?)', 
                (uid, sid))
            sqliteConnection.commit()   
            cursor.close()
            return "Subscribed successfully!"

        elif sub_record[0][0] and sub_record[0][1] != expected_price: 
            # user sub before, now calling with different expected_price

            # update expected_price 
            sql = """ UPDATE user_subcription_product_id set expected_price = ? where sid = ? and uid = ?; """
            val = (expected_price, sid, uid)
            cursor.execute(sql, val)
            sqliteConnection.commit()
            cursor.close()
            return "Subscripted expected price updated!"

        elif sub_record[0][0] and sub_record[0][1] == expected_price:
            # user subscribed the same product with same expected_price 
            return "User has subscribed the same product!"

       
        
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

# /unsubscribe/access_token/product/type/platform

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1')
