from flask import Flask
from flask import request, jsonify
from database_operations import add_model_result

app = Flask(__name__)

@app.route('/')
def test_message():
    return 'Welcome'

@app.route("/insert_data", methods=['GET','POST'])
def insert_data():
    req_data = request.get_json()
    message, status = add_model_result(req_data)
    return jsonify({"message": message}), status

if __name__ == "__main__":
    app.run(debug=True)
