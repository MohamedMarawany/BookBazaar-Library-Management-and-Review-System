from flask import Flask, jsonify, request, abort

# Initialize Flask app
app = Flask(__name__)

# In-memory data store for demonstration
books = [
    {
        "id": 1,
        "title": "The Great Gatsby",
        "author_id": 1,
        "genre": "Fiction",
        "published_year": 1925
    },
    {
        "id": 2,
        "title": "To Kill a Mockingbird",
        "author_id": 3,
        "genre": "Fiction",
        "published_year": 1960
    }
]

# Home route
@app.route('/')
def home():
    return "Welcome to BookBazaar API!"

# GET /books - Retrieve all books
@app.route('/books', methods=['GET'])
def get_books():
    return jsonify(books), 200

# POST /books - Add a new book
@app.route('/books', methods=['POST'])
def add_book():
    data = request.get_json()
    if not data or not all(key in data for key in ['title', 'author_id', 'genre', 'published_year']):
        abort(400, description="Invalid input. Ensure 'title', 'author_id', 'genre', and 'published_year' are provided.")

    new_book = {
        "id": len(books) + 1,
        "title": data['title'],
        "author_id": data['author_id'],
        "genre": data['genre'],
        "published_year": data['published_year']
    }
    books.append(new_book)
    return jsonify({"message": "Book added successfully!", "book": new_book}), 201

# PUT /books/<id> - Update a book
@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    data = request.get_json()
    if not data:
        abort(400, description="Invalid input. Provide at least one field to update.")

    book = next((book for book in books if book['id'] == book_id), None)
    if not book:
        abort(404, description="Book not found.")

    if 'title' in data:
        book['title'] = data['title']
    if 'genre' in data:
        book['genre'] = data['genre']
    if 'published_year' in data:
        book['published_year'] = data['published_year']

    return jsonify({"message": "Book updated successfully!", "book": book}), 200

# DELETE /books/<id> - Delete a book
@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    global books
    book = next((book for book in books if book['id'] == book_id), None)
    if not book:
        abort(404, description="Book not found.")

    books = [book for book in books if book['id'] != book_id]
    return jsonify({"message": "Book deleted successfully!"}), 200

# Error handler for 404
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": str(error)}), 404

# Error handler for 400
@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": str(error)}), 400

# Run the app
if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)


