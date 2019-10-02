import csv
import json
import requests
from flask import Flask, redirect, url_for, request
from flask_cors import CORS
from pymongo import MongoClient


csvSchedulePath = './data/schedule.csv'
csvStaffPath = './data/staff.csv'
arr = []


client = MongoClient(
    "mongodb+srv://suat:tran1997179@mydb-fkhoo.mongodb.net/test?retryWrites=true&w=majority")
db = client.myDB
ad_data = db["ad_data"]

app = Flask(__name__)
CORS(app)


@app.route('/')
def index():
    return 'Hello, World!'


@app.route('/ad-listing', methods=['GET', 'POST', 'DELETE'])
def ad_listing():
    # if request.method == 'POST':
    #     # user = request.form['nm']
    #     # return redirect(url_for('success', name=user))
    #     print(request.json)
    #     return "test"

    if request.method == 'GET':
        offset = request.args.get("o")
        limit = request.args.get("limit")
        if not offset:
            offset = 0
        if not limit or int(limit) > 24:
            limit = 24
        response = app.response_class(
            response=json.dumps(
                {"total": ad_data.estimated_document_count(),
                 "offset": int(offset),
                 "limit": int(limit),
                 "data": list(ad_data.find(projection={"_id": 0}).sort(
                     "list_time", -1).skip(int(offset)).limit(int(limit)))}, ensure_ascii=False).replace("NaN", "\"null\""),
            status=200,
            mimetype='application/json'
        )
        return response


@app.route('/ad-listing/<string:list_id>')
def ad_detail(list_id):
    data = requests.get(
        "https://gateway.chotot.com/v1/public/ad-listing/"+list_id).json()
    response = app.response_class(
        response=json.dumps(data, ensure_ascii=False).replace("NaN", "\"null\""),
        status=200,
        mimetype='application/json'
    )
    return response

@app.route('/recommend/<string:list_id>')
def ad_recommend(list_id):
    response = app.response_class(
            response=json.dumps(
                {"total": ad_data.estimated_document_count(),
                 "data": list(ad_data.find(projection={"_id": 0}).sort(
                     "list_time", -1).skip(10).limit(5))}, ensure_ascii=False).replace("NaN", "\"null\""),
            status=200,
            mimetype='application/json'
        )
    return response


if __name__ == '__main__':
    app.run(debug=True)
