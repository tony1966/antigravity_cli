# Todo Web App 🌐

全功能的待辦事項 Web 應用程式，以 **Python Flask** 為後端、**原生 HTML/CSS/JS** 為前端，支援 AJAX 非同步操作，資料格式與 CLI 版完全相容。

## 功能特色

- ✅ **新增** 待辦事項
- 📋 **檢視** 全部 / 未完成 / 已完成清單（即時篩選）
- ✔️ **標記完成**（AJAX，不重新整理頁面）
- 🗑️ **刪除**（AJAX，滑出動畫）
- 💾 資料持久化至 `todo_data.json`（與 CLI 版格式相容）
- 🌙 深色主題 + 玻璃擬態設計
- 📱 RWD 響應式排版

## 技術架構

```
Browser (HTML + CSS + Fetch API)
        ↕ HTTP / JSON (AJAX)
Python Flask (REST API)
        ↕ 讀寫
todo_data.json
```

## 快速開始

### 1. 安裝相依套件

```bash
pip install -r requirements.txt
```

### 2. 啟動伺服器

```bash
python app.py
```

### 3. 開啟瀏覽器

```
http://localhost:5000
```

## REST API 端點

| Method | Endpoint | 說明 |
|---|---|---|
| `GET` | `/api/todos` | 取得所有 Todo（可加 `?status=done\|pending`）|
| `POST` | `/api/todos` | 新增 Todo（Body: `{"title": "..."}`) |
| `PATCH` | `/api/todos/<id>/done` | 標記完成 |
| `DELETE` | `/api/todos/<id>` | 刪除 Todo |

## 資料格式

`todo_data.json` 與 CLI 版完全相容：

```json
[
  {
    "id": 1,
    "title": "Buy fresh milk",
    "done": true,
    "created_at": "2026-07-01T08:15:30.657339"
  }
]
```

## 專案架構

```
todo-web-app/
├── app.py               # Flask 主程式
├── todo/
│   ├── storage.py       # JSON 讀寫（Thread-safe）
│   └── manager.py       # 業務邏輯
├── static/
│   ├── css/style.css    # 自訂樣式
│   └── js/app.js        # 前端 JS
├── templates/
│   └── index.html       # 主頁面
├── todo_data.json        # 資料儲存
└── requirements.txt
```
