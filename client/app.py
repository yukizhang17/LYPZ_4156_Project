from os import access
from flask import Flask, render_template, request, jsonify, redirect, session
from flask_cors import CORS
import requests


web = 'http://127.0.0.1:5000'
# web = 'https://whispering-peak-99211.herokuapp.com'

app = Flask(__name__)


CORS(app)


@app.route('/', methods=["GET"])
def home():
    return render_template("index.html", signup_status="Sign up here", login_status="If you already had an account, log in here")


@app.route('/signup', methods=['POST'])
def signup():
    email = request.form['email']
    password = request.form['password']
    data = {}
    data["email"] = email
    data["password"] = password
    data["api_key"] = "6f074b5f90a147e78988ca4ee373191f"
    # response = requests.post("signup", data=data)
    response = requests.post(web + "/signup", data=data)
    # print(response.json())
    if "_id" in response.json():
        return render_template("index.html", signup_status="You have successfully signed up")
    return render_template("index.html", signup_status="Unsuccessfully signed up")


@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    data = {}
    data["email"] = email
    data["password"] = password
    data["api_key"] = "6f074b5f90a147e78988ca4ee373191f"
    response = requests.get(web + "/login", data=data)
    # print(response.json())
    if "access_token" in response.json():
        access_token = response.json()["access_token"]
        response = requests.get(web + "/userinfo", data={"token":access_token})
        # print(response.json())
        uid = response.json()["sub"].split("|")[1]
        # response = requests.get(web + "/query-select", data=data)
        session["access_token"] = access_token
        session["email"] = email
        session["uid"] = uid
        return redirect("subscription")
    return render_template("index.html", login_status="Bad email or password")
    

@app.route('/subscription', methods=['GET', 'POST'])
def subscribe():
    user = {}
    if request.method == 'POST':
        data = {}
        for key, value in request.form.items():
            data[key] = value
        data["access_token"] = "NizHtF)sqL*{#[Cc#sp30um!Kt6pu!"
        data["table"] = "user_subcription_keyword"
        response = requests.get(web + "/query-select", data=data)
        user["keyword"] = []
        if len(response.json()) == 0:
            user["keyword"].append("This user does not subscribe any keyword")
        for item in response.json():
            sid = item[1]
            form = {}
            form["access_token"] = "NizHtF)sqL*{#[Cc#sp30um!Kt6pu!"
            form["table"] = "subscription_keyword"
            form["sid"] = sid
            response = requests.get(web + "/query-select", data=form)
            # print(response.json())
            user["keyword"].append(response.json()[0][1])
        data["table"] = "user_subcription_product_id"
        response = requests.get(web + "/query-select", data=data)
        user["product_id"] = []
        if len(response.json()) == 0:
            user["product_id"].append("This user does not subscribe any product")
        for item in response.json():
            sid = item[1]
            form = {}
            form["access_token"] = "NizHtF)sqL*{#[Cc#sp30um!Kt6pu!"
            form["table"] = "subscription_product_id"
            form["sid"] = sid
            response = requests.get(web + "/query-select", data=form)
            print(response.json())
            user["product_id"].append(response.json()[0][2])

    
    email = session.get("email")
    user["accesstoken"] = session.get("access_token")
    user["email"] = session.get("email")
    user["login_status"] = "Welcome, " + str(email)
    user["uid"] = session.get("uid")
    #print(access_token)
    if user["accesstoken"] is not None:
        return render_template("front_subscribe.html", user=user)
    return redirect("/")

@app.route('/show-all-subscription')
def all_subscription():
    pass


@app.route('/price-compare', methods=['GET', 'POST'])
def price_compare():
    user = {}
    user["accesstoken"] = session.get("access_token")
    if user["accesstoken"] is None:
        return redirect("/")
    if request.method == 'POST':
        form = request.form
        keyword = None
        item_id = None
        platform = None
        response_json = None
        if 'keyword' in form and form['keyword'] != '':
            keyword = form['keyword']
        if 'item_id' in form and form['item_id'] != '':
            item_id = form['item_id']
        if 'platform' in form and form['platform'] != '':
            platform = form['platform']
        form = {}
        form["access_token"] = user["accesstoken"]
        form["keyword"] = keyword
        form["item_id"] = item_id
        form["platform"] = platform
        response_json = requests.get(web + "/compare", data=form).json()          
        return render_template("compare_prices.html", user=user, response_json=response_json)
    
    return render_template("compare_prices.html", user=user, response=None)
    


if __name__ == '__main__':
    app.secret_key = "yuki is sooooooooooooooooooooooo stupid"
    app.run(debug=True, host='127.0.0.1', port='50000')
