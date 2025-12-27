// Load Google Charts
google.charts.load('current', {
    'packages': ['geochart'],
});
google.charts.setOnLoadCallback(drawMap);

const nationalStats = [
    {
        name: "Bharatiya Janata Party",
        abbr: "BJP",
        seats: 240,
        percentage: 44.2, // Seats percentage (240/543)
        voteShare: 36.6,
        symbol: "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Bharatiya_Janata_Party_logo.svg/240px-Bharatiya_Janata_Party_logo.svg.png",
        desc: "Ruling party, leads the NDA alliance. Ideology: Hindutva, Integral Humanism."
    },
    {
        name: "Indian National Congress",
        abbr: "INC",
        seats: 99,
        percentage: 18.2,
        voteShare: 21.2,
        symbol: "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6c/Indian_National_Congress_hand_logo.svg/240px-Indian_National_Congress_hand_logo.svg.png",
        desc: "Main opposition, leads the INDIA alliance. Ideology: Secularism, Social Liberalism."
    },
    {
        name: "Aam Aadmi Party",
        abbr: "AAP",
        seats: 3,
        percentage: 0.6,
        voteShare: 1.1,
        symbol: "https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/Aam_Aadmi_Party_logo_%28English%29.svg/240px-Aam_Aadmi_Party_logo_%28English%29.svg.png",
        desc: "Governing Delhi & Punjab. Ideology: Populism, Anti-corruption."
    },
    {
        name: "Bahujan Samaj Party",
        abbr: "BSP",
        seats: 0,
        percentage: 0,
        voteShare: 2.0, // approx
        symbol: "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d2/Elephant_Bahujan_Samaj_Party.svg/240px-Elephant_Bahujan_Samaj_Party.svg.png",
        desc: "Represents Bahujans (SC/ST/OBC). Strong base in UP."
    }
];

const statePartyData = {
    'IN-UP': ['Samajwadi Party (SP)', 'Bharatiya Janata Party (BJP)', 'Bahujan Samaj Party (BSP)'],
    'IN-MH': ['Shiv Sena (UBT)', 'NCP (SP)', 'BJP', 'INC'],
    'IN-WB': ['Trinamool Congress (TMC)', 'BJP', 'CPI(M)'],
    'IN-TN': ['Dravida Munnetra Kazhagam (DMK)', 'AIADMK', 'INC'],
    'IN-AP': ['Telugu Desam Party (TDP)', 'YSR Congress (YSRCP)', 'Jana Sena'],
    'IN-BR': ['Janata Dal United (JDU)', 'Rashtriya Janata Dal (RJD)', 'BJP'],
    'IN-KL': ['CPI(M) (LDF)', 'INC (UDF)', 'IUML'],
    'IN-DL': ['Aam Aadmi Party (AAP)', 'BJP'],
    'IN-PB': ['Aam Aadmi Party (AAP)', 'Shiromani Akali Dal (SAD)', 'INC'],
    'IN-OD': ['Biju Janata Dal (BJD)', 'BJP', 'INC'],
    'IN-TS': ['Bharat Rashtra Samithi (BRS)', 'INC', 'BJP'],
    'IN-KA': ['INC', 'BJP', 'JD(S)'],
    'IN-GJ': ['BJP', 'INC', 'AAP'],
    'IN-RJ': ['BJP', 'INC'],
    'IN-MP': ['BJP', 'INC'],
    'IN-CT': ['BJP', 'INC'],
    'IN-JH': ['Jharkhand Mukti Morcha (JMM)', 'BJP', 'AJSU'],
    'IN-AS': ['BJP', 'Asom Gana Parishad (AGP)', 'AIUDF'],
    'IN-JK': ['National Conference (NC)', 'PDP', 'BJP']
};

// Render National Grid
document.addEventListener('DOMContentLoaded', () => {
    const grid = document.getElementById('nationalGrid');
    nationalStats.forEach(p => {
        const div = document.createElement('div');
        div.className = 'party-card';
        div.innerHTML = `
            <div class="party-header">
                <img src="${p.symbol}" alt="${p.abbr}" style="width:40px;height:40px;object-fit:contain;">
                <div>
                    <h3 style="margin:0;">${p.name}</h3>
                    <span style="color:var(--text-muted);font-size:0.9rem;">${p.abbr}</span>
                </div>
            </div>
            <p style="font-size:0.9rem; color:var(--text-muted); flex-grow:1;">${p.desc}</p>
            <div class="seat-stats">
                <div style="text-align:center;">
                    <span style="display:block; font-weight:bold; font-size:1.2rem;">${p.seats}</span>
                    <span style="font-size:0.8rem; color:var(--text-muted);">Seats Won</span>
                </div>
                <div style="text-align:center;">
                    <span style="display:block; font-weight:bold; font-size:1.2rem; color:var(--accent);">${p.voteShare}%</span>
                    <span style="font-size:0.8rem; color:var(--text-muted);">Vote Share</span>
                </div>
            </div>
        `;
        grid.appendChild(div);
    });
});

function drawMap() {
    document.getElementById('loadingMap').style.display = 'none';

    // Header for map data
    var data = new google.visualization.DataTable();
    data.addColumn('string', 'State Code');   // ISO 3166-2:IN code
    data.addColumn('number', 'Value');        // Value for coloring
    data.addColumn({ type: 'string', role: 'tooltip' }); // Custom Tooltip

    // We use dummy values to color the map slightly different or uniform
    // ISO codes: https://en.wikipedia.org/wiki/ISO_3166-2:IN
    data.addRows([
        ['IN-UP', 1, 'Winner: SP (37), BJP (33)'],
        ['IN-MH', 2, 'Winner: MVA Alliance'],
        ['IN-WB', 3, 'Winner: TMC (29)'],
        ['IN-TN', 4, 'Winner: DMK Alliance'],
        ['IN-AP', 5, 'Winner: TDP (16)'],
        ['IN-BR', 6, 'NDA Leads'],
        ['IN-GJ', 1, 'BJP Sweep'],
        ['IN-RJ', 1, 'BJP Major Lead'],
        ['IN-KA', 2, 'INC Lead'],
        ['IN-KL', 4, 'UDF Sweep'],
        ['IN-DL', 1, 'BJP Sweep (7-0)'],
        ['IN-PB', 2, 'INC (7), AAP (3)'],
        ['IN-MP', 1, 'BJP Sweep'],
        ['IN-OD', 1, 'BJP Lead'],
        ['IN-TS', 2, 'INC/BJP Tie'],
        ['IN-CT', 1, 'BJP Sweep'],
        ['IN-JH', 6, 'JMM/BJP Contest'],
        ['IN-AS', 1, 'BJP Lead'],
        ['IN-JK', 6, 'NC/BJP']
    ]);

    var options = {
        region: 'IN',
        displayMode: 'regions',
        resolution: 'provinces',
        backgroundColor: { fill: 'transparent' },
        datalessRegionColor: '#1e293b', // Dark unmapped
        colorAxis: { colors: ['#fb923c', '#ef4444', '#22c55e', '#a855f7', '#3b82f6', '#eab308'] }, // Orange(BJP), Red(Left/Others), Green(TMC/AIADMK), Purple, Blue(INC/Others), Yellow(TDP)
        tooltip: { textStyle: { color: '#333' }, showColorCode: true },
        keepAspectRatio: true,
        width: '100%'
    };

    var chart = new google.visualization.GeoChart(document.getElementById('regions_div'));

    // Click Event
    google.visualization.events.addListener(chart, 'select', function () {
        var selection = chart.getSelection();
        if (selection.length > 0) {
            var row = selection[0].row;
            var stateCode = data.getValue(row, 0);
            openStateModal(stateCode);
        }
    });

    chart.draw(data, options);
}

// Modal Logic
function openCriteriaModal() {
    document.getElementById('criteriaModal').classList.add('open');
}
function closeCriteriaModal() {
    document.getElementById('criteriaModal').classList.remove('open');
}

function openStateModal(stateCode) {
    const modal = document.getElementById('stateModal');
    const body = document.getElementById('stateModalBody');
    const parties = statePartyData[stateCode] || ['Data gathering in progress...'];

    // Convert code to name (Simple map or generic)
    const stateNameMap = {
        'IN-UP': 'Uttar Pradesh', 'IN-MH': 'Maharashtra', 'IN-WB': 'West Bengal',
        'IN-TN': 'Tamil Nadu', 'IN-AP': 'Andhra Pradesh', 'IN-GJ': 'Gujarat',
        'IN-RJ': 'Rajasthan', 'IN-KA': 'Karnataka', 'IN-KL': 'Kerala', 'IN-DL': 'Delhi',
        'IN-PB': 'Punjab', 'IN-OD': 'Odisha', 'IN-TS': 'Telangana', 'IN-MP': 'Madhya Pradesh',
        'IN-BR': 'Bihar', 'IN-CT': 'Chhattisgarh', 'IN-JH': 'Jharkhand', 'IN-AS': 'Assam',
        'IN-JK': 'Jammu & Kashmir'
    };

    const name = stateNameMap[stateCode] || stateCode;

    body.innerHTML = `
        <h2 style="margin-bottom:1rem;">${name}</h2>
        <p style="color:var(--text-muted); margin-bottom:1.5rem;">Major Political Players</p>
        <div style="display:flex; flex-direction:column; gap:0.8rem;">
            ${parties.map(p => `
                <div style="background:rgba(255,255,255,0.05); padding:1rem; border-radius:12px; border:1px solid var(--glass-border);">
                    <span style="font-weight:bold; font-size:1.1rem;">${p}</span>
                </div>
            `).join('')}
        </div>
    `;

    modal.classList.add('open');
}
function closeStateModal() {
    document.getElementById('stateModal').classList.remove('open');
}

// Close modals on outside click
window.onclick = function (event) {
    if (event.target.classList.contains('modal-overlay')) {
        event.target.classList.remove('open');
    }
}
