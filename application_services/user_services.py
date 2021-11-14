from flask import Flask, render_template, request, jsonify, g
from authlib.integrations.flask_client import OAuth
from auth0.v3.authentication import GetToken
from auth0.v3.authentication import Users
from auth0.v3.authentication import Database
from database_services.sql_service import SqliteService

import uuid
import json
import requests
import socket
import sqlite3

CLIENT_ID = 'EfQZGs8qdAdrof7gkCU7hMN12M5yMi3G'
CLIENT_SECRET = 'z-CiE8aGv75UMqTjZZf_Cmbs3hraHNVhvKn92fMxpMl1FBm6kW5wZMK06Qk5W9Hc'
API = 'https://4156_LYPZ/api'
DB = 'Username-Password-Authentication'

#check if all required fields are included in api form
def validate_all_api_form_fields(fields, form):
	for field in fields:
		if field not in form:
			return False
	return True

def login_request(username, password):
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

        return c

    except Exception as e:
        error = str(e).split(":")
        return {"code": error[0], "reason": error[1]}

def signup_request(email, password, api_key=None):
	if api_key:
		username = email + "_apikey_" + api_key
	else:
		username = email + "_APP"

	data = {
	    "client_id": CLIENT_ID,
	    "email": email,
	    "password": password,
	    "connection": DB,
	    "username": username
	}

	callback = requests.post("https://dev-ntceedrk.us.auth0.com/dbconnections/signup", json = data)
	return callback

def validate_token(token):
    try:
        user = Users('dev-ntceedrk.us.auth0.com')
        rst = user.userinfo(token)
        return rst
    except Exception as e:
        error = str(e).split(":")
        return {"code": error[0], "reason": error[1]} 

def get_user_id(token):
	response = validate_token(token)
	if "sub" in response:
		return response["sub"].split("|")[1]
	return False
