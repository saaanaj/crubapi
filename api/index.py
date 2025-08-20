from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)
CORS(app)  # Enable CORS

# ------------------ MongoDB Connection ------------------
MONGO_URI = "mongodb+srv://savan:Kumar123@datasav.n8wcv70.mongodb.net/?retryWrites=true&w=majority&appName=datasav"
client = MongoClient(MONGO_URI)
db = client["datasav"]          # Database name
collection = db["tests"]        # Collection name

# ------------------ Home ------------------
@app.route("/", methods=["GET"])
def index():
    return "✅ API is running with MongoDB Atlas."

# ------------------ GET ------------------
@app.route("/api/tests", methods=["GET"])
def get_all_tests():
    query = {}
    name = request.args.get("name")
    test_type = request.args.get("type")

    if name:
        query["name"] = {"$regex": name, "$options": "i"}
    if test_type:
        query["type"] = {"$regex": test_type, "$options": "i"}

    tests = list(collection.find(query))
    for t in tests:
        t["_id"] = str(t["_id"])
    return jsonify(tests)

@app.route("/api/tests/<string:test_id>", methods=["GET"])
def get_test(test_id):
    try:
        test = collection.find_one({"_id": ObjectId(test_id)})
        if test:
            test["_id"] = str(test["_id"])
            return jsonify(test)
        return jsonify({"error": "Test not found"}), 404
    except:
        return jsonify({"error": "Invalid ID"}), 400

# ------------------ POST ------------------
@app.route("/api/tests", methods=["POST"])
def add_tests():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 415
    payload = request.get_json()

    inserted_ids = []

    if isinstance(payload, dict) and "tests" in payload:
        result = collection.insert_many(payload["tests"])
        inserted_ids = [str(i) for i in result.inserted_ids]
    elif isinstance(payload, dict):
        result = collection.insert_one(payload)
        inserted_ids = [str(result.inserted_id)]
    else:
        return jsonify({"error": "Invalid data format"}), 400

    return jsonify({"message": f"{len(inserted_ids)} test(s) added successfully", "ids": inserted_ids}), 201

# ------------------ PUT ------------------
@app.route("/api/tests/<string:test_id>", methods=["PUT"])
def update_test(test_id):
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 415
    updated_fields = request.get_json()
    if not updated_fields:
        return jsonify({"error": "No data provided"}), 400

    try:
        result = collection.update_one({"_id": ObjectId(test_id)}, {"$set": updated_fields})
        if result.matched_count:
            return jsonify({"message": "Test updated successfully"})
        return jsonify({"error": "Test not found"}), 404
    except:
        return jsonify({"error": "Invalid ID"}), 400

# ------------------ DELETE ------------------
@app.route("/api/tests/<string:test_id>", methods=["DELETE"])
def delete_test(test_id):
    try:
        result = collection.delete_one({"_id": ObjectId(test_id)})
        if result.deleted_count:
            return jsonify({"message": "Test deleted successfully"})
        return jsonify({"error": "Test not found"}), 404
    except:
        return jsonify({"error": "Invalid ID"}), 400

# ------------------ Export for Vercel ------------------
if __name__ == "__main__":
    app.run(debug=True)
