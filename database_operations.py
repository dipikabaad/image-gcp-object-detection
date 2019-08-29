from bson import ObjectId # For ObjectId to work
from pymongo import MongoClient
import json
import glob
import os
import shutil
import ast
from google.cloud import storage
from netlight_utils import constants


username = 'objectDetectionAdmin'
password = 'n8light#549_9012'
client = MongoClient('mongodb://%s:%s@127.0.0.1' % (username, password)) #host uri
db = client.local    #Select the database

model_results = db.model_results_5 #Select the collection name

def add_model_result(json_result):
    try:
        result = model_results.insert_one(json_result)
        op = model_results.find_one({'input_file_path': json_result['input_file_path']})
        return "Successfully inserted data", 200
    except:
        return "Insertion operation failed", 400

def retrieve_model_result():
    results = []
    json_data = {}
    try:
        for post in model_results.find():
            results.append({'input_file_path': post['input_file_path'], 'location': post['location'], 'detected_objects': post['detected_objects'], 'detected_scores': post['detected_scores'], 'output_file_path': post['output_file_path'] })
            # try:
            #     json_data = json.dumps({"data": results})
            # except:
            #     print("Error because of dump")
            #     print(results)
            # break
        # print(json_data)
        return results, 200
    except:
        return "Insertion operation failed", 400

def load_images(json_result):
    # images = ast.literal_eval(json_result['image_paths'])
    images = json_result['image_paths']
    output_path = json_result['output_frontend_folder']
    client = storage.Client(project=constants.cloud_config['PROJECT_ID'])
    bucket = client.bucket(constants.cloud_config['STORAGE_BUCKET'])
    # Clearning the directory
    files = glob.glob(output_path)
    os.chmod(output_path, 0o777)
    shutil.rmtree(output_path, ignore_errors=True)
    os.mkdir(output_path)
    try:
        for image in images:
            blob = bucket.get_blob(image)
            output_file_name = image[image.find('/')+1:]
            download_path = (output_path + '/' + output_file_name).replace('//','/')
            blob.download_to_filename(download_path)
        return "Successfully downloaded files", 200
    except:
        return "Failed to download the file", 400
