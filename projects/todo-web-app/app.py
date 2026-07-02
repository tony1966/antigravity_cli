from flask import Flask, jsonify, request, render_template, abort
from todo.storage import TodoStorage
from todo.manager import TodoManager

app = Flask(__name__)

# Initialise shared storage and manager instances
storage = TodoStorage("todo_data.json")
manager = TodoManager(storage)


# ─────────────────────────────────────────────
# Frontend Route
# ─────────────────────────────────────────────

@app.route("/")
def index():
    """Serve the main SPA page."""
    return render_template("index.html")


# ─────────────────────────────────────────────
# REST API Routes
# ─────────────────────────────────────────────

@app.route("/api/todos", methods=["GET"])
def get_todos():
    """GET /api/todos — Return all todos (optionally filtered by ?status=done|pending|all)."""
    status = request.args.get("status", "all")
    todos = manager.list_todos(status=status)
    return jsonify(todos), 200


@app.route("/api/todos", methods=["POST"])
def create_todo():
    """POST /api/todos — Create a new todo. Body: {"title": "..."}"""
    data = request.get_json(silent=True)
    if not data or not data.get("title", "").strip():
        abort(400, description="Field 'title' is required and cannot be empty.")
    new_todo = manager.add(data["title"])
    return jsonify(new_todo), 201


@app.route("/api/todos/<int:todo_id>/done", methods=["PATCH"])
def mark_done(todo_id: int):
    """PATCH /api/todos/<id>/done — Mark a todo as completed."""
    updated = manager.mark_done(todo_id)
    if updated is None:
        abort(404, description=f"Todo with id={todo_id} not found.")
    return jsonify({"success": True, "todo": updated}), 200


@app.route("/api/todos/<int:todo_id>", methods=["DELETE"])
def delete_todo(todo_id: int):
    """DELETE /api/todos/<id> — Delete a todo."""
    deleted = manager.delete(todo_id)
    if not deleted:
        abort(404, description=f"Todo with id={todo_id} not found.")
    return jsonify({"success": True, "id": todo_id}), 200


# ─────────────────────────────────────────────
# Error Handlers
# ─────────────────────────────────────────────

@app.errorhandler(400)
def bad_request(e):
    return jsonify({"error": str(e.description)}), 400


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": str(e.description)}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error."}), 500


# ─────────────────────────────────────────────
# Entry Point
# ─────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True, port=5000)
