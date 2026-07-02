import json
import threading
from pathlib import Path
from typing import List, Dict


class TodoStorage:
    """Handles reading and writing todos to a JSON file.
    Thread-safe with a lock to prevent concurrent write corruption.
    Data schema is fully compatible with the CLI version (id: int, title: str).
    """

    def __init__(self, filepath: str = "todo_data.json"):
        self.filepath = Path(filepath)
        self._lock = threading.Lock()
        self._ensure_file()

    def _ensure_file(self) -> None:
        """Create the JSON file with an empty list if it doesn't exist."""
        if not self.filepath.exists():
            self.filepath.write_text("[]", encoding="utf-8")

    def load(self) -> List[Dict]:
        """Load and return all todos from the JSON file."""
        with self._lock:
            try:
                content = self.filepath.read_text(encoding="utf-8")
                return json.loads(content)
            except (json.JSONDecodeError, FileNotFoundError):
                return []

    def save(self, todos: List[Dict]) -> None:
        """Save the list of todos to the JSON file."""
        with self._lock:
            self.filepath.write_text(
                json.dumps(todos, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
