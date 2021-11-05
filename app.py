from flask import Flask, render_template, request, jsonify
import json

app = Flask(__name__)



@app.route('/', methods=['GET'])
def home():
    pass

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1')
