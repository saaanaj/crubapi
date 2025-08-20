from flask import Flask, request, jsonify
from flask_cors import CORS
import jsonfrom flask import Flask, request, jsonify
from flask_cors import CORS   # 👈 import flask-cors
import json
import os

app = Flask(__name__)
CORS(app)  # 👈 enable CORS for all routes

DATA_FILE = "data.json"

# Agar file exist nahi karti to ek empty array bana do
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump([], f, indent=4)

# ------------------ Read/Write helpers ------------------
def read_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def write_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ------------------ Home ------------------
@app.route("/", methods=["GET"])
def index():
    return "✅ API is running fine."

# ------------------ GET ------------------
@app.route("/api/tests", methods=["GET"])
def get_all_tests():
    data = read_data()
    name = request.args.get("name")
    test_type = request.args.get("type")
    
    if name:
        data = [d for d in data if name.lower() in d.get("name","").lower()]
    if test_type:
        data = [d for d in data if test_type.lower() in d.get("type","").lower()]

    return jsonify(data)

@app.route("/api/tests/<int:test_id>", methods=["GET"])
def get_test(test_id):
    data = read_data()
    for test in data:
        if test["id"] == test_id:
            return jsonify(test)
    return jsonify({"error": "Test not found"}), 404

# ------------------ POST ------------------
@app.route("/api/tests", methods=["POST"])
def add_tests():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 415
    payload = request.get_json()

    data = read_data()
    added_tests = []

    # Support multiple tests with "tests": [ {...}, {...} ]
    if isinstance(payload, dict) and "tests" in payload:
        tests_list = payload.get("tests")
        if not isinstance(tests_list, list) or not tests_list:
            return jsonify({"error": "No tests provided"}), 400

        for new_test in tests_list:
            new_test["id"] = max([d["id"] for d in data], default=0) + 1
            data.append(new_test)
            added_tests.append(new_test)
    # Support single test object
    elif isinstance(payload, dict):
        new_test = payload
        new_test["id"] = max([d["id"] for d in data], default=0) + 1
        data.append(new_test)
        added_tests.append(new_test)
    else:
        return jsonify({"error": "Invalid data format"}), 400

    write_data(data)
    return jsonify({"message": f"{len(added_tests)} test(s) added successfully", "data": added_tests}), 201

# ------------------ PUT (Update specific test by ID) ------------------
@app.route("/api/tests/<int:test_id>", methods=["PUT"])
def update_test(test_id):
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 415
    updated_fields = request.get_json()
    if not updated_fields:
        return jsonify({"error": "No data provided"}), 400

    data = read_data()
    for test in data:
        if test["id"] == test_id:
            test.update(updated_fields)
            write_data(data)
            return jsonify({"message": "Test updated successfully", "data": test})
    return jsonify({"error": "Test not found"}), 404

# ------------------ DELETE ------------------
@app.route("/api/tests/<int:test_id>", methods=["DELETE"])
def delete_test(test_id):
    data = read_data()
    for test in data:
        if test["id"] == test_id:
            data.remove(test)
            write_data(data)
            return jsonify({"message": "Test deleted successfully"})
    return jsonify({"error": "Test not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)

import os

app = Flask(__name__)
CORS(app)  # Allow all origins for frontend requests

DATA_FILE = "data.json"

# Agar file exist nahi karti to create karo
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump([], f, indent=4)

def read_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def write_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

@app.route("/", methods=["GET"])
def index():
    return "Lab Tests API is working!"

@app.route("/api/tests", methods=["GET"])
def get_all_tests():
    data = read_data()
    return jsonify(data)

@app.route("/api/tests", methods=["POST"])
def add_test():
    data = read_data()
    new_test = request.json
    # Generate ID based on max existing id
    new_test["id"] = max([d["id"] for d in data], default=0) + 1
    data.append(new_test)
    write_data(data)
    return jsonify({"message": "Test added successfully", "data": new_test})

@app.route("/api/tests/<int:test_id>", methods=["PUT"])
def update_test(test_id):
    data = read_data()
    for test in data:
        if test["id"] == test_id:
            test.update(request.json)  # Update only the fields provided
            write_data(data)
            return jsonify({"message": "Test updated successfully", "data": test})
    return jsonify({"error": "Test not found"}), 404

@app.route("/api/tests/<int:test_id>", methods=["DELETE"])
def delete_test(test_id):
    data = read_data()
    for test in data:
        if test["id"] == test_id:
            data.remove(test)
            write_data(data)
            return jsonify({"message": "Test deleted successfully"})
    return jsonify({"error": "Test not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)
