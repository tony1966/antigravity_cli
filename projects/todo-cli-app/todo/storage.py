import json
import os

class Storage:
    """Handles loading and saving todo data from/to a JSON file."""
    
    def __init__(self, filepath: str = "todo_data.json"):
        self.filepath = filepath

    def load(self) -> list:
        """Loads todo list from JSON file. Returns empty list if file doesn't exist or is invalid."""
        if not os.path.exists(self.filepath):
            return []
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, list):
                    return []
                return data
        except (json.JSONDecodeError, IOError):
            # If the file is corrupted or unreadable, return an empty list
            return []

    def save(self, data: list) -> None:
        """Saves todo list to JSON file."""
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"Error saving todo data: {e}")
