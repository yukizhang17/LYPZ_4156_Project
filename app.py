from flask import Flask, request, jsonify
from database_services.sql_service import SqliteService
from application_services.user_services import CLIENT_ID, \
    CLIENT_SECRET, validate_token, login_request, signup_request, \
    validate_all_api_form_fields, get_user_id, valid_email
# from application_services.price_fetching_services import compare_prices, \
#     validate_optional_api_form_fields
from application_services.subscribe import get_subscribe_input, \
    subscribe_product, get_unsubscribe_input, unsubscribe_product
import uuid
import os

file_path = os.path.realpath(__file__)
print(file_path)

app = Flask(__name__)


API = 'https://4156_LYPZ/api'
DB = 'Username-Password-Authentication'


@app.route('/', methods=["GET"])
def home():
    return "Hello World"


# Generate 32 digit of unique token for each dev
@app.route('/generate-apikey', methods=['GET', 'POST'])
def generate_apikey():
    # check if all require information are presented
    form = request.form
    if not validate_all_api_form_fields(["email", "password"], form):
        return jsonify({
            "reason": "missing required fields", "status_code": 400})

    email = form['email']
    password = form['password']

    if request.method == "GET":
        # Login with Auth0 to see if application exist
        rst = SqliteService.select("application", {"email": email})
        if len(rst) == 0:
            return jsonify({"error": "user not found", "status_code": 404})

        response = login_request(email + "_APP", password)

        if "access_token" not in response:
            return jsonify(response)
        # If email already verified, return api key
        if rst[0][2] == 1:
            return jsonify({"api_key": rst[0][1], "status_code": 200})

        # If email verified, update db and return api_key
        response = validate_token(response["access_token"])

        if not response["email_verified"]:
            return jsonify({
                "error": "Please verify your email", "status_code": 401})

        SqliteService.update("application", {"verified": 1}, {"email": email})
        return jsonify({"api_key": rst[0][1], "status_code": 200})

    if request.method == "POST":
        # If already signup, return error
        response = signup_request(email, password).json()
        if "statusCode" in response and response["statusCode"] == 400:
            return jsonify(response)

        # generate api_key
        token = uuid.uuid4().hex
        SqliteService.insert("application", {
            "email": email, "api_key": token, "verified": 0})

        return jsonify({
            "message": "token created, please verified your email ",
            "status_code": 200})
        # return jsonify({"api_key": token, "status_code": 201})


# user signup end point
@app.route('/signup', methods=['POST'])
def signup():
    # check if all require information are presented
    form = request.form
    if not validate_all_api_form_fields(
            ["email", "password", "api_key"], form):
        return jsonify({
            "reason": "missing required fields", "status_code": 400})

    email = form["email"]
    password = form["password"]
    api_key = form["api_key"]
    if not valid_email(email):
        return jsonify({
            "reason": "email not valid format", "status_code": 400})

    callback = signup_request(email, password, api_key)

    if callback.status_code == 200:
        data = callback.json()
        uid = data['_id']
        SqliteService.insert("user", {
            "uid": uid, "email": email,
            "api_key": api_key, "notification_interval": "monthly"})

    return jsonify(callback.json())


@app.route('/login', methods=['GET'])
def login():
    # check if all require information are presented
    form = request.form
    if not validate_all_api_form_fields(
            ["email", "password", "api_key"], form):
        return jsonify({
            "reason": "missing required fields", "status_code": 400})

    username = form["email"] + "_apikey_" + form["api_key"]
    password = form["password"]

    return jsonify(login_request(username, password))


@app.route('/userinfo', methods=['GET'])
def userinfo():
    # check if all require information are presented
    form = request.form
    if not validate_all_api_form_fields(["token"], form):
        return jsonify({
            "reason": "missing required fields", "status_code": 400})

    return jsonify(validate_token(form["token"]))


# @app.route('/compare', methods=['GET'])
# def compare():
#     # compare realtime amazon and bestbuy prices for keyword or item id
#     form = request.form
#     if not validate_all_api_form_fields(["token"], form):
#         return jsonify(
#             {
#                 "reason": "missing required fields",
#                 "status_code": 400
#             }
#         )
#     validation_res = validate_token(form["token"])
#     if 'email' not in validation_res:
#         return jsonify(validation_res)

#     if not validate_optional_api_form_fields(
#         [["keyword"], ["item_id", "platform"]], form
#     ):
#         return jsonify(
#             {
#                 "reason": "missing required fields",
#                 "status_code": 400
#             }
#         )

#     keyword = None
#     if "keyword" in form:
#         keyword = form["keyword"]

#     item_id = None
#     if "item_id" in form:
#         item_id = form["item_id"]

#     platform = None
#     if "platform" in form:
#         platform = form["platform"]

#     res = compare_prices(keyword, item_id, platform)

#     if res is None:
#         return jsonify(
#             {
#                 "reason": "unable to fetch prices, please try again",
#                 "status_code": 400
#             }
#         )

#     return jsonify(res)


@app.route('/subscribe', methods=['POST'])
def subscribe():
    form = request.form
    if not validate_all_api_form_fields(
            ["access_token", "product", "type"], form):
        return jsonify({
            "reason": "missing required fields",
            "status_code": 400})

    validation_res = validate_token(form["access_token"])
    if 'email' not in validation_res:
        return jsonify(validation_res)
    else:
        uid = get_user_id(form["access_token"])

    valid_message = get_subscribe_input(form)
    #  print(valid_message)
    if valid_message[0] == 400:
        return jsonify({"reason": valid_message[1], "status_code": 400})

    respond = subscribe_product(
        uid, valid_message[1]["product"],
        valid_message[1]["type"],
        valid_message[1]["platform"],
        valid_message[1]["expected_price"])
    #  print("respond", respond)
    return jsonify({"reason": respond[1], "status_code": respond[0]})


#  User Unsubscribe ENDPOINT
@app.route('/unsubscribe', methods=['POST'])
def unsubscribe():
    form = request.form
    #  print("form", form)
    if not validate_all_api_form_fields(
            ["access_token", "product", "type"], form):
        return jsonify({
            "reason": "missing required fields",
            "status_code": 400})

    validation_res = validate_token(form["access_token"])
    if 'email' not in validation_res:
        return jsonify(validation_res)
    else:
        uid = get_user_id(form["access_token"])

    valid_message = get_unsubscribe_input(form)
    if valid_message[0] == 400:
        return jsonify({"reason": valid_message[1], "status_code": 400})

    respond = unsubscribe_product(
        uid,
        valid_message[1]["product"],
        valid_message[1]["type"],
        valid_message[1]["platform"])
    #  print("respond", respond)
    return jsonify({"reason": respond[1], "status_code": respond[0]})


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1')
