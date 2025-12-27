const API_URL = '/api/admin/stats';
const LOGIN_URL = '/api/admin/login';
let trafficChart, locationChart;

function getAuthHeaders() {
    const creds = localStorage.getItem('admin_creds'); // Stored as base64 'user:pass'
    if (!creds) return null;
    return { 'Authorization': `Basic ${creds}` };
}

async function login() {
    const u = document.getElementById('username').value;
    const p = document.getElementById('password').value;
    const creds = btoa(`${u}:${p}`);

    try {
        const res = await fetch(LOGIN_URL, {
            method: 'POST',
            headers: { 'Authorization': `Basic ${creds}` }
        });

        if (res.ok) {
            localStorage.setItem('admin_creds', creds);
            showDashboard();
        } else {
            document.getElementById('errorMsg').innerText = "Invalid credentials";
            document.getElementById('errorMsg').style.display = 'block';
        }
    } catch (e) { console.error(e); }
}

function logout() {
    localStorage.removeItem('admin_creds');
    location.reload();
}

async function showDashboard() {
    document.getElementById('loginSection').style.display = 'none';
    document.getElementById('dashboardSection').style.display = 'block';

    loadStats();
}

async function loadStats() {
    const headers = getAuthHeaders();
    if (!headers) { logout(); return; }

    const res = await fetch(API_URL, { headers });
    if (!res.ok) {
        if (res.status === 401) {
            logout();
        } else {
            console.error("Stats API Error:", res.status, res.statusText);
            // Optional: visual error feedback?
        }
        return;
    }

    const data = await res.json();

    // Overview
    document.getElementById('statUsers').innerText = data.new_users;
    document.getElementById('statDuration').innerText = data.avg_duration + 's';

    // Top Actions
    renderList('topActionsList', data.top_actions || [], 'event_type', 'count', '#6C63FF');

    // Drop-offs
    renderList('dropOffList', data.drop_offs || [], 'event_type', 'count', '#FF6584');

    // Charts
    renderTrafficChart(data.traffic_by_hour || []);
    renderLocationChart(data.top_locations || []);

    // Map
    renderMap(data.top_locations || []);

    // Chat Logs
    renderChatLogs(data.recent_chats || []);
}

function renderChatLogs(chats) {
    const tbody = document.getElementById('chatLogBody');
    tbody.innerHTML = '';
    chats.forEach(chat => {
        const row = document.createElement('tr');
        row.style.borderBottom = '1px solid rgba(255,255,255,0.1)';

        const time = new Date(chat.timestamp).toLocaleString();
        const rating = chat.rating ? '⭐'.repeat(chat.rating) : '-';

        row.innerHTML = `
            <td style="padding: 1rem; font-size: 0.9em; color: #aaa;">${time}</td>
            <td style="padding: 1rem;">${chat.user_query}</td>
            <td style="padding: 1rem; color: #ccc;">${chat.ai_response.substring(0, 100)}...</td>
            <td style="padding: 1rem;">${rating}</td>
        `;
        tbody.appendChild(row);
    });
}

function renderList(elementId, items, keyLabel, keyVal, color) {
    const list = document.getElementById(elementId);
    list.innerHTML = '';
    items.forEach(item => {
        const div = document.createElement('div');
        div.className = 'list-item';
        div.innerHTML = `<span>${item[keyLabel]}</span> <span style="color:${color}; font-weight:bold;">${item[keyVal]}</span>`;
        list.appendChild(div);
    });
}

function renderTrafficChart(data) {
    const ctx = document.getElementById('trafficChart').getContext('2d');
    const hours = Array.from({ length: 24 }, (_, i) => i.toString().padStart(2, '0'));
    const counts = hours.map(h => {
        const found = data.find(d => d.hour === h);
        return found ? found.count : 0;
    });

    if (trafficChart) trafficChart.destroy();

    trafficChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: hours,
            datasets: [{
                label: 'Activity',
                data: counts,
                borderColor: '#6C63FF',
                backgroundColor: 'rgba(108, 99, 255, 0.2)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: {
                y: { grid: { color: 'rgba(255,255,255,0.1)' } },
                x: { grid: { display: false } }
            }
        }
    });
}

function renderLocationChart(data) {
    const ctx = document.getElementById('locationChart').getContext('2d');
    const labels = data.map(d => d.location || 'Unknown');
    const counts = data.map(d => d.count);

    if (locationChart) locationChart.destroy();

    locationChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: counts,
                backgroundColor: ['#6C63FF', '#FF6584', '#3B82F6', '#10B981', '#F59E0B'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'bottom', labels: { color: '#ccc' } }
            }
        }
    });
}

let map;
function renderMap(locations) {
    if (!map) {
        map = L.map('worldMap').setView([20, 0], 2);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; OpenStreetMap contributors'
        }).addTo(map);
    }

    // Clear existing markers (simplistic approach: remove all layers and re-add tile)
    map.eachLayer((layer) => {
        if (layer instanceof L.Marker) {
            layer.remove();
        }
    });

    locations.forEach(loc => {
        if (loc.latitude && loc.longitude) {
            L.marker([loc.latitude, loc.longitude])
                .addTo(map)
                .bindPopup(`<b>${loc.location}</b><br>Visits: ${loc.count}`);
        }
    });
}

// Auto-login check
if (getAuthHeaders()) {
    showDashboard();
}
