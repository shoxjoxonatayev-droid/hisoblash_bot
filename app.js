/* =============================================
   HISOBLAGICH — app.js (Bot integratsiyali)
   ============================================= */

const SECTIONS = ['restoran', 'mehmonxona', 'shaxsiy'];

const state = {
  restoran:   [],
  mehmonxona: [],
  shaxsiy:    []
};

let tg = null;

// ---- INIT ----
document.addEventListener('DOMContentLoaded', () => {
  initTelegram();
  loadFromStorage();
  setDate();
  SECTIONS.forEach(renderSection);
});

// =============================================
// TELEGRAM MINI APP
// =============================================
function initTelegram() {
  if (!window.Telegram || !window.Telegram.WebApp) return;
  tg = window.Telegram.WebApp;
  tg.expand();
  tg.ready();

  // Foydalanuvchi ismi
  const user = tg.initDataUnsafe && tg.initDataUnsafe.user;
  if (user) {
    const badge = document.getElementById('userBadge');
    if (badge) badge.textContent = '👤 ' + (user.first_name || 'Foydalanuvchi');
  }

  // Main button — Saqlash
  tg.MainButton.setText('💾 Botga saqlash');
  tg.MainButton.color = '#2CA5E0';
  tg.MainButton.show();
  tg.MainButton.onClick(sendDataToBot);
}

// =============================================
// BOTGA MA'LUMOT YUBORISH
// =============================================
function sendDataToBot() {
  if (!tg) {
    showToast('⚠️ Telegram WebApp topilmadi');
    return;
  }
  const hasData = SECTIONS.some(s => state[s].length > 0);
  if (!hasData) {
    showToast('ℹ️ Hali hech qanday yozuv yo\'q');
    return;
  }
  tg.MainButton.showProgress(false);
  try {
    tg.sendData(JSON.stringify(state));
  } catch(e) {
    tg.MainButton.hideProgress();
    showToast('⚠️ Yuborishda xato: ' + e.message);
  }
}

// ---- DATE ----
function setDate() {
  const el = document.getElementById('appDate');
  if (!el) return;
  const now = new Date();
  el.textContent = now.toLocaleDateString('uz-UZ', {
    year: 'numeric', month: 'long', day: 'numeric'
  });
}

// =============================================
// TAB SWITCHING
// =============================================
function switchTab(tab) {
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.tab === tab);
  });
  document.querySelectorAll('.tab-panel').forEach(panel => {
    panel.classList.toggle('active', panel.id === 'tab-' + tab);
  });
}

// =============================================
// ADD ENTRY
// =============================================
function addEntry(section, type) {
  const descEl   = document.getElementById(section + '-desc');
  const amountEl = document.getElementById(section + '-amount');

  const desc   = descEl.value.trim();
  const amount = parseFloat(amountEl.value);

  if (!desc) {
    showToast('⚠️ Tavsif kiriting!');
    descEl.focus();
    return;
  }
  if (!amount || amount <= 0) {
    showToast('⚠️ To\'g\'ri summa kiriting!');
    amountEl.focus();
    return;
  }

  const entry = {
    id:     Date.now(),
    desc:   desc,
    amount: amount,
    type:   type,
    time:   getNowTime()
  };

  state[section].unshift(entry);
  saveToStorage();
  renderSection(section);

  descEl.value   = '';
  amountEl.value = '';
  descEl.focus();

  const label = type === 'income' ? '✅ Kirim qo\'shildi' : '✅ Chiqim qo\'shildi';
  showToast(label);
}

// =============================================
// DELETE ENTRY
// =============================================
function deleteEntry(section, id) {
  state[section] = state[section].filter(e => e.id !== id);
  saveToStorage();
  renderSection(section);
  showToast('🗑 Yozuv o\'chirildi');
}

// =============================================
// CLEAR ALL
// =============================================
function clearAll(section) {
  if (state[section].length === 0) {
    showToast('ℹ️ Tarix bo\'sh');
    return;
  }
  const confirmed = confirm('Bu bo\'limdagi barcha yozuvlarni o\'chirmoqchimisiz?');
  if (!confirmed) return;

  state[section] = [];
  saveToStorage();
  renderSection(section);
  showToast('🗑 Barcha yozuvlar o\'chirildi');
}

// =============================================
// RENDER SECTION
// =============================================
function renderSection(section) {
  const entries = state[section];

  let totalIncome  = 0;
  let totalExpense = 0;

  entries.forEach(e => {
    if (e.type === 'income')  totalIncome  += e.amount;
    if (e.type === 'expense') totalExpense += e.amount;
  });

  const balance = totalIncome - totalExpense;

  document.getElementById(section + '-balance').textContent  = formatMoney(balance);
  document.getElementById(section + '-income').textContent   = formatMoney(totalIncome);
  document.getElementById(section + '-expense').textContent  = formatMoney(totalExpense);

  const listEl = document.getElementById(section + '-list');
  listEl.innerHTML = '';

  if (entries.length === 0) {
    listEl.innerHTML = '<li class="empty-msg">Hali yozuv yo\'q</li>';
    return;
  }

  entries.forEach(entry => {
    const li = document.createElement('li');
    li.className = 'history-item';
    li.innerHTML = `
      <span class="item-dot ${entry.type}"></span>
      <div class="item-info">
        <div class="item-desc">${escapeHtml(entry.desc)}</div>
        <div class="item-time">${entry.time}</div>
      </div>
      <span class="item-amount ${entry.type}">
        ${entry.type === 'income' ? '+' : '−'}${formatMoney(entry.amount)}
      </span>
      <button class="item-delete" onclick="deleteEntry('${section}', ${entry.id})" title="O'chirish">×</button>
    `;
    listEl.appendChild(li);
  });
}

// =============================================
// HELPERS
// =============================================
function formatMoney(amount) {
  const num = Math.abs(amount);
  const formatted = num.toLocaleString('uz-UZ');
  return (amount < 0 ? '−' : '') + formatted + ' so\'m';
}

function getNowTime() {
  const now = new Date();
  const hh  = String(now.getHours()).padStart(2, '0');
  const mm  = String(now.getMinutes()).padStart(2, '0');
  const dd  = now.getDate();
  const mo  = now.getMonth() + 1;
  return `${dd}/${mo}  ${hh}:${mm}`;
}

function escapeHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// =============================================
// TOAST
// =============================================
let toastTimer = null;

function showToast(msg) {
  const toast = document.getElementById('toast');
  toast.textContent = msg;
  toast.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove('show'), 2200);
}

// =============================================
// LOCAL STORAGE
// =============================================
const STORAGE_KEY = 'hisoblagich_v1';

function saveToStorage() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  } catch (e) {
    console.warn('LocalStorage yozib bo\'lmadi:', e);
  }
}

function loadFromStorage() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return;
    const saved = JSON.parse(raw);
    SECTIONS.forEach(s => {
      if (Array.isArray(saved[s])) state[s] = saved[s];
    });
  } catch (e) {
    console.warn('LocalStorage o\'qib bo\'lmadi:', e);
  }
}