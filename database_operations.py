from bson import ObjectId # For ObjectId to work
from pymongo import MongoClient

username = 'objectDetectionAdmin'
password = 'n8light#549_9012'
client = MongoClient('mongodb://%s:%s@127.0.0.1' % (username, password)) #host uri
db = client.local    #Select the database

model_results = db.model_results #Select the collection name

def add_model_result(json_result):
    try:
        result = model_results.insert_one(json_result)
        op = model_results.find_one({'name': 'dipika'})
        return "Successfully inserted data", 200
    except pymongo.errors.PyMongoError as e:
        return "Insertion operation failed", 400
