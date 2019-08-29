from flask import Flask
from flask import request, jsonify
from database_operations import add_model_result, retrieve_model_result, load_images
from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/')
def test_message():
    return 'Welcome'

@app.route("/insert_data", methods=['GET','POST'])
def insert_data():
    req_data = request.get_json()
    message, status = add_model_result(req_data)
    return jsonify({"message": message, "status": status})

@app.route("/get_data", methods=['GET'])
def get_data():
    results, status = retrieve_model_result()
    return jsonify({"results": results, "status": status})

@app.route("/load_data", methods=['POST'])
@cross_origin()
def load_data():
    req_data = request.get_json()
    message, status = load_images(req_data)
    return jsonify({"message": message, "status": status})

if __name__ == "__main__":
    app.run(debug=True)
