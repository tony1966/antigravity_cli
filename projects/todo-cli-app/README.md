# Todo CLI App

一個用 Python 寫的輕量級待辦事項命令列工具（CLI App），使用 JSON 檔案儲存資料。

## 支援功能
- 新增待辦事項：`add`
- 列出待辦事項：`list`（支援過濾：`--done`、`--pending`、`--all`）
- 完成待辦事項：`done`
- 刪除待辦事項：`delete`

---

## 安裝與執行

確保你已安裝 Python 3.8+。

### 1. 新增待辦事項 (Add)
```bash
python main.py add "購買新鮮牛奶"
python main.py add "練習 Python 程式碼"
```

### 2. 列出待辦事項 (List)
- 列出所有事項：
  ```bash
  python main.py list
  ```
- 僅列出未完成事項：
  ```bash
  python main.py list --pending
  ```
- 僅列出已完成事項：
  ```bash
  python main.py list --done
  ```

### 3. 完成待辦事項 (Done)
將指定 ID 的事項標記為已完成：
```bash
python main.py done 1
```

### 4. 刪除待辦事項 (Delete)
將指定 ID 的事項刪除：
```bash
python main.py delete 2
```

---

## 專案結構

- [main.py](file:///D:/agy/todo-cli-app/main.py): 進入點。
- [todo/cli.py](file:///D:/agy/todo-cli-app/todo/cli.py): 負責 CLI 解析與輸出排版。
- [todo/manager.py](file:///D:/agy/todo-cli-app/todo/manager.py): 核心邏輯（新增、列出、完成、刪除）。
- [todo/storage.py](file:///D:/agy/todo-cli-app/todo/storage.py): JSON 檔案載入與儲存。
- `todo_data.json`: 儲存待辦事項資料（自動生成於執行目錄中）。
