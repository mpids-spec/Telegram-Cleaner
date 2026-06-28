"""
TG Cleaner — Telegram Group & Channel Manager
https://github.com/YOUR_USERNAME/tg-cleaner

Requires: pip install -r requirements.txt
Run:      py tg_cleaner_app.py
Open:     http://localhost:5000
"""

from flask import Flask, render_template_string, jsonify, request
from telethon import TelegramClient
from telethon.tl.types import Channel, Chat
from telethon.tl.functions.channels import LeaveChannelRequest
import asyncio
import threading
import os
import time

# ──────────────────────────────────────────────────────────────
# GET YOUR API KEYS AT: https://my.telegram.org → App configuration
# Set them as environment variables OR paste directly here
# ──────────────────────────────────────────────────────────────
API_ID   = int(os.environ.get("TG_API_ID", 0))
API_HASH = os.environ.get("TG_API_HASH", "")

# Or paste directly (not recommended for public repos):
# API_ID   = 12345678
# API_HASH = "your_hash_here"
# ──────────────────────────────────────────────────────────────

SESSION_NAME = "tg_cleaner_session"

app = Flask(__name__)
app.secret_key = os.urandom(24)

client = None
loop = None

HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>TG Cleaner</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

  :root {
    --bg: #0d0f14;
    --surface: #161920;
    --surface2: #1e2230;
    --border: #2a2f3d;
    --accent: #5b8af0;
    --accent2: #7c5cf0;
    --danger: #f05b5b;
    --success: #5bf0a0;
    --text: #e8eaf0;
    --muted: #6b7290;
  }

  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: 'Inter', sans-serif; background: var(--bg); color: var(--text); min-height: 100vh; }

  header {
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    padding: 18px 32px;
    display: flex; align-items: center; gap: 14px;
    position: sticky; top: 0; z-index: 100;
  }
  .logo {
    width: 36px; height: 36px;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px;
  }
  header h1 { font-size: 18px; font-weight: 600; letter-spacing: -0.3px; }
  header span { color: var(--muted); font-size: 13px; margin-left: auto; }

  .container { max-width: 1100px; margin: 0 auto; padding: 28px 24px; }

  .auth-card {
    max-width: 420px; margin: 80px auto;
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 16px; padding: 36px; text-align: center;
  }
  .auth-card .icon { font-size: 48px; margin-bottom: 16px; }
  .auth-card h2 { font-size: 22px; font-weight: 600; margin-bottom: 8px; }
  .auth-card p { color: var(--muted); font-size: 14px; margin-bottom: 24px; line-height: 1.6; }
  .auth-card input {
    width: 100%; padding: 12px 16px;
    background: var(--bg); border: 1px solid var(--border);
    border-radius: 10px; color: var(--text); font-size: 15px;
    margin-bottom: 12px; outline: none; transition: border-color .2s; font-family: inherit;
  }
  .auth-card input:focus { border-color: var(--accent); }

  .btn {
    padding: 11px 22px; border-radius: 10px; border: none;
    font-size: 14px; font-weight: 500; cursor: pointer;
    transition: all .15s; font-family: inherit;
    display: inline-flex; align-items: center; gap: 7px;
  }
  .btn-primary { background: var(--accent); color: #fff; width: 100%; justify-content: center; }
  .btn-primary:hover { background: #4a78e0; }
  .btn-danger { background: var(--danger); color: #fff; }
  .btn-danger:hover { background: #e04a4a; }
  .btn-ghost { background: var(--surface2); color: var(--text); border: 1px solid var(--border); }
  .btn-ghost:hover { background: var(--border); }
  .btn:disabled { opacity: .5; cursor: not-allowed; }

  .filters-bar {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 14px; padding: 20px 24px; margin-bottom: 20px;
    display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; align-items: end;
  }
  .filter-group label {
    display: block; font-size: 11px; font-weight: 600; color: var(--muted);
    text-transform: uppercase; letter-spacing: .8px; margin-bottom: 8px;
  }
  .filter-group input, .filter-group select {
    width: 100%; padding: 9px 12px;
    background: var(--bg); border: 1px solid var(--border);
    border-radius: 8px; color: var(--text); font-size: 13px;
    outline: none; font-family: inherit; transition: border-color .2s;
  }
  .filter-group input:focus, .filter-group select:focus { border-color: var(--accent); }
  .filter-group select option { background: var(--surface2); }

  .toolbar { display: flex; align-items: center; gap: 10px; margin-bottom: 14px; flex-wrap: wrap; }
  .toolbar .count { font-size: 13px; color: var(--muted); margin-left: auto; }
  .selected-count {
    background: var(--accent); color: #fff;
    padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 600;
  }

  .table-wrap { background: var(--surface); border: 1px solid var(--border); border-radius: 14px; overflow: hidden; }
  table { width: 100%; border-collapse: collapse; }
  thead th {
    padding: 13px 16px; text-align: left; font-size: 11px; font-weight: 600;
    color: var(--muted); text-transform: uppercase; letter-spacing: .7px;
    border-bottom: 1px solid var(--border); background: var(--surface2);
    cursor: pointer; user-select: none;
  }
  thead th:hover { color: var(--text); }
  thead th:first-child { width: 44px; }
  tbody tr { border-bottom: 1px solid var(--border); transition: background .1s; }
  tbody tr:last-child { border-bottom: none; }
  tbody tr:hover { background: var(--surface2); }
  tbody tr.selected { background: rgba(91,138,240,.08); }
  td { padding: 13px 16px; font-size: 13px; vertical-align: middle; }

  .chat-name { font-weight: 500; }
  .chat-sub { font-size: 11px; color: var(--muted); margin-top: 2px; }

  .badge { display: inline-block; padding: 3px 9px; border-radius: 20px; font-size: 11px; font-weight: 600; }
  .badge-channel  { background: #1a2a50; color: #7aabf0; }
  .badge-group    { background: #1a3030; color: #7af0d0; }
  .badge-mega     { background: #2a1a50; color: #b07af0; }

  .unread-badge { background: var(--accent); color: #fff; padding: 3px 9px; border-radius: 20px; font-size: 11px; font-weight: 700; }
  .unread-zero  { color: var(--muted); }

  .role-badge { padding: 3px 9px; border-radius: 20px; font-size: 11px; font-weight: 600; }
  .role-member  { background: #1a2a1a; color: #7af070; }
  .role-admin   { background: #2a2010; color: #f0c070; }
  .role-creator { background: #2a1010; color: #f07070; }

  .inactive-warn { color: #f0a050; font-weight: 600; }

  input[type=checkbox] { width: 16px; height: 16px; accent-color: var(--accent); cursor: pointer; }

  .empty-state { text-align: center; padding: 60px 20px; color: var(--muted); }
  .empty-state .icon { font-size: 48px; margin-bottom: 12px; }

  .modal-overlay {
    display: none; position: fixed; inset: 0;
    background: rgba(0,0,0,.7); z-index: 200;
    align-items: center; justify-content: center;
  }
  .modal-overlay.show { display: flex; }
  .modal {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 16px; padding: 32px; max-width: 440px; width: 90%; text-align: center;
  }
  .modal h3 { font-size: 18px; margin-bottom: 10px; }
  .modal p  { color: var(--muted); font-size: 14px; margin-bottom: 24px; line-height: 1.6; }
  .modal-btns { display: flex; gap: 10px; justify-content: center; }

  .progress-bar { background: var(--border); border-radius: 4px; height: 4px; margin: 16px 0 0; overflow: hidden; display: none; }
  .progress-fill { background: linear-gradient(90deg, var(--accent), var(--accent2)); height: 100%; width: 0%; border-radius: 4px; transition: width .3s; }

  .toast {
    position: fixed; bottom: 24px; right: 24px;
    background: var(--surface2); border: 1px solid var(--border);
    border-radius: 12px; padding: 14px 20px; font-size: 14px;
    display: flex; align-items: center; gap: 10px;
    box-shadow: 0 8px 32px rgba(0,0,0,.4); z-index: 999;
    transform: translateY(100px); opacity: 0; transition: all .3s; max-width: 380px;
  }
  .toast.show { transform: translateY(0); opacity: 1; }
  .toast.success { border-color: var(--success); }
  .toast.error   { border-color: var(--danger); }

  .no-keys-banner {
    background: rgba(240,91,91,.1); border: 1px solid var(--danger);
    border-radius: 12px; padding: 16px 20px; margin-bottom: 20px;
    font-size: 13px; line-height: 1.6;
  }
  .no-keys-banner a { color: var(--accent); }
</style>
</head>
<body>

<header>
  <div class="logo">🧹</div>
  <h1>TG Cleaner</h1>
  <span id="header-status"></span>
</header>

<div id="auth-screen">
  <div class="auth-card">
    <div class="icon">📱</div>
    <h2>Войти в Telegram</h2>
    <p>Введи номер телефона в формате +1... — получишь код в Telegram</p>
    <div id="auth-step1">
      <input id="phone" type="tel" placeholder="+1 (403) 000-0000" />
      <button class="btn btn-primary" onclick="sendPhone()">Получить код →</button>
    </div>
    <div id="auth-step2" style="display:none">
      <input id="code" type="text" placeholder="Код из Telegram" maxlength="6" />
      <button class="btn btn-primary" onclick="sendCode()">Войти →</button>
    </div>
    <div id="auth-step3" style="display:none">
      <input id="password" type="password" placeholder="Пароль 2FA" />
      <button class="btn btn-primary" onclick="sendPassword()">Подтвердить →</button>
    </div>
    <div id="auth-msg" style="margin-top:14px;font-size:13px;color:var(--muted)"></div>
  </div>
</div>

<div id="main-app" style="display:none">
  <div class="container">

    <div class="filters-bar">
      <div class="filter-group">
        <label>🔍 Поиск</label>
        <input id="f-search" type="text" placeholder="Название..." oninput="applyFilters()">
      </div>
      <div class="filter-group">
        <label>📅 Не заходил (мес.)</label>
        <select id="f-inactive" onchange="applyFilters()">
          <option value="0">Все</option>
          <option value="1">1+ месяц</option>
          <option value="3">3+ месяца</option>
          <option value="6">6+ месяцев</option>
          <option value="12">1+ год</option>
          <option value="24">2+ года</option>
        </select>
      </div>
      <div class="filter-group">
        <label>💬 Мои сообщения</label>
        <select id="f-msgs" onchange="applyFilters()">
          <option value="all">Все</option>
          <option value="no">Никогда не писал</option>
          <option value="yes">Писал</option>
        </select>
      </div>
      <div class="filter-group">
        <label>📢 Тип</label>
        <select id="f-type" onchange="applyFilters()">
          <option value="all">Все</option>
          <option value="channel">Каналы</option>
          <option value="group">Группы</option>
          <option value="megagroup">Супергруппы</option>
        </select>
      </div>
      <div class="filter-group">
        <label>🔔 Непрочитанные</label>
        <select id="f-unread" onchange="applyFilters()">
          <option value="all">Все</option>
          <option value="yes">Есть</option>
          <option value="no">Нет</option>
        </select>
      </div>
      <div class="filter-group">
        <label>👤 Роль</label>
        <select id="f-role" onchange="applyFilters()">
          <option value="all">Все</option>
          <option value="member">Участник</option>
          <option value="admin">Админ</option>
          <option value="creator">Создатель</option>
        </select>
      </div>
    </div>

    <div class="toolbar">
      <button class="btn btn-ghost" onclick="selectAll()">☑ Все</button>
      <button class="btn btn-ghost" onclick="selectNone()">✕ Сбросить</button>
      <button class="btn btn-ghost" onclick="selectFiltered()">⚡ Отфильтрованные</button>
      <span id="selected-count" class="selected-count" style="display:none">0 выбрано</span>
      <span class="count" id="shown-count"></span>
      <button class="btn btn-danger" id="leave-btn" onclick="confirmLeave()" disabled>🚪 Выйти из выбранных</button>
      <button class="btn btn-ghost" onclick="markAllRead()">✅ Пометить прочитанными</button>
    </div>

    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th><input type="checkbox" id="check-all" onchange="toggleAll(this)"></th>
            <th onclick="sortBy('name')">Название</th>
            <th onclick="sortBy('type')">Тип</th>
            <th onclick="sortBy('unread')">Непрочит. ▾</th>
            <th onclick="sortBy('inactive')">Последний заход</th>
            <th onclick="sortBy('msgs')">Мои сообщ.</th>
            <th>Роль</th>
          </tr>
        </thead>
        <tbody id="table-body">
          <tr><td colspan="7">
            <div class="empty-state"><div class="icon">⏳</div><p>Загрузка...</p></div>
          </td></tr>
        </tbody>
      </table>
    </div>

  </div>
</div>

<div class="modal-overlay" id="modal">
  <div class="modal">
    <h3>⚠️ Подтверждение</h3>
    <p id="modal-text"></p>
    <div class="modal-btns">
      <button class="btn btn-ghost" onclick="closeModal()">Отмена</button>
      <button class="btn btn-danger" onclick="doLeave()">Выйти</button>
    </div>
    <div class="progress-bar" id="progress-bar">
      <div class="progress-fill" id="progress-fill"></div>
    </div>
  </div>
</div>

<div class="toast" id="toast"></div>

<script>
let allDialogs = [], filtered = [], selected = new Set();
let sortCol = 'unread', sortDir = -1, phone_hash = '';

async function sendPhone() {
  const phone = document.getElementById('phone').value.trim();
  if (!phone) return;
  setAuthMsg('Отправляю код...');
  const r = await fetch('/auth/phone', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({phone})});
  const d = await r.json();
  if (d.ok) {
    phone_hash = d.phone_code_hash;
    document.getElementById('auth-step1').style.display = 'none';
    document.getElementById('auth-step2').style.display = 'block';
    setAuthMsg('Код отправлен ✅');
  } else { setAuthMsg('Ошибка: ' + d.error); }
}

async function sendCode() {
  const phone = document.getElementById('phone').value.trim();
  const code = document.getElementById('code').value.trim();
  setAuthMsg('Проверяю...');
  const r = await fetch('/auth/code', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({phone, code, phone_code_hash: phone_hash})});
  const d = await r.json();
  if (d.ok) startApp();
  else if (d.need_password) {
    document.getElementById('auth-step2').style.display = 'none';
    document.getElementById('auth-step3').style.display = 'block';
    setAuthMsg('Введи пароль 2FA');
  } else { setAuthMsg('Ошибка: ' + d.error); }
}

async function sendPassword() {
  const password = document.getElementById('password').value;
  setAuthMsg('Проверяю...');
  const r = await fetch('/auth/password', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({password})});
  const d = await r.json();
  if (d.ok) startApp(); else setAuthMsg('Ошибка: ' + d.error);
}

function setAuthMsg(t) { document.getElementById('auth-msg').textContent = t; }

async function checkAuth() {
  const r = await fetch('/auth/check');
  const d = await r.json();
  if (d.ok) startApp();
}

function startApp() {
  document.getElementById('auth-screen').style.display = 'none';
  document.getElementById('main-app').style.display = 'block';
  loadDialogs();
}

async function loadDialogs() {
  document.getElementById('header-status').textContent = '⏳ Загружаю...';
  const r = await fetch('/dialogs');
  const d = await r.json();
  if (d.error) { showToast('Ошибка: ' + d.error, 'error'); return; }
  allDialogs = d.dialogs;
  document.getElementById('header-status').textContent = allDialogs.length + ' чатов';
  applyFilters();
}

function applyFilters() {
  const search   = document.getElementById('f-search').value.toLowerCase();
  const inactive = parseInt(document.getElementById('f-inactive').value);
  const msgs     = document.getElementById('f-msgs').value;
  const type     = document.getElementById('f-type').value;
  const unread   = document.getElementById('f-unread').value;
  const role     = document.getElementById('f-role').value;
  const now = Date.now() / 1000;

  filtered = allDialogs.filter(d => {
    if (search && !d.name.toLowerCase().includes(search)) return false;
    if (inactive > 0 && (now - d.last_message_ts) / (60*60*24*30) < inactive) return false;
    if (msgs === 'no' && d.my_messages > 0) return false;
    if (msgs === 'yes' && d.my_messages === 0) return false;
    if (type !== 'all' && d.type !== type) return false;
    if (unread === 'yes' && d.unread === 0) return false;
    if (unread === 'no' && d.unread > 0) return false;
    if (role !== 'all' && d.role !== role) return false;
    return true;
  });

  filtered.sort((a, b) => {
    let va = a[sortCol], vb = b[sortCol];
    if (typeof va === 'string') return sortDir * va.localeCompare(vb);
    return sortDir * (va - vb);
  });

  renderTable();
}

function sortBy(col) {
  if (sortCol === col) sortDir *= -1; else { sortCol = col; sortDir = -1; }
  applyFilters();
}

function renderTable() {
  const tbody = document.getElementById('table-body');
  document.getElementById('shown-count').textContent = `Показано: ${filtered.length} из ${allDialogs.length}`;

  if (!filtered.length) {
    tbody.innerHTML = `<tr><td colspan="7"><div class="empty-state"><div class="icon">🔍</div><p>Ничего не найдено</p></div></td></tr>`;
    return;
  }

  const now = Date.now() / 1000;
  tbody.innerHTML = filtered.map(d => {
    const sel = selected.has(d.id) ? 'selected' : '';
    const chk = selected.has(d.id) ? 'checked' : '';
    const months = Math.floor((now - d.last_message_ts) / (60*60*24*30));
    const lastStr = months === 0 ? 'Недавно' : months < 12 ? `${months} мес. назад` : `${Math.floor(months/12)} г. назад`;
    const inactiveCls = months >= 3 ? 'inactive-warn' : '';
    const typeBadge = {channel:'<span class="badge badge-channel">📢 Канал</span>', group:'<span class="badge badge-group">👥 Группа</span>', megagroup:'<span class="badge badge-mega">⚡ Супергруппа</span>'}[d.type] || d.type;
    const roleBadge = {member:'<span class="role-badge role-member">Участник</span>', admin:'<span class="role-badge role-admin">Админ</span>', creator:'<span class="role-badge role-creator">Создатель</span>'}[d.role] || d.role;
    const unreadBadge = d.unread > 0 ? `<span class="unread-badge">${d.unread >= 1000 ? Math.floor(d.unread/1000)+'k+' : d.unread}</span>` : `<span class="unread-zero">—</span>`;
    const myMsgs = d.my_messages > 0 ? d.my_messages : `<span style="color:var(--muted)">—</span>`;
    return `<tr class="${sel}" onclick="toggleRow(${d.id},event)">
      <td><input type="checkbox" ${chk} onchange="toggleSelect(${d.id})" onclick="event.stopPropagation()"></td>
      <td><div class="chat-name">${esc(d.name)}</div><div class="chat-sub">${d.members > 0 ? d.members.toLocaleString()+' участников' : ''}</div></td>
      <td>${typeBadge}</td>
      <td>${unreadBadge}</td>
      <td class="${inactiveCls}">${lastStr}</td>
      <td>${myMsgs}</td>
      <td>${roleBadge}</td>
    </tr>`;
  }).join('');

  updateSelectionUI();
}

function esc(s) { return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }

function toggleRow(id, e) { if (e.target.type==='checkbox') return; toggleSelect(id); }
function toggleSelect(id) { selected.has(id) ? selected.delete(id) : selected.add(id); renderTable(); }
function toggleAll(cb) { cb.checked ? filtered.forEach(d=>selected.add(d.id)) : selected.clear(); renderTable(); }
function selectAll()      { allDialogs.forEach(d=>selected.add(d.id)); renderTable(); }
function selectNone()     { selected.clear(); renderTable(); }
function selectFiltered() { filtered.forEach(d=>selected.add(d.id)); renderTable(); }

function updateSelectionUI() {
  const n = selected.size;
  const cnt = document.getElementById('selected-count');
  document.getElementById('leave-btn').disabled = n === 0;
  cnt.style.display = n > 0 ? 'inline' : 'none';
  if (n > 0) cnt.textContent = `${n} выбрано`;
}

function confirmLeave() {
  const names = [...selected].map(id=>allDialogs.find(d=>d.id===id)?.name).filter(Boolean);
  const preview = names.slice(0,5).map(n=>`• ${n}`).join('<br>');
  const more = names.length > 5 ? `<br>...и ещё ${names.length-5}` : '';
  document.getElementById('modal-text').innerHTML = `Выйти из <b>${names.length}</b> групп/каналов?<br><br><small style="color:var(--muted)">${preview}${more}</small>`;
  document.getElementById('modal').classList.add('show');
}

function closeModal() { document.getElementById('modal').classList.remove('show'); }

async function doLeave() {
  const ids = [...selected];
  const bar = document.getElementById('progress-bar');
  const fill = document.getElementById('progress-fill');
  bar.style.display = 'block';
  let done = 0;
  for (const id of ids) {
    const r = await fetch('/leave', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({id})});
    const d = await r.json();
    done++;
    fill.style.width = (done/ids.length*100) + '%';
    if (d.ok) { selected.delete(id); allDialogs = allDialogs.filter(x=>x.id!==id); }
  }
  closeModal();
  bar.style.display = 'none'; fill.style.width = '0%';
  showToast(`✅ Вышел из ${done} чатов`, 'success');
  applyFilters();
}

async function markAllRead() {
  showToast('⏳ Помечаю прочитанными...', '');
  const r = await fetch('/mark_read', {method:'POST'});
  const d = await r.json();
  showToast(`✅ Помечено: ${d.count}`, 'success');
  allDialogs.forEach(x=>x.unread=0);
  applyFilters();
}

function showToast(msg, type) {
  const t = document.getElementById('toast');
  t.textContent = msg; t.className = 'toast show ' + (type||'');
  setTimeout(()=>t.classList.remove('show'), 3500);
}

checkAuth();
</script>
</body>
</html>
"""

def run_async(coro):
    return asyncio.run_coroutine_threadsafe(coro, loop).result(timeout=120)

async def get_client():
    global client
    if client is None:
        client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    if not client.is_connected():
        await client.connect()
    return client

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/auth/check')
def auth_check():
    try:
        c = run_async(get_client())
        ok = run_async(c.is_user_authorized())
        return jsonify({'ok': ok})
    except:
        return jsonify({'ok': False})

@app.route('/auth/phone', methods=['POST'])
def auth_phone():
    try:
        phone = request.json['phone']
        c = run_async(get_client())
        result = run_async(c.send_code_request(phone))
        return jsonify({'ok': True, 'phone_code_hash': result.phone_code_hash})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)})

@app.route('/auth/code', methods=['POST'])
def auth_code():
    try:
        data = request.json
        c = run_async(get_client())
        run_async(c.sign_in(data['phone'], data['code'], phone_code_hash=data['phone_code_hash']))
        return jsonify({'ok': True})
    except Exception as e:
        err = str(e)
        if 'Two-steps' in err or 'password' in err.lower():
            return jsonify({'ok': False, 'need_password': True})
        return jsonify({'ok': False, 'error': err})

@app.route('/auth/password', methods=['POST'])
def auth_password():
    try:
        c = run_async(get_client())
        run_async(c.sign_in(password=request.json['password']))
        return jsonify({'ok': True})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)})

@app.route('/dialogs')
def get_dialogs():
    try:
        async def _load():
            c = await get_client()
            dialogs = await c.get_dialogs(limit=500)
            result = []
            for d in dialogs:
                entity = d.entity
                if not isinstance(entity, (Channel, Chat)):
                    continue
                if isinstance(entity, Channel):
                    dtype = 'channel' if entity.broadcast else ('megagroup' if entity.megagroup else 'group')
                else:
                    dtype = 'group'
                role = 'creator' if getattr(entity, 'creator', False) else ('admin' if getattr(entity, 'admin_rights', None) else 'member')
                last_ts = int(d.message.date.timestamp()) if d.message and d.message.date else 0
                result.append({
                    'id': entity.id, 'name': d.name or '(без названия)',
                    'type': dtype, 'unread': d.unread_count,
                    'last_message_ts': last_ts, 'my_messages': 0,
                    'members': getattr(entity, 'participants_count', 0) or 0,
                    'role': role,
                })
            return result
        return jsonify({'dialogs': run_async(_load())})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/leave', methods=['POST'])
def leave_chat():
    try:
        chat_id = request.json['id']
        async def _leave():
            c = await get_client()
            entity = await c.get_entity(chat_id)
            if isinstance(entity, Channel):
                await c(LeaveChannelRequest(entity))
            else:
                from telethon.tl.functions.messages import DeleteChatUserRequest
                me = await c.get_me()
                await c(DeleteChatUserRequest(entity.id, me))
        run_async(_leave())
        return jsonify({'ok': True})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)})

@app.route('/mark_read', methods=['POST'])
def mark_read():
    try:
        async def _read():
            c = await get_client()
            dialogs = await c.get_dialogs(limit=500)
            count = 0
            for d in dialogs:
                if d.unread_count > 0:
                    try:
                        await c.send_read_acknowledge(d.entity)
                        count += 1
                    except:
                        pass
            return count
        return jsonify({'ok': True, 'count': run_async(_read())})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)})

def start_loop():
    global loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_forever()

if __name__ == '__main__':
    if not API_ID or not API_HASH:
        print("\n" + "="*55)
        print("  ❌  Заполни API_ID и API_HASH!")
        print("  Получить: https://my.telegram.org → App configuration")
        print("  Открой tg_cleaner_app.py и вставь свои ключи")
        print("="*55 + "\n")
        exit(1)
    t = threading.Thread(target=start_loop, daemon=True)
    t.start()
    time.sleep(0.3)
    print("\n" + "="*50)
    print("  🧹 TG Cleaner запущен!")
    print("  Открой: http://localhost:5000")
    print("="*50 + "\n")
    app.run(host='127.0.0.1', port=5000, debug=False)
