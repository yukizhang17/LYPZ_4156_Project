from flask import Flask, render_template, request, jsonify
from authlib.integrations.flask_client import OAuth
from auth0.v3.authentication import GetToken
from auth0.v3.authentication import Users
from auth0.v3.authentication import Database

import uuid
import json
import requests
import socket

app = Flask(__name__)

oauth = OAuth(app)

CLIENT_ID = 'EfQZGs8qdAdrof7gkCU7hMN12M5yMi3G'
CLIENT_SECRET='z-CiE8aGv75UMqTjZZf_Cmbs3hraHNVhvKn92fMxpMl1FBm6kW5wZMK06Qk5W9Hc'
API='https://4156_LYPZ/api'
DB='Username-Password-Authentication'

@app.route('/signup', methods=['POST'])
def signup():
    form = request.form
    email = form["email"]
    username = email + "Yuki"
    password = form["password"]

    db = Database('dev-ntceedrk.us.auth0.com')
    db.signup(client_id=CLIENT_ID, username = username, email=email, password=password, connection='Username-Password-Authentication')

    data = {
        "client_id": CLIENT_ID,
        "email": email,
        "password": password,
        "connection": DB,
        "username": username
    }

    callback = requests.post("https://dev-ntceedrk.us.auth0.com/dbconnections/signup", json = data)

    return jsonify(callback.json())


@app.route('/login', methods=['GET'])
def login():
    form = request.form
    email = form["email"]
    username = email + "Yuki"
    password = form["password"]

    token = GetToken('dev-ntceedrk.us.auth0.com')

    try:
        c = token.login(
            client_id=CLIENT_ID,
            client_secret = CLIENT_SECRET,
            audience=API,
            username=username,
            password=password,
            scope="openid",
            realm=DB
            )
        return jsonify(c)
    except Exception as e:
        error = str(e).split(":")
        return {"code": error[0], "reason": error[1]}


@app.route('/userinfo', methods=['GET'])
def userinfo():
    try:
        token = request.form["token"]
        user = Users('dev-ntceedrk.us.auth0.com')
        return jsonify(user.userinfo(token))
    except Exception as e:
        error = str(e).split(":")
        return {"code": error[0], "reason": error[1]} 



'''
    form = request.form
    username = form["username"]
    password = form["password"]

    data = {
        "grant_type": "password-realm",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "audience": "https://4156_LYPZ/api",
        "password": password,
        "username": username,
        "realm": "Username-Password-Authentication"
    }

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    #'auth0-forwarded-for': socket.gethostbyname(socket.gethostname())

    callback = requests.post("https://dev-ntceedrk.us.auth0.com/oauth/token", json=data, headers=headers)

    return jsonify(callback.json())

    data = {
        "client_id": CLIENT_ID,
        "response_type": "json",
        "audience": "https://dev-ntceedrk.us.auth0.com/api/v2/"
    }

    callback = requests.get("https://dev-ntceedrk.us.auth0.com/authorize", params=data)
    print(type(callback))
    return str(callback.text)


'''







if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1')
