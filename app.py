from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the Todo model
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'completed': self.completed
        }

@app.route('/test', methods=['GET'])
def test():
    return "API is working!"

@app.route('/todos', methods=['POST'])
def add_todo():
    data = request.get_json()

    # Check if 'title' and 'description' are provided and valid
    if not data.get('title') or not isinstance(data['title'], str):
        return jsonify({"error": "Title is required and must be a string"}), 400

    if not data.get('description') or not isinstance(data['description'], str):
        return jsonify({"error": "Description is required and must be a string"}), 400

    # Proceed with adding the task
    new_todo = Todo(
        title=data['title'],
        description=data['description'],
        completed=False
    )
    db.session.add(new_todo)
    db.session.commit()

    return jsonify(new_todo.serialize()), 201

@app.route('/todos', methods=['GET'])
def get_todos():
    todos = Todo.query.all()
    return jsonify([todo.to_dict() for todo in todos]), 200

@app.route('/todos/<int:id>', methods=['PUT'])
def update_todo(id):
    data = request.get_json()

    # Validate that title and description are strings if provided
    if 'title' in data and not isinstance(data['title'], str):
        return jsonify({"error": "Title must be a string"}), 400

    if 'description' in data and not isinstance(data['description'], str):
        return jsonify({"error": "Description must be a string"}), 400

    # Proceed with updating the task if it exists
    todo = Todo.query.get(id)
    if todo is None:
        return jsonify({"error": "Task not found"}), 404

    todo.title = data.get('title', todo.title)
    todo.description = data.get('description', todo.description)
    todo.completed = data.get('completed', todo.completed)

    db.session.commit()

    return jsonify(todo.serialize()), 200

@app.route('/todos/<int:id>', methods=['DELETE'])
def delete_todo(id):
    todo = Todo.query.get(id)

    if todo is None:
        return jsonify({"error": "Task not found"}), 404

    db.session.delete(todo)
    db.session.commit()

    return jsonify({"message": "Task deleted"}), 200

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Resource not found"}), 404


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(debug=True)


