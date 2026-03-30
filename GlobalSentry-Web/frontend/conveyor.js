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

// Fetch status from API
async function pollStatus() {
    try {
        const res = await fetch('http://localhost:8000/api/status');
        if (!res.ok) return;
        const data = await res.json();
        
        // 1. Update Active Analysis
        const activeContainer = document.getElementById('list-active');
        if (data.current_analysis) {
            // Check if we are already showing it to prevent re-rendering and losing animation
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
                 // Update the active node text without re-rendering the whole card
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

        // 2. Rejected
        const rejectedContainer = document.getElementById('list-rejected');
        if (data.recent_rejections) {
            // Keep track of things we just added so we don't duplicate
            data.recent_rejections.reverse().forEach(rej => {
                const h = rej.headline;
                if (!seenRejected.has(h)) {
                    addToSetLimited(seenRejected, h);
                    const card = createCard(rej, 'rejected');
                    rejectedContainer.prepend(card);
                    // Remove DOM element after CSS animation finishes
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
        const res = await fetch('http://localhost:8000/api/alerts?limit=15');
        if (!res.ok) return;
        const data = await res.json();
        const container = document.getElementById('list-accepted');
        
        // Iterate backwards to prepend older ones first if they are new to the UI
        [...data.alerts].reverse().forEach(alert => {
            const h = alert.headline;
            if (!seenAccepted.has(h)) {
                addToSetLimited(seenAccepted, h);
                const card = createCard(alert, 'accepted');
                container.prepend(card);
                
                // Keep list from growing infinitely 
                if (container.children.length > 30) {
                    container.removeChild(container.lastChild);
                }
            }
        });
        document.getElementById('count-accepted').innerText = data.total;
    } catch(e) {
        console.error("Conveyor Alerts Error:", e);
    }
}

async function fetchPolledInputs() {
    try {
        const modes = ['epi', 'eco', 'supply'];
        
        // Fetch in parallel
        const fetchPromises = modes.map(m => fetch(`http://localhost:8000/api/feed/${m}?limit=50`).then(res => res.ok ? res.json() : null));
        const results = await Promise.all(fetchPromises);
        
        let allFeeds = [];
        results.forEach(data => {
            if (data && data.headlines) {
                allFeeds = allFeeds.concat(data.headlines);
            }
        });
        
        // Sort newest first
        allFeeds.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
        
        const container = document.getElementById('list-polled');
        // Reverse array to maintain chronological top-prepend order
        allFeeds.reverse().forEach(item => {
            const h = item.headline;
            if (!seenPolled.has(h)) {
                addToSetLimited(seenPolled, h);
                const card = createCard(item, 'polled');
                container.prepend(card);
                
                // Keep list capped
                if (container.children.length > 100) {
                    container.removeChild(container.lastChild);
                }
            }
        });
        
        // Just show current buffer length
        document.getElementById('count-polled').innerText = document.getElementById('list-polled').children.length;
    } catch(e) {
        console.error("Conveyor Feeds Error:", e);
    }
}

setInterval(pollStatus, 1000);
setInterval(fetchAccepted, 3000);
setInterval(fetchPolledInputs, 15000); // Polled inputs don't change often, once every 15s is fine

// Initial Load
fetchPolledInputs();
fetchAccepted();
pollStatus();
