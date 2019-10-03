import csv
import json
import requests
from flask import Flask, redirect, url_for, request
from flask_cors import CORS
from pymongo import MongoClient

import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import Normalizer
normalizer = Normalizer()

properties_ads = pd.read_csv('./data/last_hope.csv')
loaded_model = joblib.load('./data/recommendation.pkl')
filter_adstats = pd.read_csv('./data/filter_adstats.csv')
count_list_id = dict(filter_adstats['adlist_id'].value_counts())
median = int(np.median(np.array(list(count_list_id.values()))))


def counter(x):
    return count_list_id.get(x, median)


def convert_vector(temp_matrix):
    # First preprocessing data
    temp_matrix['price'] = temp_matrix['price'] / \
        10000000  # Divided 10.000.000
    temp_matrix['area'] = temp_matrix['area']*1000
    temp_matrix['count'] = temp_matrix['list_id'].apply(counter)
    temp_matrix = temp_matrix.drop(columns=['list_id'])
    processing_data = normalizer.fit_transform(temp_matrix)
    return processing_data


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
        response=json.dumps(data, ensure_ascii=False).replace(
            "NaN", "\"null\""),
        status=200,
        mimetype='application/json'
    )
    return response


@app.route('/recommend/<string:list_id>')
def ad_recommend(list_id):
    int_list_id = int(list_id)
    temp_matrix = properties_ads[['price', 'area', 'ward', 'rooms',
                                  'list_id']][properties_ads["list_id"] == int(list_id)]
    processing_data = convert_vector(temp_matrix)
    distance, [indices] = loaded_model.kneighbors(processing_data)
    return_data = properties_ads.loc(i for i in indices[1:6])
    print(return_data)

    # response = app.response_class(
    #     response=json.dumps(
    #         {"total": ad_data.estimated_document_count(),
    #          "data": list(ad_data.find(projection={"_id": 0}).sort(
    #              "list_time", -1).skip(10).limit(5))}, ensure_ascii=False).replace("NaN", "\"null\""),
    #     status=200,
    #     mimetype='application/json'
    # )
    # return response
    return "hello"


if __name__ == '__main__':
    app.run(debug=True)
