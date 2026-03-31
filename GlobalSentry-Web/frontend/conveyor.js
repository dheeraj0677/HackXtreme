// Add helper to manage set sizes to prevent memory leaks
function addToSetLimited(set, item, maxSize = 1000) {
    set.add(item);
    if (set.size > maxSize) {
        set.delete(set.values().next().value);
    }
}

let seenPolled = new Set();
let seenAccepted = new Set();
let seenRejected = new Set();

function createCard(item, type) {
    const div = document.createElement('div');
    // Ensure mode has a fallback safely
    const modeClass = item.mode ? item.mode : 'general';
    div.className = `belt-card ${modeClass} card-${type}`;
    
    const sourceLabel = item.source ? item.source : (item.mode ? item.mode.toUpperCase() + '-SENTRY' : 'RSS');
    const timeLabel = new Date(item.timestamp || Date.now()).toLocaleTimeString();
    
    div.innerHTML = `
        <div class="belt-headline"></div>
        <div class="belt-meta">
            <span class="source-span"></span>
            <span class="time-span"></span>
        </div>
    `;
    div.querySelector('.belt-headline').textContent = item.headline;
    div.querySelector('.source-span').textContent = sourceLabel;
    div.querySelector('.time-span').textContent = timeLabel;
    
    return div;
}

// ─── Pipeline Node Highlighting ──────────────────────────────────────────────
const PIPELINE_NODES = ['profiler', 'triage', 'retriever', 'analyst', 'correlator', 'validator', 'retry', 'notify', 'archiver'];
const NODE_IDS = {
    'profiler': 'pnode-profiler',
    'triage': 'pnode-triage',
    'retriever': 'pnode-retriever',
    'analyst': 'pnode-analyst',
    'correlator': 'pnode-correlator',
    'validator': 'pnode-validator',
    'retry': 'pnode-reflect',
    'retry_counter': 'pnode-reflect',
    'notify': 'pnode-notify',
    'archiver': 'pnode-archive'
};
const NODE_LABELS = {
    'profiler': 'Profiler',
    'triage': 'Triage (Agent A)',
    'retriever': 'Retriever (RAG)',
    'analyst': 'Analyst (Agent B)',
    'correlator': 'Correlator (Neural Moat)',
    'validator': 'Validator (Agent C)',
    'retry': 'Reflection Loop',
    'retry_counter': 'Reflection Loop',
    'notify': 'Notify',
    'archiver': 'Archiver'
};

function updatePipelineViz(currentAnalysis) {
    const statusText = document.getElementById('pipeline-status-text');
    const headlineEl = document.getElementById('pipeline-headline');
    const trackerPill = document.getElementById('data-tracker-pill');

    // Reset all pipeline nodes
    document.querySelectorAll('.pipeline-node').forEach(n => {
        n.classList.remove('active', 'done');
    });

    if (!currentAnalysis) {
        if (statusText) statusText.textContent = 'Waiting for next signal...';
        if (headlineEl) headlineEl.textContent = '';
        if (trackerPill) trackerPill.style.opacity = '0';
        return;
    }

    const activeNode = currentAnalysis.active_node;
    const activeLabel = NODE_LABELS[activeNode] || activeNode;
    const modeLabel = currentAnalysis.mode ? currentAnalysis.mode.toUpperCase() : '?';

    if (statusText) statusText.textContent = `⚡ ${activeLabel} — [${modeLabel}]`;
    if (headlineEl) headlineEl.textContent = currentAnalysis.headline;

    // Highlight pipeline nodes: done → active → pending
    const currentID = NODE_IDS[activeNode];
    let isDonePhase = true;

    PIPELINE_NODES.forEach(n => {
        const elId = NODE_IDS[n];
        if (!elId) return;
        const el = document.getElementById(elId);
        if (!el) return;

        if (elId === currentID) {
            el.classList.add('active');
            isDonePhase = false;

            // Position tracker pill over active node
            if (trackerPill) {
                trackerPill.textContent = currentAnalysis.headline;
                trackerPill.style.opacity = '1';
                const containerEl = document.getElementById('pipeline-nodes');
                const containerRect = containerEl.getBoundingClientRect();
                const nodeRect = el.getBoundingClientRect();
                const leftPos = (nodeRect.left - containerRect.left) + (nodeRect.width / 2);
                trackerPill.style.transform = `translateX(${leftPos}px) translateX(-50%)`;
            }
        } else if (isDonePhase) {
            el.classList.add('done');
        }
    });
}

// ─── Fetch status from API ───────────────────────────────────────────────────
async function pollStatus() {
    try {
        const res = await fetch('http://localhost:8000/api/status');
        if (!res.ok) return;
        const data = await res.json();
        
        // 1. Update Pipeline Visualization
        updatePipelineViz(data.current_analysis);
        
        // 2. Update Active Analysis Card
        const activeContainer = document.getElementById('list-active');
        if (data.current_analysis) {
            if (activeContainer.dataset.activeId !== data.current_analysis.headline) {
                activeContainer.innerHTML = '';
                const card = createCard(data.current_analysis, 'active');
                card.style.transform = 'scale(1.02)';
                card.style.boxShadow = '0 0 15px rgba(56, 189, 248, 0.4)';
                const nodeDiv = document.createElement('div');
                nodeDiv.style.cssText = "margin-top: 10px; font-size: 11px; color:#38bdf8; text-transform:uppercase; font-weight:bold;";
                nodeDiv.textContent = `⚡ Evaluating via ${data.current_analysis.active_node}...`;
                card.appendChild(nodeDiv);
                activeContainer.appendChild(card);
                activeContainer.dataset.activeId = data.current_analysis.headline;
            } else {
                 const nodeText = activeContainer.querySelector('div:last-child');
                 if (nodeText && data.current_analysis.active_node) {
                     nodeText.textContent = `⚡ Evaluating via ${data.current_analysis.active_node}...`;
                 }
            }
        } else {
            if (activeContainer.innerHTML.indexOf('empty-state') === -1) {
                activeContainer.innerHTML = '<div class="empty-state">Waiting for next scan cycle...</div>';
                delete activeContainer.dataset.activeId;
            }
        }

        // 3. Rejected
        const rejectedContainer = document.getElementById('list-rejected');
        if (data.recent_rejections) {
            data.recent_rejections.reverse().forEach(rej => {
                const h = rej.headline;
                if (!seenRejected.has(h)) {
                    addToSetLimited(seenRejected, h);
                    const card = createCard(rej, 'rejected');
                    rejectedContainer.prepend(card);
                    card.addEventListener('animationend', () => card.remove());
                }
            });
            document.getElementById('count-rejected').innerText = seenRejected.size;
        }
    } catch(e) {
        console.error("Conveyor Status Fetch Error:", e);
    }
}

async function fetchAccepted() {
    try {
        const res = await fetch('http://localhost:8000/api/alerts?limit=50');
        if (!res.ok) return;
        const data = await res.json();
        const container = document.getElementById('list-accepted');
        
        // Only show agent-processed alerts — NOT raw RSS feeds
        const agentAlerts = data.alerts.filter(a => a.is_raw_feed !== true);
        
        [...agentAlerts].reverse().forEach(alert => {
            const h = alert.headline;
            if (!seenAccepted.has(h)) {
                addToSetLimited(seenAccepted, h);
                const card = createCard(alert, 'accepted');
                container.prepend(card);
                
                if (container.children.length > 30) {
                    container.removeChild(container.lastChild);
                }
            }
        });
        document.getElementById('count-accepted').innerText = seenAccepted.size;
    } catch(e) {
        console.error("Conveyor Alerts Error:", e);
    }
}

async function fetchPolledInputs() {
    try {
        const modes = ['epi', 'eco', 'supply'];
        
        const fetchPromises = modes.map(m => fetch(`http://localhost:8000/api/feed/${m}?limit=50`).then(res => res.ok ? res.json() : null));
        const results = await Promise.all(fetchPromises);
        
        let allFeeds = [];
        results.forEach(data => {
            if (data && data.headlines) {
                allFeeds = allFeeds.concat(data.headlines);
            }
        });
        
        allFeeds.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
        
        const container = document.getElementById('list-polled');
        allFeeds.reverse().forEach(item => {
            const h = item.headline;
            if (!seenPolled.has(h)) {
                addToSetLimited(seenPolled, h);
                const card = createCard(item, 'polled');
                container.prepend(card);
                
                if (container.children.length > 100) {
                    container.removeChild(container.lastChild);
                }
            }
        });
        
        document.getElementById('count-polled').innerText = document.getElementById('list-polled').children.length;
    } catch(e) {
        console.error("Conveyor Feeds Error:", e);
    }
}

setInterval(pollStatus, 1000);
setInterval(fetchAccepted, 3000);
setInterval(fetchPolledInputs, 15000);

// Initial Load
fetchPolledInputs();
fetchAccepted();
pollStatus();
