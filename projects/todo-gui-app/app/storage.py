"""
storage.py — Todo 資料持久化層
負責所有 CRUD 操作與 JSON 檔案讀寫。
UI 元件不直接碰資料，全部透過此類別操作。
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

TODO_FILE = Path(__file__).parent.parent / "data" / "todos.json"


class TodoStorage:
    """
    管理 Todo 資料的讀取、儲存與操作。

    資料結構（每筆 Todo）：
    {
        "id":         str (UUID4),
        "text":       str,
        "done":       bool,
        "created_at": str (ISO 8601)
    }
    """

    def __init__(self):
        self._todos: List[Dict[str, Any]] = []
        self._ensure_data_dir()
        self.load()

    # ─── 私有工具 ───────────────────────────────────────────────

    def _ensure_data_dir(self) -> None:
        """確保 data/ 資料夾存在。"""
        TODO_FILE.parent.mkdir(parents=True, exist_ok=True)

    def _new_id(self) -> str:
        return str(uuid.uuid4())

    def _now_iso(self) -> str:
        return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    # ─── 讀寫 ───────────────────────────────────────────────────

    def load(self) -> None:
        """從 JSON 檔案讀取資料；若檔案不存在或格式錯誤則初始化為空清單。"""
        if not TODO_FILE.exists():
            self._todos = []
            return
        try:
            with TODO_FILE.open("r", encoding="utf-8") as f:
                data = json.load(f)
            # 基本驗證：必須是 list
            if not isinstance(data, list):
                self._todos = []
            else:
                self._todos = data
        except (json.JSONDecodeError, OSError):
            self._todos = []

    def save(self) -> None:
        """將目前資料寫回 JSON 檔案。"""
        with TODO_FILE.open("w", encoding="utf-8") as f:
            json.dump(self._todos, f, ensure_ascii=False, indent=2)

    # ─── CRUD ───────────────────────────────────────────────────

    def add(self, text: str) -> Optional[Dict[str, Any]]:
        """
        新增一筆 Todo。
        - 若 text 為空字串（去除首尾空白後）則回傳 None，不新增。
        - 成功則回傳新建立的 Todo dict。
        """
        text = text.strip()
        if not text:
            return None

        todo = {
            "id":         self._new_id(),
            "text":       text,
            "done":       False,
            "created_at": self._now_iso(),
        }
        self._todos.append(todo)
        self.save()
        return todo

    def toggle_done(self, todo_id: str) -> bool:
        """
        切換指定 Todo 的完成狀態。
        回傳切換後的 done 值；若找不到 ID 則回傳 False。
        """
        for todo in self._todos:
            if todo["id"] == todo_id:
                todo["done"] = not todo["done"]
                self.save()
                return todo["done"]
        return False

    def delete(self, todo_id: str) -> bool:
        """
        刪除指定 Todo。
        回傳 True（成功）或 False（找不到）。
        """
        original_len = len(self._todos)
        self._todos = [t for t in self._todos if t["id"] != todo_id]
        if len(self._todos) < original_len:
            self.save()
            return True
        return False

    def get_all(self) -> List[Dict[str, Any]]:
        """回傳所有 Todo 的副本（依建立時間排序，最新在後）。"""
        return list(self._todos)

    def get_by_id(self, todo_id: str) -> Optional[Dict[str, Any]]:
        """依 ID 查詢單筆 Todo；找不到回傳 None。"""
        for todo in self._todos:
            if todo["id"] == todo_id:
                return dict(todo)
        return None

    # ─── 統計 ───────────────────────────────────────────────────

    def count_total(self) -> int:
        return len(self._todos)

    def count_done(self) -> int:
        return sum(1 for t in self._todos if t["done"])

    def count_pending(self) -> int:
        return sum(1 for t in self._todos if not t["done"])
