from datetime import datetime
from typing import List, Dict, Optional
from todo.storage import Storage

class TodoManager:
    """Manages todo actions: add, list, done, delete, delegating persistence to Storage."""
    
    def __init__(self, storage: Storage):
        self.storage = storage

    def _load_todos(self) -> List[Dict]:
        return self.storage.load()

    def _save_todos(self, todos: List[Dict]) -> None:
        self.storage.save(todos)

    def add(self, title: str) -> Dict:
        """Adds a new todo item and returns it."""
        todos = self._load_todos()
        
        # Auto-increment ID
        new_id = max([todo["id"] for todo in todos], default=0) + 1
        
        new_todo = {
            "id": new_id,
            "title": title.strip(),
            "done": False,
            "created_at": datetime.now().isoformat()
        }
        
        todos.append(new_todo)
        self._save_todos(todos)
        return new_todo

    def list_todos(self, status: str = "all") -> List[Dict]:
        """Lists todos filtered by status: 'all', 'done', or 'pending'."""
        todos = self._load_todos()
        if status == "done":
            return [todo for todo in todos if todo["done"]]
        elif status == "pending":
            return [todo for todo in todos if not todo["done"]]
        return todos

    def mark_done(self, todo_id: int) -> bool:
        """Marks a todo item as completed. Returns True if found and updated, False otherwise."""
        todos = self._load_todos()
        for todo in todos:
            if todo["id"] == todo_id:
                if todo["done"]:
                    return True # Already done
                todo["done"] = True
                self._save_todos(todos)
                return True
        return False

    def delete(self, todo_id: int) -> bool:
        """Deletes a todo item. Returns True if found and deleted, False otherwise."""
        todos = self._load_todos()
        initial_length = len(todos)
        todos = [todo for todo in todos if todo["id"] != todo_id]
        
        if len(todos) < initial_length:
            self._save_todos(todos)
            return True
        return False
