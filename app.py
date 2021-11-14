from flask import Flask, render_template, request, jsonify, g
from authlib.integrations.flask_client import OAuth
from auth0.v3.authentication import GetToken
from auth0.v3.authentication import Users
from auth0.v3.authentication import Database
from database_services.sql_service import SqliteService
from application_services.user_services import *

import uuid
import json
import requests
import socket
import sqlite3


app = Flask(__name__)


CLIENT_ID = 'EfQZGs8qdAdrof7gkCU7hMN12M5yMi3G'
CLIENT_SECRET = 'z-CiE8aGv75UMqTjZZf_Cmbs3hraHNVhvKn92fMxpMl1FBm6kW5wZMK06Qk5W9Hc'
API = 'https://4156_LYPZ/api'
DB = 'Username-Password-Authentication'


#Generate 32 digit of unique token for each dev
@app.route('/generate-apikey', methods=['GET', 'POST'])
def generate_apikey():
    #check if all require information are presented
    form = request.form
    if not validate_all_api_form_fields(["email", "password"], form):
        return jsonify({"reason": "missing required fields", "status_code": 400})

    email = form['email']
    password = form['password']

    if request.method == "GET":
        #Login with Auth0 to see if application exsit
        rst = SqliteService.select("application", {"email": email})
        if len(rst) == 0:
            return jsonify({"error": "user not found", "status_code": 404})

        response = login_request(email + "_APP", password)

        if "access_token" not in response:
            return jsonify(response)
        #If email already verified, return api key
        if rst[0][2] == 1:
            return jsonify({"api_key": rst[0][1], "status_code": 200})

        #If email verified, update db and return api_key
        response = validate_token(response["access_token"])

        if not response["email_verified"]:
            return jsonify({"error": "Please verify your email", "status_code": 401})

        SqliteService.update("application", {"verified": 1}, {"email": email})
        return jsonify({"api_key": rst[0][1], "status_code": 200})


    if request.method == "POST":
        #If already signup, return error
        response = signup_request(email, password)
        if "statusCode" in response and response["statusCode"] == 400:
            return jsonify(response)

        #generate api_key
        token = uuid.uuid4().hex
        SqliteService.insert("application", {"email": email, "api_key": token, "verified": 0})

        return jsonify({"message": "token created, please verified your email before receiving the token", "status_code": 200})
        #return jsonify({"api_key": token, "status_code": 201})
    
#user signup end point
@app.route('/signup', methods=['POST'])
def signup():
    #check if all require information are presented
    form = request.form
    if not validate_all_api_form_fields(["email", "password", "api_key"], form):
        return jsonify({"reason": "missing required fields", "status_code": 400})

    email = form["email"]
    password = form["password"]
    api_key = form["api_key"]

    callback = signup_request(email, password, api_key)

    if callback.status_code == 200:
        data = callback.json()
        uid = data['_id']
        SqliteService.insert("user", {"uid": uid, "email": email, "api_key":api_key, "notification_interval":"monthly"})

    return jsonify(callback.json())

@app.route('/login', methods=['GET'])
def login():
    #check if all require information are presented
    form = request.form
    if not validate_all_api_form_fields(["email", "password", "api_key"], form):
        return jsonify({"reason": "missing required fields", "status_code": 400})

    username = form["email"] + "_apikey_" + form["api_key"]
    password = form["password"]

    return jsonify(login_request(username, password))

@app.route('/userinfo', methods=['GET'])
def userinfo():
    #check if all require information are presented
    form = request.form
    if not validate_all_api_form_fields(["token"], form):
        return jsonify({"reason": "missing required fields", "status_code": 400})

    return jsonify(validate_token(form["token"]))


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1')
