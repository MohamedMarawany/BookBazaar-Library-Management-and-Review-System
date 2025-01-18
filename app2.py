from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
from pymongo.errors import ConnectionFailure, OperationFailure
import sqlite3

app = Flask(__name__)

# MongoDB connection details
MONGO_URI = "mongodb://localhost:27017/bookbazaar_reviews"

# Connect to MongoDB
def connect_to_mongodb():
    try:
        client = MongoClient(MONGO_URI)
        client.admin.command('ping')
        print("Successfully connected to MongoDB!")
        return client
    except ConnectionFailure as e:
        print(f"Failed to connect to MongoDB: {e}")
        return None

client = connect_to_mongodb()
db = client.bookbazaar_reviews if client is not None else None
reviews_collection = db.reviews if db is not None else None

# SQLite database connection (for verifying book existence)
def get_book_from_sqlite(book_id):
    try:
        conn = sqlite3.connect('bookbazaar.db')
        cursor = conn.cursor()
        print(f"Fetching book with ID: {book_id}")  # Debug statement
        cursor.execute("SELECT * FROM Books WHERE id = ?", (book_id,))
        book = cursor.fetchone()
        print(f"Book found: {book}")  # Debug statement
        conn.close()
        return book
    except sqlite3.OperationalError as e:
        print(f"SQLite error: {e}")
        return None

# GET /books/<id>/reviews
@app.route('/books/<int:book_id>/reviews', methods=['GET'])
def get_reviews_for_book(book_id):
    if reviews_collection is None:
        return jsonify({"error": "Database connection failed"}), 500

    reviews = list(reviews_collection.find({"book_id": book_id}, {"_id": 0}))
    return jsonify(reviews), 200

# POST /books/<id>/reviews
@app.route('/books/<int:book_id>/reviews', methods=['POST'])
def add_review(book_id):
    if reviews_collection is None:
        return jsonify({"error": "Database connection failed"}), 500

    # Verify book exists in SQLite database
    book = get_book_from_sqlite(book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404

    # Get review data from request
    data = request.get_json()
    user_id = data.get("user_id")
    rating = data.get("rating")
    comment = data.get("comment")

    if not all([user_id, rating, comment]):
        return jsonify({"error": "Missing required fields"}), 400

    # Add review to MongoDB
    review = {
        "book_id": book_id,
        "user_id": user_id,
        "rating": rating,
        "comment": comment
    }
    result = reviews_collection.insert_one(review)
    return jsonify({"message": "Review added", "review_id": str(result.inserted_id)}), 201

# PUT /reviews/<review_id>
@app.route('/reviews/<review_id>', methods=['PUT'])
def update_review(review_id):
    if reviews_collection is None:
        return jsonify({"error": "Database connection failed"}), 500

    # Get updated data from request
    data = request.get_json()
    new_rating = data.get("rating")
    new_comment = data.get("comment")

    if not all([new_rating, new_comment]):
        return jsonify({"error": "Missing required fields"}), 400

    # Update review in MongoDB
    result = reviews_collection.update_one(
        {"_id": ObjectId(review_id)},
        {"$set": {"rating": new_rating, "comment": new_comment}}
    )

    if result.modified_count > 0:
        return jsonify({"message": "Review updated successfully"}), 200
    else:
        return jsonify({"error": "Review not found"}), 404

# DELETE /reviews/<review_id>
@app.route('/reviews/<review_id>', methods=['DELETE'])
def delete_review(review_id):
    if reviews_collection is None:
        return jsonify({"error": "Database connection failed"}), 500

    # Delete review from MongoDB
    result = reviews_collection.delete_one({"_id": ObjectId(review_id)})

    if result.deleted_count > 0:
        return jsonify({"message": "Review deleted successfully"}), 200
    else:
        return jsonify({"error": "Review not found"}), 404

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)