/* ═══════════════════════════════════════════════════════════════════════
   GlobalSentry — JavaScript Application
   Handles: mode switching, alert feed, pipeline demo, modal, API calls
═══════════════════════════════════════════════════════════════════════ */

// ─── Configuration ──────────────────────────────────────────────────────────
const API_BASE = 'http://localhost:8000/api';
const USE_API  = true; // FastAPI is running at localhost:8000 with /api/ prefix

// ─── Mock Alert Data (used when API is offline) ─────────────────────────────
const MOCK_ALERTS = {
  epi: [
    {
      id: 'epi-1',
      headline: 'Unusual pneumonia cluster detected in Southeast Asia — WHO investigating',
      mode: 'epi', severity: 4, confidence: 0.87, is_verified: true,
      source: 'WHO Situation Report',
      timestamp: new Date(Date.now() - 12 * 60000).toISOString(),
      analysis: 'Pattern consistent with novel respiratory pathogen. Hospitalization rate 3× baseline. Immediate surveillance escalation recommended. Cross-border air travel vectors identified.',
      convergence_warning: null,
    },
    {
      id: 'epi-2',
      headline: 'New drug-resistant TB strain reported across 5 countries',
      mode: 'epi', severity: 3, confidence: 0.79, is_verified: true,
      source: 'ProMED-mail',
      timestamp: new Date(Date.now() - 64 * 60000).toISOString(),
      analysis: 'MDR-TB genotype confirmed via laboratory sequencing. Cross-border travel patterns suggest rapid spread vector through Central Asia corridor.',
      convergence_warning: '⚡ ECO-LINK: Flood displacement camps in the same region may accelerate exposure rates.',
    },
    {
      id: 'epi-3',
      headline: 'Dengue fever outbreaks spike in South America — 40% above seasonal average',
      mode: 'epi', severity: 2, confidence: 0.92, is_verified: true,
      source: 'PAHO/WHO',
      timestamp: new Date(Date.now() - 180 * 60000).toISOString(),
      analysis: 'Vector proliferation linked to increased standing water from irregular rainfall. Urban centers at highest risk. Aedes aegypti density 40% above seasonal baseline.',
      convergence_warning: null,
    },
    {
      id: 'epi-4',
      headline: 'Unconfirmed viral hemorrhagic fever reports emerging from Central Africa',
      mode: 'epi', severity: 5, confidence: 0.61, is_verified: false,
      source: 'Social Media Signals',
      timestamp: new Date(Date.now() - 38 * 60000).toISOString(),
      analysis: 'Awaiting WHO ground-truth confirmation. Symptom pattern matches VHF profile. UNVERIFIED — monitor closely. Local health ministry denial on record.',
      convergence_warning: null,
    },
  ],
  eco: [
    {
      id: 'eco-1',
      headline: 'Magnitude 6.8 earthquake strikes coastal Chile — tsunami advisory issued',
      mode: 'eco', severity: 5, confidence: 0.97, is_verified: true,
      source: 'USGS / NOAA',
      timestamp: new Date(Date.now() - 5 * 60000).toISOString(),
      analysis: 'Shallow-focus quake (depth 18km) maximizes surface impact. Coastal evacuation zones active. Aftershocks expected within 72 hours. Tsunami wave 0.5m detected at Juan Fernández.',
      convergence_warning: '⚡ SUPPLY-LINK: Valparaíso port — major copper export hub — may face operational shutdown for 2–5 days.',
    },
    {
      id: 'eco-2',
      headline: 'Category 4 cyclone forming in Bay of Bengal — landfall predicted in 72hrs',
      mode: 'eco', severity: 4, confidence: 0.89, is_verified: true,
      source: 'IMD Cyclone Warning',
      timestamp: new Date(Date.now() - 120 * 60000).toISOString(),
      analysis: 'Track models show 85% probability of Odisha/Andhra landfall. Storm surge 3–5m above normal tide. 12M population in direct impact corridor. Evacuation orders issued for 6 coastal districts.',
      convergence_warning: null,
    },
    {
      id: 'eco-3',
      headline: 'Mega-drought declaration issued for Western United States — 23-year low',
      mode: 'eco', severity: 3, confidence: 0.95, is_verified: true,
      source: 'US Bureau of Reclamation',
      timestamp: new Date(Date.now() - 300 * 60000).toISOString(),
      analysis: 'Lake Mead at 27% capacity. Hydroelectric output cut 40%. Agricultural water allocation suspended in 3 states. $8.7B economic impact projected for Q3.',
      convergence_warning: '⚡ EPI-LINK: Water scarcity increasing vector-borne disease risk in urban centers across Nevada and Arizona.',
    },
    {
      id: 'eco-4',
      headline: 'Wildfire season begins 6 weeks early in Southern Europe — red alert issued',
      mode: 'eco', severity: 3, confidence: 0.83, is_verified: true,
      source: 'Copernicus EFFIS',
      timestamp: new Date(Date.now() - 480 * 60000).toISOString(),
      analysis: 'Unprecedented heat-drought combination. Fire weather index at extreme level across Portugal, Spain, Greece. 14,000 ha burned in first 48 hours of season.',
      convergence_warning: null,
    },
  ],
  supply: [
    {
      id: 'supply-1',
      headline: 'Major TSMC fab halts production — global chip shortage feared',
      mode: 'supply', severity: 5, confidence: 0.91, is_verified: true,
      source: 'Reuters / SEC Filing',
      timestamp: new Date(Date.now() - 22 * 60000).toISOString(),
      analysis: 'Whistleblower report filed with SEC. 3nm fab line offline for minimum 2 weeks. Apple, NVIDIA, AMD tier-1 exposure confirmed. Q4 product launches at risk.',
      convergence_warning: '⚡ ECO-LINK: Earthquake near Hsinchu triggered facility shutdown — compound convergence event confirmed.',
    },
    {
      id: 'supply-2',
      headline: 'Red Sea shipping lane disruption continues — Suez diversions spike 340%',
      mode: 'supply', severity: 4, confidence: 0.96, is_verified: true,
      source: 'Freightos Baltic Index',
      timestamp: new Date(Date.now() - 60 * 60000).toISOString(),
      analysis: 'Container shipping rates at 18-month high. Europe-Asia freight +22 days transit time. Energy, electronics, automotive sectors in critical impact zone. Daily loss estimate $12M.',
      convergence_warning: null,
    },
    {
      id: 'supply-3',
      headline: 'Rare earth mining ban declared in Myanmar — EV battery chain at risk',
      mode: 'supply', severity: 3, confidence: 0.78, is_verified: true,
      source: 'Bloomberg Supply Chain Monitor',
      timestamp: new Date(Date.now() - 240 * 60000).toISOString(),
      analysis: 'Myanmar supplies 40% global rare earth output. Tesla, BYD, Volkswagen flagged in risk registry. 6-month buffer supply estimated before critical shortfall.',
      convergence_warning: null,
    },
    {
      id: 'supply-4',
      headline: 'Anonymous ESG whistleblower alleges forced labor in smartphone supply chain',
      mode: 'supply', severity: 2, confidence: 0.58, is_verified: false,
      source: 'Whistleblower Platform',
      timestamp: new Date(Date.now() - 360 * 60000).toISOString(),
      analysis: 'Report under third-party audit review. Social compliance violations alleged at Tier-2 supplier in Shenzhen industrial zone. UNVERIFIED — pending independent investigation and corroboration.',
      convergence_warning: null,
    },
  ],
};

// ─── Application State ──────────────────────────────────────────────────────
const state = {
  activeMode: 'eco',
  triggeredAlerts: [],
  isRunningPipeline: false,
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
      const resp = await fetch(`${API_BASE}/alerts?mode=${mode}&limit=10`);
      const data = await resp.json();
      alerts = data.alerts || [];
    } catch {
      alerts = getLocalAlerts(mode);
    }
  } else {
    alerts = getLocalAlerts(mode);
  }

  renderAlerts(alerts);
  checkConvergence(alerts);
  updateMiniStats();
}

function getLocalAlerts(mode) {
  const triggered = state.triggeredAlerts.filter(a => a.mode === mode);
  return [...triggered, ...MOCK_ALERTS[mode]];
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
  card.className = `alert-card mode-${alert.mode} sev-${alert.severity} entering`;
  card.style.animationDelay = `${index * 60}ms`;
  card.setAttribute('data-alert-id', alert.id);

  const sevDots = buildSeverityDots(alert.severity, alert.mode);
  const modeBadgeClass = `badge-${alert.mode}`;
  const vBadgeClass = alert.is_verified ? 'badge-verified' : 'badge-unverified';
  const vText = alert.is_verified ? '✓ Verified' : '⚠ Unverified';
  const timeAgo = formatTimeAgo(new Date(alert.timestamp));

  card.innerHTML = `
    <div class="alert-card-top">
      <div class="alert-headline">${escapeHtml(alert.headline)}</div>
      <div class="alert-badges">
        <span class="badge ${modeBadgeClass}">${alert.mode.toUpperCase()}</span>
        <span class="badge ${vBadgeClass}">${vText}</span>
      </div>
    </div>
    <div class="alert-card-bottom">
      <div class="alert-meta">
        <div class="alert-severity">${sevDots}</div>
        <span class="alert-source">${escapeHtml(alert.source)}</span>
        <span class="alert-time">${timeAgo}</span>
      </div>
      <button class="alert-view-btn" id="btn-view-details-${alert.id}" onclick="openAlertModal('${alert.id}')">
        View Details →
      </button>
    </div>
    ${alert.convergence_warning ? `<div style="margin-top:10px;font-size:0.78rem;color:var(--eco);border-top:1px solid rgba(245,158,11,0.2);padding-top:8px;">${escapeHtml(alert.convergence_warning)}</div>` : ''}
  `;

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

// ─── Trigger Analysis ───────────────────────────────────────────────────────
async function triggerAnalysis() {
  const input  = document.getElementById('trigger-input');
  const status = document.getElementById('trigger-status');
  const btn    = document.getElementById('btn-trigger-analysis');

  const headline = input.value.trim();
  if (!headline) {
    showToast('Please enter a headline to analyze', 'error');
    input.focus();
    return;
  }

  btn.disabled = true;
  btn.textContent = '⏳ Analyzing...';
  status.style.display = 'block';
  status.className = 'trigger-status running';
  status.textContent = '🔄 Running pipeline nodes...';

  // Animate pipeline
  await animatePipelineNodes();

  let newAlert;
  if (USE_API) {
    try {
      const resp = await fetch(`${API_BASE}/trigger`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ headline, mode: state.activeMode }),
      });
      const data = await resp.json();
      newAlert = data.alert || buildMockTriggerAlert(headline);
    } catch {
      newAlert = buildMockTriggerAlert(headline);
    }
  } else {
    await sleep(2200);
    newAlert = buildMockTriggerAlert(headline);
  }

  state.triggeredAlerts.unshift(newAlert);

  status.className = 'trigger-status success';
  status.innerHTML = `✅ Analysis complete — Severity ${newAlert.severity}/5 | Confidence ${Math.round(newAlert.confidence * 100)}% | ${newAlert.is_verified ? '✓ Verified' : '⚠ Unverified'}`;

  btn.disabled = false;
  btn.textContent = '⚡ Trigger Analysis';

  // Prepend to feed
  const container = document.getElementById('alerts-container');
  container.querySelectorAll('.alert-loading').forEach(el => el.remove());
  const card = buildAlertCard(newAlert, 0);
  card.style.animationDelay = '0ms';
  container.prepend(card);

  if (newAlert.convergence_warning) {
    document.getElementById('convergence-text').textContent = newAlert.convergence_warning;
    document.getElementById('convergence-panel').style.display = 'flex';
  }

  showToast(`Analysis complete: Severity ${newAlert.severity}/5`, 'success');
  updateMiniStats();
}

function buildMockTriggerAlert(headline) {
  const severity = Math.floor(Math.random() * 3) + 2;
  const confidence = parseFloat((Math.random() * 0.3 + 0.65).toFixed(2));
  const analyses = {
    epi: `Epidemiological triage complete. Symptom pattern cross-matched with ${3 + Math.floor(Math.random() * 9)} historical outbreaks in Qdrant memory. R0 estimation initiated.`,
    eco: `Geophysical risk model applied. Satellite data cross-referenced. Affected population zone estimated at ${50 + Math.floor(Math.random() * 450)}K residents.`,
    supply: `Supply chain dependency graph queried. ${2 + Math.floor(Math.random() * 7)} Tier-1 suppliers identified in impact zone. ESG registry cross-checked.`,
  };
  return {
    id: `triggered-${Date.now()}`,
    headline,
    mode: state.activeMode,
    severity,
    confidence,
    is_verified: confidence > 0.75,
    source: 'Live Demo — Manual Trigger',
    timestamp: new Date().toISOString(),
    analysis: analyses[state.activeMode],
    convergence_warning: Math.random() > 0.55 ? '⚡ CONVERGENCE: Cross-mode pattern match detected in Qdrant memory.' : null,
  };
}

// ─── Pipeline Visualizer ────────────────────────────────────────────────────
const PIPELINE_STEPS = [
  { id: 'pnode-ingest',    label: 'Ingest & Profiler', msRange: [120, 280] },
  { id: 'pnode-retriever', label: 'Retriever (RAG)',   msRange: [200, 600] },
  { id: 'pnode-triage',    label: 'Agent A — Triage',  msRange: [80, 200] },
  { id: 'pnode-analyst',   label: 'Agent B — Analyst', msRange: [400, 1200] },
  { id: 'pnode-validator', label: 'Agent C — Validator', msRange: [300, 800] },
  { id: 'pnode-notify',    label: 'Notify',            msRange: [50, 150] },
  { id: 'pnode-archive',   label: 'Archive',           msRange: [50, 150] },
];

async function runPipelineDemo() {
  if (state.isRunningPipeline) return;
  state.isRunningPipeline = true;

  const btn = document.getElementById('btn-run-pipeline');
  const progress = document.getElementById('pipeline-progress');
  const bar = document.getElementById('pipeline-progress-bar');
  btn.disabled = true;
  btn.textContent = '⏳ Running...';
  progress.style.display = 'block';

  // Reset all nodes
  PIPELINE_STEPS.forEach((step, i) => {
    const node = document.getElementById(step.id);
    if (node) { node.classList.remove('active', 'done'); }
    const timeEl = document.getElementById(`ptime-${i}`);
    if (timeEl) timeEl.textContent = '';
  });

  for (let i = 0; i < PIPELINE_STEPS.length; i++) {
    const step = PIPELINE_STEPS[i];
    const node = document.getElementById(step.id);
    const timeEl = document.getElementById(`ptime-${i}`);

    if (node) { node.classList.add('active'); node.scrollIntoView({ behavior: 'smooth', block: 'nearest' }); }

    const ms = step.msRange[0] + Math.random() * (step.msRange[1] - step.msRange[0]);
    await sleep(ms);

    if (node) { node.classList.remove('active'); node.classList.add('done'); }
    if (timeEl) timeEl.textContent = `${Math.round(ms)}ms ✓`;

    bar.style.width = `${((i + 1) / PIPELINE_STEPS.length) * 100}%`;
  }

  btn.disabled = false;
  btn.textContent = '▶ Run Pipeline Demo';
  progress.style.display = 'none';
  bar.style.width = '0%';
  state.isRunningPipeline = false;

  showToast('Pipeline demo complete!', 'success');

  // Reset nodes after 3s
  setTimeout(() => {
    PIPELINE_STEPS.forEach(step => {
      const node = document.getElementById(step.id);
      if (node) node.classList.remove('done');
    });
  }, 3000);
}

async function animatePipelineNodes() {
  // Scroll to pipeline and run it
  const pSection = document.getElementById('pipeline');
  if (pSection) pSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
  await sleep(500);
  await runPipelineDemo();
  document.getElementById('dashboard').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ─── Alert Modal ────────────────────────────────────────────────────────────
function openAlertModal(alertId) {
  // Find alert in all data
  let alert = null;
  for (const mode of ['epi', 'eco', 'supply']) {
    alert = MOCK_ALERTS[mode].find(a => a.id === alertId);
    if (alert) break;
  }
  if (!alert) {
    alert = state.triggeredAlerts.find(a => a.id === alertId);
  }
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
  const epiCount    = MOCK_ALERTS.epi.length + state.triggeredAlerts.filter(a => a.mode === 'epi').length;
  const ecoCount    = MOCK_ALERTS.eco.length + state.triggeredAlerts.filter(a => a.mode === 'eco').length;
  const supplyCount = MOCK_ALERTS.supply.length + state.triggeredAlerts.filter(a => a.mode === 'supply').length;

  const e = document.getElementById('mini-epi');
  const c = document.getElementById('mini-eco');
  const s = document.getElementById('mini-supply');
  if (e) e.textContent = epiCount;
  if (c) c.textContent = ecoCount;
  if (s) s.textContent = supplyCount;

  // Update memory status
  const mem = document.getElementById('status-memory');
  if (mem) mem.textContent = `${epiCount + ecoCount + supplyCount} events indexed`;
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
  startStatusClock();
  updateMiniStats();

  // Load initial alert feed (eco is default)
  loadAlerts('eco');

  // Demo hint in trigger input
  const demoHints = {
    epi: 'New respiratory illness cluster confirmed in Southeast Asia — WHO monitoring',
    eco: 'Magnitude 7.1 earthquake strikes coastal Peru — tsunami watch issued',
    supply: 'Major semiconductor factory shutting down amid ESG audit — chip shortage feared',
  };

  // Rotate placeholder hints every 5s
  let hintIndex = 0;
  const hintModes = ['epi', 'eco', 'supply'];
  const triggerInput = document.getElementById('trigger-input');
  if (triggerInput) {
    setInterval(() => {
      hintIndex = (hintIndex + 1) % 3;
      triggerInput.placeholder = demoHints[hintModes[hintIndex]];
    }, 5000);
  }
});
