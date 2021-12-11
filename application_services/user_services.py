from auth0.v3.authentication import GetToken
from auth0.v3.authentication import Users
import requests
import re

# Jona Auth 0
CLIENT_ID = 'EfQZGs8qdAdrof7gkCU7hMN12M5yMi3G'
CLIENT_SECRET = 'z-CiE8aGv75UMqTjZZf_Cmbs3hra' + \
                'HNVhvKn92fMxpMl1FBm6kW5wZMK06Qk5W9Hc'

# Yuqi Auth 0
'''
CLIENT_ID = '4B0wjTqzViFBcMRWBYXIDWBu8xSWJOg7'
CLIENT_SECRET = 'A69T9TJGGzElqcDAFwHfFFSChs0sFq3c' + \
                'Rg9Tibq2jUUwIBRoNIspQHkfO517AJZv'
'''
API = 'https://4156_LYPZ/api'
DB = 'Username-Password-Authentication'


# check if all required fields are included in api form
def validate_all_api_form_fields(fields, form):
    for field in fields:
        if field not in form:
            return False
    return True


# Take username and password to perform login request
def login_request(username, password):
    token = GetToken('dev-ntceedrk.us.auth0.com')

    try:
        c = token.login(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
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


# Take username and password and api key (None is for application)
# to perform login request
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

    callback = requests.post(
        "https://dev-ntceedrk.us.auth0.com/dbconnections/signup",
        json=data)
    return callback


# Validate access token
def validate_token(token):
    try:
        user = Users('dev-ntceedrk.us.auth0.com')
        rst = user.userinfo(token)
        return rst
    except Exception as e:
        error = str(e).split(":")
        return {"code": error[0], "reason": error[1]}


# get user id using access token
def get_user_id(token):
    response = validate_token(token)
    if "sub" in response:
        return response["sub"].split("|")[1]
    return False


# This is copy from website to check if email valid
def valid_email(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    # pass the regular expression
    # and the string into the fullmatch() method
    if(re.fullmatch(regex, email)):
        return True
    return False
