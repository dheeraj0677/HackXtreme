/* ═══════════════════════════════════════════════════════════════════════
   GlobalSentry — JavaScript Application
   Handles: mode switching, alert feed, pipeline demo, modal, API calls
═══════════════════════════════════════════════════════════════════════ */

// ─── Configuration ──────────────────────────────────────────────────────────
const API_BASE = 'http://localhost:8000/api';
const USE_API  = true; // FastAPI is running at localhost:8000 with /api/ prefix

// No mock data — all alerts come from live Indian RSS feeds and the AI agent pipeline.

const state = {
  activeMode: 'eco',
  alerts: [],
};

// ─── Mode Config ────────────────────────────────────────────────────────────
const MODE_CONFIG = {
  epi: {
    label: '🩺 EPI-SENTRY MODE',
    feedTitle: '🩺 Epidemic & Health Alerts',
    badge: 'EPI',
    bodyClass: 'mode-epi',
    badgeClass: 'badge-mode-epi',
  },
  eco: {
    label: '🌪️ ECO-SENTRY MODE',
    feedTitle: '🌪️ Climate & Disaster Alerts',
    badge: 'ECO',
    bodyClass: 'mode-eco',
    badgeClass: 'badge-mode-eco',
  },
  supply: {
    label: '♻️ SUPPLY-SENTRY MODE',
    feedTitle: '♻️ Supply Chain Alerts',
    badge: 'SUPPLY',
    bodyClass: 'mode-supply',
    badgeClass: 'badge-mode-supply',
  },
};

// ─── Switch Mode ────────────────────────────────────────────────────────────
function switchMode(mode) {
  if (state.activeMode === mode) return;
  state.activeMode = mode;

  // Body class
  document.body.className = MODE_CONFIG[mode].bodyClass;

  // Navbar buttons
  document.querySelectorAll('.nav-mode-btn').forEach(btn => {
    btn.classList.remove('active');
    if (btn.dataset.mode === mode) btn.classList.add('active');
  });

  // Dashboard toggle buttons
  document.querySelectorAll('.mode-toggle-btn').forEach(btn => {
    btn.classList.remove('active');
    if (btn.dataset.mode === mode) btn.classList.add('active');
  });

  // Dashboard label
  const lbl = document.getElementById('dashboard-mode-label');
  if (lbl) lbl.textContent = MODE_CONFIG[mode].label;

  // Feed title
  const ft = document.getElementById('feed-title');
  if (ft) ft.textContent = MODE_CONFIG[mode].feedTitle;

  // Sidebar mode badge
  const mb = document.getElementById('sidebar-mode-badge');
  if (mb) {
    mb.textContent = MODE_CONFIG[mode].badge;
    mb.className = `status-value mode-badge ${MODE_CONFIG[mode].badgeClass}`;
  }

  // Update last poll
  const lp = document.getElementById('status-last-poll');
  if (lp) lp.textContent = 'Just now';

  // Reload alert feed
  loadAlerts(mode);

  showToast(`Switched to ${MODE_CONFIG[mode].feedTitle}`, 'info');
}

function switchModeAndScroll(mode) {
  switchMode(mode);
  scrollToDashboard();
}

// ─── Scroll helpers ─────────────────────────────────────────────────────────
function scrollToDashboard() {
  document.getElementById('dashboard').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function scrollToSection(id) {
  document.getElementById(id).scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ─── Load Alerts ────────────────────────────────────────────────────────────
async function loadAlerts(mode) {
  const container = document.getElementById('alerts-container');
  container.innerHTML = '<div class="alert-loading"><div class="spinner"></div><span>Fetching intelligence...</span></div>';

  await sleep(600);

  let alerts = [];

  if (USE_API) {
    try {
      const resp = await fetch(`${API_BASE}/alerts?mode=${mode}&limit=50`);
      const data = await resp.json();
      // Only show agent-processed alerts — NOT raw RSS feeds
      alerts = (data.alerts || []).filter(a => a.is_raw_feed !== true);
    } catch (e) {
      console.warn('API error', e);
    }
  }

  state.alerts = alerts;
  renderAlerts(alerts);
  checkConvergence(alerts);
  updateMiniStats();
}

function renderAlerts(alerts) {
  const container = document.getElementById('alerts-container');
  container.innerHTML = '';

  if (!alerts.length) {
    container.innerHTML = '<div class="alert-loading"><span>No alerts in this mode.</span></div>';
    return;
  }

  alerts.forEach((alert, i) => {
    const card = buildAlertCard(alert, i);
    container.appendChild(card);
  });
}

function buildAlertCard(alert, index) {
  const card = document.createElement('div');
  const isRaw = alert.is_raw_feed || alert.severity === 0;
  card.className = `alert-card mode-${alert.mode} ${isRaw ? 'sev-raw' : `sev-${alert.severity}`} entering`;
  card.style.animationDelay = `${index * 60}ms`;
  card.setAttribute('data-alert-id', alert.id);

  const modeBadgeClass = `badge-${alert.mode}`;
  const timeAgo = formatTimeAgo(new Date(alert.timestamp));

  if (isRaw) {
    // Raw RSS headline — not yet processed by AI agent
    card.innerHTML = `
      <div class="alert-card-top">
        <div class="alert-headline">${escapeHtml(alert.headline)}</div>
        <div class="alert-badges">
          <span class="badge ${modeBadgeClass}">${alert.mode.toUpperCase()}</span>
          <span class="badge badge-raw">📡 RSS FEED</span>
        </div>
      </div>
      <div class="alert-card-bottom">
        <div class="alert-meta">
          <span class="alert-source">${escapeHtml(alert.source)}</span>
          <span class="alert-time">${timeAgo}</span>
        </div>
      </div>
    `;
  } else {
    // Agent-processed alert — full card with severity, analysis, and badges
    const verifiedBadge = alert.is_verified
      ? '<span class="badge badge-verified">✅ VERIFIED</span>'
      : '<span class="badge badge-unverified">⏳ UNVERIFIED</span>';

    const convergenceHtml = alert.convergence_warning
      ? `<div class="alert-convergence">🧠 ${escapeHtml(alert.convergence_warning)}</div>`
      : '';

    card.innerHTML = `
      <div class="alert-card-top">
        <div class="alert-headline">${escapeHtml(alert.headline)}</div>
        <div class="alert-badges">
          <span class="badge ${modeBadgeClass}">${alert.mode.toUpperCase()}</span>
          <span class="badge badge-agent">🤖 AI AGENT</span>
          ${verifiedBadge}
        </div>
      </div>
      <div class="alert-severity-row">
        <div class="severity-dots">${buildSeverityDots(alert.severity, alert.mode)}</div>
        <span class="alert-confidence">${Math.round((alert.confidence || 0) * 100)}% confidence</span>
      </div>
      <div class="alert-analysis">${escapeHtml((alert.analysis || '').substring(0, 300))}</div>
      ${convergenceHtml}
      <div class="alert-card-bottom">
        <div class="alert-meta">
          <span class="alert-source">${escapeHtml(alert.source || 'Agent Pipeline')}</span>
          <span class="alert-time">${timeAgo}</span>
        </div>
      </div>
    `;
  }

  return card;
}

function buildSeverityDots(severity, mode) {
  const colorMap = { epi: 'var(--epi)', eco: 'var(--eco)', supply: 'var(--supply)' };
  const color = colorMap[mode] || 'var(--mode-color)';
  let html = '';
  for (let i = 1; i <= 5; i++) {
    const filled = i <= severity;
    html += `<div class="sev-dot" style="background:${filled ? color : 'var(--border-medium)'}; opacity:${filled ? 1 : 0.3}"></div>`;
  }
  return html;
}

// ─── Convergence Panel ──────────────────────────────────────────────────────
function checkConvergence(alerts) {
  const panel = document.getElementById('convergence-panel');
  const text  = document.getElementById('convergence-text');
  const convergent = alerts.find(a => a.convergence_warning);

  if (convergent) {
    text.textContent = convergent.convergence_warning;
    panel.style.display = 'flex';
  } else {
    panel.style.display = 'none';
  }
}

function closeConvergence() {
  document.getElementById('convergence-panel').style.display = 'none';
}

// ─── Refresh & Clear ────────────────────────────────────────────────────────
function refreshFeed() {
  loadAlerts(state.activeMode);
  showToast('Feed refreshed', 'success');
}

function clearFeed() {
  const container = document.getElementById('alerts-container');
  container.innerHTML = '<div class="alert-loading"><span>Feed cleared. Click Refresh to reload.</span></div>';
  document.getElementById('convergence-panel').style.display = 'none';
  showToast('Feed cleared', 'info');
}

// ─── Autonomous Agent Status UI ──────────────────────────────────────────────
async function pollSystemStatus() {
  if (!USE_API) return;
  try {
    const resp = await fetch(`${API_BASE}/status`);
    const data = await resp.json();
    updateAutonomousUI(data.current_analysis);
  } catch (e) {
    console.warn('Failed to poll status', e);
  }
}

function updateAutonomousUI(currentAnalysis) {
  const display = document.getElementById('current-analysis-display');
  const indText = document.getElementById('active-node-text');

  if (!currentAnalysis) {
    if (display) display.innerHTML = '<em>Waiting for next signal...</em>';
    if (indText) indText.textContent = 'Idling (Waiting 20s)';
    return;
  }

  if (display) display.innerHTML = `<strong>[Mode: ${currentAnalysis.mode.toUpperCase()}]</strong> ${escapeHtml(currentAnalysis.headline)}`;
  
  const nodeNames = {
    'profiler': 'Profiler',
    'triage': 'Triage (Agent A)',
    'retriever': 'Retriever (RAG)',
    'analyst': 'Analyst (Agent B)',
    'correlator': 'Correlator (Neural Moat)',
    'validator': 'Validator (Agent C)',
    'retry': 'Reflection Loop',
    'notify': 'Notify',
    'archiver': 'Archiver'
  };
  
  const activeLabel = nodeNames[currentAnalysis.active_node] || currentAnalysis.active_node;
  if (indText) indText.textContent = `Running: ${activeLabel}...`;
}

// ─── Alert Modal ────────────────────────────────────────────────────────────
function openAlertModal(alertId) {
  const alert = state.alerts.find(a => a.id === alertId);
  if (!alert) return;

  const overlay = document.getElementById('modal-overlay');
  const title   = document.getElementById('modal-title');
  const body    = document.getElementById('modal-body');

  title.textContent = alert.headline;

  const colorMap = { epi: 'var(--epi)', eco: 'var(--eco)', supply: 'var(--supply)' };
  const color = colorMap[alert.mode];
  const sevDots = Array.from({length: 5}, (_, i) =>
    `<div class="modal-sev-dot" style="background:${i < alert.severity ? color : 'var(--border-medium)'}; opacity:${i < alert.severity ? 1 : 0.3}"></div>`
  ).join('');

  const vBadge = alert.is_verified
    ? `<span class="badge badge-verified">✓ Verified by secondary sources</span>`
    : `<span class="badge badge-unverified">⚠ Awaiting verification</span>`;

  body.innerHTML = `
    <div class="modal-section">
      <div class="modal-section-label">Badges</div>
      <div class="modal-badges">
        <span class="badge badge-${alert.mode}">${alert.mode.toUpperCase()} SENTRY</span>
        ${vBadge}
        <span class="badge" style="background:var(--bg-card);color:var(--text-secondary);border:1px solid var(--border-subtle);">
          Confidence: ${Math.round(alert.confidence * 100)}%
        </span>
      </div>
    </div>
    <div class="modal-section">
      <div class="modal-section-label">Severity Level</div>
      <div class="modal-severity-bar">
        ${sevDots}
        <span class="modal-sev-label" style="color:${color}; margin-left:10px;">${alert.severity}/5</span>
      </div>
    </div>
    <div class="modal-section">
      <div class="modal-section-label">AI Analysis</div>
      <div class="modal-section-text">${escapeHtml(alert.analysis)}</div>
    </div>
    ${alert.convergence_warning ? `
    <div class="modal-section">
      <div class="modal-section-label">Cross-Mode Convergence</div>
      <div class="modal-section-text" style="color:var(--eco);">${escapeHtml(alert.convergence_warning)}</div>
    </div>` : ''}
    <div class="modal-section">
      <div class="modal-section-label">Source & Timestamp</div>
      <div class="modal-section-text">${escapeHtml(alert.source)} · ${new Date(alert.timestamp).toLocaleString()}</div>
    </div>
  `;

  overlay.style.display = 'flex';
  document.body.style.overflow = 'hidden';
}

function closeModal(event) {
  if (event && event.target !== event.currentTarget) return;
  document.getElementById('modal-overlay').style.display = 'none';
  document.body.style.overflow = '';
}

// Close modal on Escape
document.addEventListener('keydown', e => { if (e.key === 'Escape') closeModal(); });

// ─── Mini Stats ─────────────────────────────────────────────────────────────
function updateMiniStats() {
  const epiCount    = state.alerts.filter(a => a.mode === 'epi').length;
  const ecoCount    = state.alerts.filter(a => a.mode === 'eco').length;
  const supplyCount = state.alerts.filter(a => a.mode === 'supply').length;

  const e = document.getElementById('mini-epi');
  const c = document.getElementById('mini-eco');
  const s = document.getElementById('mini-supply');
  if (e) e.textContent = epiCount || '-';
  if (c) c.textContent = ecoCount || '-';
  if (s) s.textContent = supplyCount || '-';

  // Update memory status
  const mem = document.getElementById('status-memory');
  if (mem) mem.textContent = `${state.alerts.length} events indexed`;
}

// ─── Status Last Poll Clock ─────────────────────────────────────────────────
function startStatusClock() {
  const el = document.getElementById('status-last-poll');
  let seconds = 0;
  setInterval(() => {
    seconds++;
    if (seconds < 60) el.textContent = `${seconds}s ago`;
    else if (seconds < 3600) el.textContent = `${Math.floor(seconds/60)}m ago`;
    else el.textContent = 'Polling...';
  }, 1000);
}

// ─── Animated Stat Counters ─────────────────────────────────────────────────
function animateCounters() {
  document.querySelectorAll('[data-target]').forEach(el => {
    const target = parseInt(el.dataset.target);
    const duration = 1800;
    const step = 16;
    const increment = target / (duration / step);
    let current = 0;

    const timer = setInterval(() => {
      current = Math.min(current + increment, target);
      el.textContent = Math.round(current).toLocaleString();
      if (current >= target) clearInterval(timer);
    }, step);
  });
}

// ─── Hero Particles ─────────────────────────────────────────────────────────
function createParticles() {
  const container = document.getElementById('hero-particles');
  if (!container) return;

  const colors = ['#f43f5e', '#f59e0b', '#10b981', '#6366f1'];
  for (let i = 0; i < 35; i++) {
    const p = document.createElement('div');
    p.className = 'particle';
    const size = 2 + Math.random() * 5;
    p.style.cssText = `
      width: ${size}px; height: ${size}px;
      left: ${Math.random() * 100}%;
      top: ${20 + Math.random() * 80}%;
      background: ${colors[Math.floor(Math.random() * colors.length)]};
      animation-duration: ${8 + Math.random() * 12}s;
      animation-delay: ${Math.random() * 8}s;
      filter: blur(${Math.random() > 0.7 ? 1 : 0}px);
    `;
    container.appendChild(p);
  }
}

// ─── Navbar scroll effect ───────────────────────────────────────────────────
function initNavbarScroll() {
  window.addEventListener('scroll', () => {
    const navbar = document.getElementById('navbar');
    if (window.scrollY > 60) {
      navbar.style.borderBottomColor = 'var(--border-medium)';
    } else {
      navbar.style.borderBottomColor = 'var(--border-subtle)';
    }
  }, { passive: true });
}

// ─── Intersection Observer for counter animation ────────────────────────────
function initCounterObserver() {
  const statsEl = document.querySelector('.hero-stats');
  if (!statsEl) return;

  const obs = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        animateCounters();
        obs.disconnect();
      }
    });
  }, { threshold: 0.5 });

  obs.observe(statsEl);
}

// ─── Intersection Observer for reveal animations ────────────────────────────
function initRevealObserver() {
  const reveals = document.querySelectorAll('.reveal');
  if (!reveals.length) return;

  const obs = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('active');
        obs.unobserve(entry.target);
      }
    });
  }, { threshold: 0.15, rootMargin: '0px 0px -50px 0px' });

  reveals.forEach(el => obs.observe(el));
}

// ─── Toast notifications ────────────────────────────────────────────────────
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => { toast.style.opacity = '0'; toast.style.transition = 'opacity 0.3s'; }, 2500);
  setTimeout(() => toast.remove(), 2900);
}

// ─── Utilities ──────────────────────────────────────────────────────────────
function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function formatTimeAgo(date) {
  const diff = (Date.now() - date) / 1000;
  if (diff < 60) return `${Math.round(diff)}s ago`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  return date.toLocaleDateString();
}


// ─── Initialize App ─────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  // Set initial body mode class
  document.body.classList.add('mode-eco');

  createParticles();
  initNavbarScroll();
  initCounterObserver();
  initRevealObserver();
  startStatusClock();
  updateMiniStats();
  loadThreatCounts();   // Populate pillar cards with real threat data
  loadConvergence();    // 🧠 Neural Moat

  // Start recurring polling
  setInterval(pollSystemStatus, 2000);
  setInterval(() => loadAlerts(state.activeMode), 15000);
  setInterval(loadThreatCounts, 10000);
  setInterval(loadConvergence, 8000);  // 🧠 Poll convergence every 8s

  // Init Infographics
  initCharts();
});

// ─── 🧠 Neural Moat — Convergence Fetcher ────────────────────────────────────
async function loadConvergence() {
  try {
    const resp = await fetch(`${API_BASE}/convergence`);
    if (!resp.ok) return;
    const data = await resp.json();

    // Update stats
    const totalEl = document.getElementById('moat-total');
    const vectorsEl = document.getElementById('moat-vectors');
    if (totalEl) totalEl.textContent = data.total || 0;
    if (vectorsEl) vectorsEl.textContent = data.memory_vectors || 0;

    // Update SVG link map
    updateMoatGraph(data.mode_links || {});

    // Render convergence alerts
    renderMoatAlerts(data.convergence_alerts || []);
  } catch (e) {
    console.warn('[NeuralMoat] Convergence fetch error:', e);
  }
}

function updateMoatGraph(links) {
  const linkPairs = {
    'epi-eco':     { lineId: 'link-epi-eco',     badgeId: 'badge-epi-eco',     textId: 'badge-epi-eco-text' },
    'eco-supply':  { lineId: 'link-eco-supply',   badgeId: 'badge-eco-supply',  textId: 'badge-eco-supply-text' },
    'epi-supply':  { lineId: 'link-epi-supply',   badgeId: 'badge-epi-supply',  textId: 'badge-epi-supply-text' },
  };

  for (const [key, ids] of Object.entries(linkPairs)) {
    const count = links[key] || 0;
    const line = document.getElementById(ids.lineId);
    const badge = document.getElementById(ids.badgeId);
    const text = document.getElementById(ids.textId);

    if (count > 0) {
      line?.classList.add('active');
      if (badge) badge.style.display = '';
      if (text) text.textContent = count;
    } else {
      line?.classList.remove('active');
      if (badge) badge.style.display = 'none';
    }
  }
}

function renderMoatAlerts(alerts) {
  const container = document.getElementById('moat-alerts-list');
  if (!container) return;

  if (!alerts.length) {
    container.innerHTML = `
      <div class="moat-empty">
        <span class="moat-empty-icon">🔍</span>
        <span>Scanning for cross-mode patterns...</span>
      </div>`;
    return;
  }

  container.innerHTML = alerts.map(a => {
    const warning = escapeHtml(a.convergence_warning || '').substring(0, 200);
    const headline = escapeHtml(a.headline || '').substring(0, 100);
    const mode = a.mode || 'eco';
    const sevDots = Array.from({length: 5}, (_, i) =>
      `<span style="display:inline-block;width:6px;height:6px;border-radius:50%;margin-right:2px;background:${i < (a.severity||3) ? '#6366f1' : 'var(--border-medium)'}"></span>`
    ).join('');

    return `
      <div class="moat-alert-item">
        <div class="moat-alert-headline">${headline}</div>
        <div class="moat-alert-warning">${warning}</div>
        <div class="moat-alert-meta">
          <span class="moat-alert-badge badge-${mode}">${mode.toUpperCase()}</span>
          <span class="moat-alert-badge badge-convergence">🧠 CONVERGENCE</span>
          ${sevDots}
        </div>
      </div>`;
  }).join('');
}


// ─── Threat Counts & Consequences for Pillar Cards ──────────────────────────
async function loadThreatCounts() {
  try {
    // Fetch total counts
    const countsResp = await fetch(`${API_BASE}/threat-counts`);
    const counts = await countsResp.json();

    for (const mode of ['epi', 'eco', 'supply']) {
      const el = document.getElementById(`${mode}-threat-count`);
      if (el && counts[mode]) {
        el.textContent = counts[mode].total;
      }
    }

    // Fetch top headlines for each mode as "consequences"
    for (const mode of ['epi', 'eco', 'supply']) {
      const listEl = document.getElementById(`${mode}-consequences-list`);
      if (!listEl) continue;

      try {
        const feedResp = await fetch(`${API_BASE}/feed/${mode}?page=1&per_page=20`);
        const feedData = await feedResp.json();
        const items = feedData.headlines || feedData.items || [];

        if (items.length === 0) {
          listEl.innerHTML = '<li style="opacity:0.5">Scanning feeds...</li>';
          continue;
        }

        // Duplicate items for infinite scroll effect
        const displayItems = [...items, ...items];
        listEl.innerHTML = displayItems
          .map(item => `<li>${escapeHtml(item.headline || item.title || '')}</li>`)
          .join('');
      } catch (e) {
        console.warn(`[Ticker] Failed to load ${mode} feed`, e);
      }
    }
  } catch (e) {
    console.warn('[ThreatCounts] API error', e);
  }
}
  
  // ─── Chart.js Infographics ────────────────────────────────────────────────
  let charts = {};
  
  function initCharts() {
    if (typeof Chart === 'undefined') return;
  
    Chart.defaults.color = '#86868b';
    Chart.defaults.font.family = "'Inter', system-ui, sans-serif";
  
    const ctxEpi = document.getElementById('chartEpi');
    const ctxEco = document.getElementById('chartEco');
    const ctxSupply = document.getElementById('chartSupply');
  
    if (ctxEpi) {
      charts.epi = new Chart(ctxEpi, {
        type: 'line',
        data: {
          labels: ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5', 'Day 6', 'Day 7'],
          datasets: [{
            label: 'Estimated Cases',
            data: [12, 19, 35, 76, 150, 240, 410],
            borderColor: '#f43f5e',
            backgroundColor: 'rgba(244,63,94,0.1)',
            borderWidth: 3,
            fill: true,
            tension: 0.4,
            pointBackgroundColor: '#f43f5e'
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            y: { grid: { color: 'rgba(0,0,0,0.05)' } },
            x: { grid: { display: false } }
          }
        }
      });
    }
  
    if (ctxEco) {
      charts.eco = new Chart(ctxEco, {
        type: 'bar',
        data: {
          labels: ['S. America', 'S. Europe', 'W. USA', 'SE Asia', 'E. Africa'],
          datasets: [{
            label: 'Disaster Risk Index',
            data: [7.2, 8.5, 9.1, 6.4, 7.8],
            backgroundColor: 'rgba(245,158,11,0.8)',
            borderRadius: 6
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            y: { grid: { color: 'rgba(0,0,0,0.05)' }, max: 10 },
            x: { grid: { display: false } }
          }
        }
      });
    }
  
    if (ctxSupply) {
      charts.supply = new Chart(ctxSupply, {
        type: 'doughnut',
        data: {
          labels: ['Logistics', 'Raw Materials', 'Labor Shortage', 'Energy Costs'],
          datasets: [{
            data: [35, 25, 20, 20],
            backgroundColor: ['#10b981', '#34d399', '#6ee7b7', '#a7f3d0'],
            borderWidth: 0,
            hoverOffset: 4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          cutout: '65%',
          plugins: {
            legend: { position: 'right' }
          }
        }
      });
    }
  }
