// Analytics Init
const SESSION_KEY = 'citizen_session_id';
let sessionId = localStorage.getItem(SESSION_KEY);
if (!sessionId) {
    sessionId = 'sess_' + Math.random().toString(36).substr(2, 9);
    localStorage.setItem(SESSION_KEY, sessionId);
}

document.addEventListener('DOMContentLoaded', () => {
    fetchReps();
    startHeartbeat();
    trackEvent('page_view', 'home');

    // Initial Chat Message
    addMessage('Hello! I am your Citizen Assistant. I can help you find your MP or understand government schemes.\nSUGGESTIONS: ["Who is the MP of New Delhi?", "How are MPLADS funds used?", "What are my civic rights?"]', 'ai');
});

function startHeartbeat() {
    // Send heartbeat immediately then every 30s
    sendHeartbeat();
    setInterval(sendHeartbeat, 30000);
}

async function sendHeartbeat() {
    try {
        await fetch('/api/analytics/heartbeat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: sessionId })
        });
    } catch (e) { console.error("Tracking Error", e); }
}

async function trackEvent(type, details = "") {
    try {
        await fetch('/api/analytics/event', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: sessionId, event_type: type, details: details })
        });
    } catch (e) { console.error("Tracking Error", e); }
}

async function fetchReps(query = '') {
    const url = query ? `/api/representatives?search=${query}` : '/api/representatives';
    const res = await fetch(url);
    const data = await res.json();
    renderReps(data);
}

/* --- Party Symbols --- */
const partySymbols = {
    'BJP': 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Bharatiya_Janata_Party_logo.svg/240px-Bharatiya_Janata_Party_logo.svg.png',
    'INC': 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/6c/Indian_National_Congress_hand_logo.svg/240px-Indian_National_Congress_hand_logo.svg.png',
    'AAP': 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/Aam_Aadmi_Party_logo_%28English%29.svg/240px-Aam_Aadmi_Party_logo_%28English%29.svg.png',
    'TMC': 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c0/All_India_Trinamool_Congress_symbol.svg/240px-All_India_Trinamool_Congress_symbol.svg.png',
    'DMK': 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/Rising_Sun_Symbol.svg/240px-Rising_Sun_Symbol.svg.png',
    'CPI(M)': 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Cpi_m_logo.svg/240px-Cpi_m_logo.svg.png',
    'SP': 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d2/Bicycle_Symbol.svg/240px-Bicycle_Symbol.svg.png',
    'YSRCP': 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/8f/Ceiling_Fan_Symbol.svg/240px-Ceiling_Fan_Symbol.svg.png'
};

function getPartySymbol(party) {
    if (!party) return '';
    const cleanParty = party.trim();
    if (partySymbols[cleanParty]) {
        return `<img src="${partySymbols[cleanParty]}" alt="${cleanParty}" class="party-symbol" title="${cleanParty}">`;
    }
    for (const key of Object.keys(partySymbols)) {
        if (cleanParty.includes(key)) {
            return `<img src="${partySymbols[key]}" alt="${cleanParty}" class="party-symbol" title="${cleanParty}">`;
        }
    }
    return '';
}

function renderReps(reps) {
    const grid = document.getElementById('repsGrid');
    grid.innerHTML = '';

    if (reps.length === 0) {
        grid.innerHTML = '<p style="color:var(--text-muted);">No representatives found.</p>';
        return;
    }

    reps.forEach(rep => {
        let achievements = [];
        try {
            if (rep.achievements) {
                achievements = JSON.parse(rep.achievements);
            }
        } catch (e) {
            achievements = ["Data unavailable"];
        }

        const card = document.createElement('div');
        card.className = 'card';
        card.onclick = () => openRepModal(rep); // Click to open modal

        card.innerHTML = `
            <div class="card-header">
                <img src="${rep.image_url || 'https://via.placeholder.com/60?text=MP'}" alt="${rep.name}" class="avatar">
                <div class="info">
                    <h3>${rep.name}</h3>
                    <span style="display:flex; align-items:center;">${rep.role} • ${rep.party} ${getPartySymbol(rep.party)}</span>
                </div>
            </div>
            <p style="color:var(--text-muted); font-size: 0.9rem; margin-bottom:1rem;">${rep.constituency}, ${rep.state}</p>
            <p style="font-size: 0.95rem; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">${rep.bio}</p>
            <div class="stats">
                <div class="stat-item">
                    <span class="stat-val">${rep.years_in_office || '-'} Yrs</span>
                    <span class="stat-label">Term</span>
                </div>
                 <div class="stat-item">
                    <span class="stat-val">₹${rep.funds_spent_crores || 0}Cr</span>
                    <span class="stat-label">Spent</span>
                </div>
                 <div class="stat-item">
                    <span class="stat-val">${rep.attendance_percentage || 0}%</span>
                    <span class="stat-label">Attend</span>
                </div>
            </div>
            <div style="margin-top:1rem;">
                <span class="stat-label">Key Achievement:</span>
                <p style="font-size:0.9rem;">✨ ${achievements[0] || 'N/A'}</p>
            </div>
        `;
        grid.appendChild(card);
    });
}

/* --- Modal Logic --- */
function openRepModal(rep) {
    const modal = document.getElementById('repModal');
    const body = document.getElementById('repModalBody');

    // Parse complex fields
    let achievements = [];
    let news = [];
    let sources = [];
    try { achievements = rep.achievements ? JSON.parse(rep.achievements) : []; } catch (e) { }
    try { news = rep.news ? JSON.parse(rep.news) : []; } catch (e) { }
    try { sources = rep.sources ? JSON.parse(rep.sources) : []; } catch (e) { }

    const achievementsHtml = achievements.length ?
        `<ul>${achievements.map(a => `<li style="margin-bottom:0.5rem;">${a}</li>`).join('')}</ul>` :
        '<p style="color:var(--text-muted)">No specific data available.</p>';

    const newsHtml = news.length ?
        news.map(n => `
            <div class="news-item">
                <h5 style="margin-bottom:0.3rem">${n.headline}</h5>
                <small style="color:var(--text-muted)">${n.date}</small>
            </div>
        `).join('') : '<p style="color:var(--text-muted)">No recent news.</p>';

    const sourcesHtml = sources.length ?
        sources.map(s => `<span class="source-tag">${s}</span>`).join('') : '<span>N/A</span>';

    body.innerHTML = `
        <div class="modal-header-content">
            <img src="${rep.image_url || 'https://via.placeholder.com/100?text=MP'}" alt="${rep.name}" class="modal-avatar">
            <div>
                <h2 style="font-size:2rem; margin-bottom:0.5rem;">${rep.name}</h2>
                <p style="font-size:1.1rem; color: #a5b4fc; display:flex; align-items:center;">
                    ${rep.role} • ${rep.party} ${getPartySymbol(rep.party)}
                </p>
                <p style="color:var(--text-muted)">${rep.constituency}, ${rep.state}</p>
            </div>
        </div>

        <div style="margin-bottom: 2rem;">
            <p style="font-size: 1.05rem; line-height: 1.6;">${rep.bio}</p>
        </div>

        <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin-bottom: 2rem;">
            <div>
                <h3 style="margin-bottom:1rem; border-bottom:1px solid var(--glass-border); padding-bottom:0.5rem;">Achievements</h3>
                ${achievementsHtml}
            </div>
            <div>
                <h3 style="margin-bottom:1rem; border-bottom:1px solid var(--glass-border); padding-bottom:0.5rem;">Statistics</h3>
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap:1rem;">
                    <div>
                        <span class="stat-label">Term Length</span>
                        <p style="font-size:1.2rem; font-weight:bold;">${rep.years_in_office || 0} Years</p>
                    </div>
                    <div>
                        <span class="stat-label">Attendance</span>
                         <p style="font-size:1.2rem; font-weight:bold;">${rep.attendance_percentage || 0}%</p>
                    </div>
                     <div>
                        <span class="stat-label">Funds Used</span>
                         <p style="font-size:1.2rem; font-weight:bold;">₹${rep.funds_spent_crores || 0}Cr / ₹${rep.funds_total_crores || 0}Cr</p>
                    </div>
                </div>
            </div>
        </div>

        <div>
             <h3 style="margin-bottom:1rem; border-bottom:1px solid var(--glass-border); padding-bottom:0.5rem;">Recent News & Updates</h3>
             ${newsHtml}
        </div>

        <div style="margin-top: 2rem;">
            <p class="stat-label" style="margin-bottom:0.5rem;">Verified Sources:</p>
            ${sourcesHtml}
        </div>
    `;

    modal.classList.add('open');
    modal.style.display = 'flex'; // Ensure flex is applied for centering
}

function closeRepModal() {
    const modal = document.getElementById('repModal');
    modal.classList.remove('open');
    setTimeout(() => { modal.style.display = 'none'; }, 200); // Wait for transition if any, or instant
}

// Close on outside click
window.onclick = function (event) {
    const modal = document.getElementById('repModal');
    if (event.target == modal) {
        closeRepModal();
    }
}

function searchReps() {
    const query = document.getElementById('searchInput').value;
    trackEvent('search', query);
    fetchReps(query);
}

/* --- Location Logic --- */
function detectLocation() {
    if (!navigator.geolocation) {
        alert("Geolocation is not supported by your browser.");
        return;
    }

    const btn = document.querySelector('.location-btn');
    btn.innerHTML = "⏳ Locating...";

    navigator.geolocation.getCurrentPosition(async (position) => {
        const payload = {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude
        };

        try {
            const res = await fetch('/api/detect-location', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await res.json();

            btn.innerHTML = "📍 My MP";

            if (data.status === 'success') {
                let msg = `You are in ${data.location}.\n`;

                if (data.mp) {
                    msg += `MP: ${data.mp.name} (${data.mp.party})\n`;
                }

                if (data.local_reps) {
                    const lr = data.local_reps;
                    msg += `MLA: ${lr.mla_name || 'Unknown'} (${lr.mla_party || ''})\n`;
                    msg += `Councillor: ${lr.councillor_name || 'Unknown'} (${lr.councillor_party || ''})`;
                }

                alert(msg);

                // Also trigger chat to introduce
                toggleChat();
                addMessage(`I see you are in ${data.location}. Your MP is ${data.mp ? data.mp.name : 'unknown'}. How can I help you regarding them?`, 'ai');
            } else {
                alert("Could not detect MP: " + data.message);
            }
        } catch (e) {
            console.error(e);
            btn.innerHTML = "📍 My MP";
            alert("Location check failed.");
        }
    }, () => {
        btn.innerHTML = "📍 My MP";
        alert("Unable to retrieve your location.");
    });
}

/* --- Chat Logic --- */
const chatWidget = document.getElementById('chatWidget');
const chatMsgs = document.getElementById('chatMessages');
const chatInput = document.getElementById('chatInput');

function toggleChat() {
    chatWidget.classList.toggle('open');
}

function handleEnter(e) {
    if (e.key === 'Enter') sendMessage();
}

async function sendMessage(textOverride = null) {
    const text = textOverride || chatInput.value.trim();
    if (!text) return;

    // User Msg
    addMessage(text, 'user');
    chatInput.value = '';

    trackEvent('chat_query', text);

    // Loading State
    const loadingId = addMessage('Thinking...', 'ai');

    try {
        const res = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: text })
        });
        const data = await res.json();

        // Remove Loading interaction
        const loadingEl = document.querySelector(`[data-msg-id="${loadingId}"]`);
        if (loadingEl) loadingEl.remove();

        addMessage(data.response, 'ai', data.chat_id);

    } catch (e) {
        console.error(e);
        addMessage("Sorry, something went wrong.", 'ai');
    }
}

function addMessage(text, type, chatId = null) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `msg ${type}`;

    // Parse Suggestions if present
    let displayText = text;
    let suggestions = [];

    if (text.includes('SUGGESTIONS:')) {
        const parts = text.split('SUGGESTIONS:');
        displayText = parts[0].trim();
        try {
            suggestions = JSON.parse(parts[1].trim());
        } catch (e) { console.error("Could not parse suggestions", e); }
    }

    msgDiv.innerText = displayText;

    // Add unique ID for removal if needed
    const tempId = Date.now();
    msgDiv.setAttribute('data-msg-id', tempId);

    if (type === 'ai') {
        // Rating
        if (chatId) {
            const rateDiv = document.createElement('div');
            rateDiv.className = 'rating';
            rateDiv.innerHTML = `
                Rate: 
                <span class="star" onclick="rateChat(${chatId}, 1, this)">★</span>
                <span class="star" onclick="rateChat(${chatId}, 2, this)">★</span>
                <span class="star" onclick="rateChat(${chatId}, 3, this)">★</span>
                <span class="star" onclick="rateChat(${chatId}, 4, this)">★</span>
                <span class="star" onclick="rateChat(${chatId}, 5, this)">★</span>
            `;
            msgDiv.appendChild(rateDiv);
        }

        // Render Chips
        if (suggestions.length > 0) {
            const chipContainer = document.createElement('div');
            chipContainer.className = 'suggestion-chips';
            suggestions.forEach(s => {
                const chip = document.createElement('button');
                chip.className = 'chip';
                chip.innerText = s;
                chip.onclick = () => sendMessage(s);
                chipContainer.appendChild(chip);
            });
            msgDiv.appendChild(chipContainer);
        }
    }

    chatMsgs.appendChild(msgDiv);
    chatMsgs.scrollTop = chatMsgs.scrollHeight;
    return tempId;
}

async function rateChat(chatId, rating, starEl) {
    // Visual update
    const parent = starEl.parentElement;
    const stars = parent.querySelectorAll('.star');
    stars.forEach((s, idx) => {
        if (idx < rating) s.classList.add('active');
        else s.classList.remove('active');
    });

    // API Call
    await fetch('/api/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ chat_id: chatId, rating: rating })
    });
    console.log(`Rated chat ${chatId} as ${rating} stars`);
}
