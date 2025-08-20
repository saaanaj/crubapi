from flask import Flask, request, jsonify
from flask_cors import CORS
import json
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
