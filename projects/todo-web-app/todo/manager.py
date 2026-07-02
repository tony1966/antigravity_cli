from datetime import datetime
from typing import List, Dict, Optional
from todo.storage import TodoStorage


class TodoManager:
    """Business logic layer for todo operations: add, list, mark_done, delete.
    Mirrors the CLI version's manager.py logic for consistency.
    """

    def __init__(self, storage: TodoStorage):
        self.storage = storage

    def _load(self) -> List[Dict]:
        return self.storage.load()

    def _save(self, todos: List[Dict]) -> None:
        self.storage.save(todos)

    def add(self, title: str) -> Dict:
        """Add a new todo item and return it."""
        todos = self._load()
        new_id = max((todo["id"] for todo in todos), default=0) + 1
        new_todo = {
            "id": new_id,
            "title": title.strip(),
            "done": False,
            "created_at": datetime.now().isoformat()
        }
        todos.append(new_todo)
        self._save(todos)
        return new_todo

    def list_todos(self, status: str = "all") -> List[Dict]:
        """Return todos filtered by status: 'all', 'done', or 'pending'."""
        todos = self._load()
        if status == "done":
            return [t for t in todos if t["done"]]
        elif status == "pending":
            return [t for t in todos if not t["done"]]
        return todos

    def mark_done(self, todo_id: int) -> Optional[Dict]:
        """Mark a todo as completed. Returns the updated item or None if not found."""
        todos = self._load()
        for todo in todos:
            if todo["id"] == todo_id:
                todo["done"] = True
                self._save(todos)
                return todo
        return None

    def delete(self, todo_id: int) -> bool:
        """Delete a todo by ID. Returns True if deleted, False if not found."""
        todos = self._load()
        filtered = [t for t in todos if t["id"] != todo_id]
        if len(filtered) < len(todos):
            self._save(filtered)
            return True
        return False
