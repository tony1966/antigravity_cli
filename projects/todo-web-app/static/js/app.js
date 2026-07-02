/* ── JS App Logic ── */
'use strict';

// ─────────────────────────────────────────────
// State
// ─────────────────────────────────────────────
let currentFilter = 'all';   // 'all' | 'pending' | 'done'
let allTodos = [];            // local cache of current todos

// ─────────────────────────────────────────────
// DOM References
// ─────────────────────────────────────────────
const todoInput   = document.getElementById('todo-input');
const addBtn      = document.getElementById('add-btn');
const todoList    = document.getElementById('todo-list');
const filterTabs  = document.querySelectorAll('.filter-tab');
const statTotal   = document.getElementById('stat-total');
const statPending = document.getElementById('stat-pending');
const statDone    = document.getElementById('stat-done');
const toastContainer = document.getElementById('toast-container');

// ─────────────────────────────────────────────
// API Helpers
// ─────────────────────────────────────────────
async function apiFetch(url, options = {}) {
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`);
  return data;
}

// ─────────────────────────────────────────────
// Toast Notification
// ─────────────────────────────────────────────
function showToast(message, type = 'success') {
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  toastContainer.appendChild(toast);
  setTimeout(() => {
    toast.style.animation = 'toastOut 0.3s ease forwards';
    toast.addEventListener('animationend', () => toast.remove());
  }, 2800);
}

// ─────────────────────────────────────────────
// Stats Update
// ─────────────────────────────────────────────
function updateStats() {
  const total   = allTodos.length;
  const done    = allTodos.filter(t => t.done).length;
  const pending = total - done;
  statTotal.textContent   = `📋 ${total} 項`;
  statPending.textContent = `⏳ ${pending} 待辦`;
  statDone.textContent    = `✅ ${done} 完成`;
}

// ─────────────────────────────────────────────
// Date Formatter
// ─────────────────────────────────────────────
function formatDate(isoStr) {
  try {
    const d = new Date(isoStr);
    return d.toLocaleDateString('zh-TW', { month: 'short', day: 'numeric' });
  } catch { return ''; }
}

// ─────────────────────────────────────────────
// Render Todos
// ─────────────────────────────────────────────
function getFilteredTodos() {
  if (currentFilter === 'pending') return allTodos.filter(t => !t.done);
  if (currentFilter === 'done')    return allTodos.filter(t => t.done);
  return allTodos;
}

function renderTodos() {
  const filtered = getFilteredTodos();
  todoList.innerHTML = '';

  if (filtered.length === 0) {
    const labels = { all: '沒有任何待辦事項', pending: '沒有未完成的事項 🎉', done: '還沒有完成的事項' };
    todoList.innerHTML = `
      <div class="empty-state">
        <span class="empty-icon">🗂️</span>
        <p>${labels[currentFilter]}</p>
      </div>`;
    return;
  }

  filtered.forEach(todo => {
    const card = createTodoCard(todo);
    todoList.appendChild(card);
  });
}

function createTodoCard(todo) {
  const card = document.createElement('div');
  card.className = `todo-card${todo.done ? ' is-done' : ''}`;
  card.dataset.id = todo.id;

  // Done button
  const doneBtn = document.createElement('button');
  doneBtn.className = `done-btn${todo.done ? ' checked' : ''}`;
  doneBtn.title = todo.done ? '已完成' : '標記完成';
  doneBtn.setAttribute('aria-label', `標記 "${todo.title}" 為完成`);
  doneBtn.innerHTML = '✓';
  if (todo.done) doneBtn.disabled = true;
  doneBtn.addEventListener('click', () => handleMarkDone(todo.id, card, doneBtn));

  // Text
  const textEl = document.createElement('span');
  textEl.className = 'todo-text';
  textEl.textContent = todo.title;

  // Meta date
  const metaEl = document.createElement('span');
  metaEl.className = 'todo-meta';
  metaEl.textContent = formatDate(todo.created_at);

  // Delete button
  const deleteBtn = document.createElement('button');
  deleteBtn.className = 'delete-btn';
  deleteBtn.title = '刪除';
  deleteBtn.setAttribute('aria-label', `刪除 "${todo.title}"`);
  deleteBtn.innerHTML = '🗑';
  deleteBtn.addEventListener('click', () => handleDelete(todo.id, card));

  card.append(doneBtn, textEl, metaEl, deleteBtn);
  return card;
}

// ─────────────────────────────────────────────
// Load Todos from API
// ─────────────────────────────────────────────
async function loadTodos() {
  try {
    allTodos = await apiFetch('/api/todos');
    updateStats();
    renderTodos();
  } catch (err) {
    showToast('載入失敗：' + err.message, 'error');
  }
}

// ─────────────────────────────────────────────
// Add Todo
// ─────────────────────────────────────────────
async function handleAdd() {
  const title = todoInput.value.trim();
  if (!title) {
    todoInput.focus();
    todoInput.classList.add('shake');
    todoInput.addEventListener('animationend', () => todoInput.classList.remove('shake'), { once: true });
    return;
  }

  addBtn.disabled = true;
  addBtn.innerHTML = '<span class="spinner"></span>';

  try {
    const newTodo = await apiFetch('/api/todos', {
      method: 'POST',
      body: JSON.stringify({ title }),
    });
    allTodos.push(newTodo);
    todoInput.value = '';
    updateStats();
    renderTodos();
    showToast(`「${newTodo.title}」已新增 ✨`);
  } catch (err) {
    showToast('新增失敗：' + err.message, 'error');
  } finally {
    addBtn.disabled = false;
    addBtn.innerHTML = '<span>＋</span> 新增';
    todoInput.focus();
  }
}

// ─────────────────────────────────────────────
// Mark Done
// ─────────────────────────────────────────────
async function handleMarkDone(id, card, btn) {
  btn.disabled = true;
  try {
    const res = await apiFetch(`/api/todos/${id}/done`, { method: 'PATCH' });
    // Update local cache
    const cached = allTodos.find(t => t.id === id);
    if (cached) cached.done = true;
    updateStats();

    // Animate in-place before re-render
    card.classList.add('is-done');
    btn.classList.add('checked');
    btn.title = '已完成';

    // Delay re-render slightly for better UX
    setTimeout(() => renderTodos(), 400);
    showToast('事項已完成 ✅');
  } catch (err) {
    btn.disabled = false;
    showToast('操作失敗：' + err.message, 'error');
  }
}

// ─────────────────────────────────────────────
// Delete Todo
// ─────────────────────────────────────────────
async function handleDelete(id, card) {
  card.classList.add('removing');
  card.addEventListener('animationend', async () => {
    try {
      await apiFetch(`/api/todos/${id}`, { method: 'DELETE' });
      allTodos = allTodos.filter(t => t.id !== id);
      updateStats();
      renderTodos();
      showToast('事項已刪除');
    } catch (err) {
      card.classList.remove('removing');
      showToast('刪除失敗：' + err.message, 'error');
    }
  }, { once: true });
}

// ─────────────────────────────────────────────
// Filter Tabs
// ─────────────────────────────────────────────
filterTabs.forEach(tab => {
  tab.addEventListener('click', () => {
    filterTabs.forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
    currentFilter = tab.dataset.filter;
    renderTodos();
  });
});

// ─────────────────────────────────────────────
// Event Listeners
// ─────────────────────────────────────────────
addBtn.addEventListener('click', handleAdd);

todoInput.addEventListener('keydown', e => {
  if (e.key === 'Enter') handleAdd();
});

// ─────────────────────────────────────────────
// Init
// ─────────────────────────────────────────────
loadTodos();
