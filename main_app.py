from flask import Flask
from flask import request, jsonify
from database_operations import add_model_result

app = Flask(__name__)

@app.route("/", methods=['POST'])
def home():
    req_data = request.get_json()
    print(req_data)
    message, status = add_model_result({'name': 'dipika', 'val': 'new'})
    return jsonify({"message": message, "status": str(status) })
    # return "Hello, World!"

if __name__ == "__main__":
    app.run(debug=True)
