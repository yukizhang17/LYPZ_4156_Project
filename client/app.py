from flask import Flask, render_template, request, redirect, session
from flask_cors import CORS
import requests


app = Flask(__name__)


CORS(app)


# This is our client's homepage
@app.route('/', methods=["GET"])
def home():
    return render_template(
        "index.html",
        signup_status="Sign up here",
        login_status="If you already had an account, log in here"
        )


# This is the signup route, users can signup here.
@app.route('/signup', methods=['POST'])
def signup():
    email = request.form['email']
    password = request.form['password']
    data = {}
    data["email"] = email
    data["password"] = password
    data["api_key"] = "6f074b5f90a147e78988ca4ee373191f"
    response = requests.post(
        "https://whispering-peak-99211.herokuapp.com/signup",
        data=data)
    if "_id" in response.json():
        return render_template(
            "index.html",
            signup_status="You have successfully signed up"
            )
    return render_template(
        "index.html",
        signup_status="Unsuccessfully signed up")


# This is the login page,
# users could see their profile only after they logged in
@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    data = {}
    data["email"] = email
    data["password"] = password
    data["api_key"] = "6f074b5f90a147e78988ca4ee373191f"
    response = requests.get(
        "https://whispering-peak-99211.herokuapp.com/login",
        data=data)
    if "access_token" in response.json():
        access_token = response.json()["access_token"]
        response = requests.get(
            "https://whispering-peak-99211.herokuapp.com/userinfo",
            data={"token": access_token})
        uid = response.json()["sub"].split("|")[1]
        session["access_token"] = access_token
        session["email"] = email
        session["uid"] = uid
        return redirect("subscription")
    return render_template("index.html", login_status="Bad email or password")


# Users could subscribe/unsubscribe products,
# and also show all the products they subscribed
@app.route('/subscription', methods=['GET', 'POST'])
def subscribe():
    user = {}
    if request.method == 'POST':
        data = {}
        for key, value in request.form.items():
            data[key] = value
        data["access_token"] = "NizHtF)sqL*{#[Cc#sp30um!Kt6pu!"
        data["table"] = "user_subcription_keyword"
        response = requests.get(
            "https://whispering-peak-99211.herokuapp.com/query-select",
            data=data)
        user["keyword"] = []
        if len(response.json()) == 0:
            user["keyword"].append("This user does not subscribe any keyword")
        for item in response.json():
            sid = item[1]
            form = {}
            form["access_token"] = "NizHtF)sqL*{#[Cc#sp30um!Kt6pu!"
            form["table"] = "subscription_keyword"
            form["sid"] = sid
            response = requests.get(
                "https://whispering-peak-99211.herokuapp.com/query-select",
                data=form)
            user["keyword"].append(response.json()[0][1])
        data["table"] = "user_subcription_product_id"
        response = requests.get(
            "https://whispering-peak-99211.herokuapp.com/query-select",
            data=data)
        user["product_id"] = []
        if len(response.json()) == 0:
            user["product_id"].append(
                "This user does not subscribe any product"
                )
        for item in response.json():
            sid = item[1]
            form = {}
            form["access_token"] = "NizHtF)sqL*{#[Cc#sp30um!Kt6pu!"
            form["table"] = "subscription_product_id"
            form["sid"] = sid
            response = requests.get(
                "https://whispering-peak-99211.herokuapp.com/query-select",
                data=form)
            print(response.json())
            user["product_id"].append(response.json()[0][2])

    email = session.get("email")
    user["accesstoken"] = session.get("access_token")
    user["email"] = session.get("email")
    user["login_status"] = "Welcome, " + str(email)
    user["uid"] = session.get("uid")
    if user["accesstoken"] is not None:
        return render_template("front_subscribe.html", user=user)
    return redirect("/")


# Users could change the notification interval
@app.route('/update-interval', methods=['POST'])
def interval_update():
    interval = request.form['interval']
    access_token = request.form['access_token']
    form = {}
    form['notification_interval'] = interval
    form['access_token'] = access_token
    requests.post(
        "https://whispering-peak-99211.herokuapp.com/update-email-preference",
        data=form)
    return "successfully updated notification interval."


if __name__ == '__main__':
    app.secret_key = "4156_LYPZ"
    app.run(debug=True, host='127.0.0.1', port=3000)
