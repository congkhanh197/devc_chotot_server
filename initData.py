import pymongo
from pymongo import MongoClient
import pandas as pd
import json

csvPath = './data/last_hope.csv'

csv = pd.read_csv(csvPath)
data = csv.to_dict('records')
for i in data:
    i.pop("Unnamed: 0")
    i.pop("Unnamed: 0.1")
    i.pop("Unnamed: 0.1.1")


client = pymongo.MongoClient(
    "mongodb+srv://suat:tran1997179@mydb-fkhoo.mongodb.net/test?retryWrites=true&w=majority")
db = client.myDB

ad_data = db["ad_data"]
# ad_data.delete_many({})
# ad_data.insert_many(data)