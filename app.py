from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

DATA_FILE = "data.json"

# Create empty data file if it doesn't exist
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

    # Multiple tests support
    if isinstance(payload, dict) and "tests" in payload:
        tests_list = payload.get("tests")
        if not isinstance(tests_list, list) or not tests_list:
            return jsonify({"error": "No tests provided"}), 400

        for new_test in tests_list:
            new_test["id"] = max([d["id"] for d in data], default=0) + 1
            data.append(new_test)
            added_tests.append(new_test)
    # Single test object
    elif isinstance(payload, dict):
        new_test = payload
        new_test["id"] = max([d["id"] for d in data], default=0) + 1
        data.append(new_test)
        added_tests.append(new_test)
    else:
        return jsonify({"error": "Invalid data format"}), 400

    write_data(data)
    return jsonify({"message": f"{len(added_tests)} test(s) added successfully", "data": added_tests}), 201

# ------------------ PUT (Update test by ID) ------------------
@app.route("/api/tests/<int:test_id>", methods=["PUT"])
def update_test_by_url(test_id):
    return update_test_common(test_id)

@app.route("/api/tests", methods=["PUT"])
def update_test_by_query():
    test_id = request.args.get("id")
    if not test_id:
        return jsonify({"error": "ID query parameter required"}), 400
    try:
        test_id = int(test_id)
    except ValueError:
        return jsonify({"error": "Invalid ID"}), 400
    return update_test_common(test_id)

def update_test_common(test_id):
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

# ------------------ DELETE (Delete test by ID) ------------------
@app.route("/api/tests/<int:test_id>", methods=["DELETE"])
def delete_test_by_url(test_id):
    return delete_test_common(test_id)

@app.route("/api/tests", methods=["DELETE"])
def delete_test_by_query():
    test_id = request.args.get("id")
    if not test_id:
        return jsonify({"error": "ID query parameter required"}), 400
    try:
        test_id = int(test_id)
    except ValueError:
        return jsonify({"error": "Invalid ID"}), 400
    return delete_test_common(test_id)

def delete_test_common(test_id):
    data = read_data()
    for test in data:
        if test["id"] == test_id:
            data.remove(test)
            write_data(data)
            return jsonify({"message": "Test deleted successfully"})
    return jsonify({"error": "Test not found"}), 404

# ------------------ Run Server ------------------
if __name__ == "__main__":
    app.run(debug=True)
