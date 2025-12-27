// Load Google Charts with Indian Domain
google.charts.load('current', {
    'packages': ['geochart'],
    'language': 'en',
    'region': 'IN' // Helps for loader localization
});
google.charts.setOnLoadCallback(drawMap);

const nationalStats = [
    {
        name: "Bharatiya Janata Party",
        abbr: "BJP",
        seats: 240,
        percentage: 44.2,
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
        name: "Samajwadi Party",
        abbr: "SP",
        seats: 37,
        percentage: 6.8,
        voteShare: 4.6,
        symbol: "https://upload.wikimedia.org/wikipedia/commons/thumb/0/03/Samajwadi_Party_Flag.svg/240px-Samajwadi_Party_Flag.svg.png",
        desc: "Major socialist party based in Uttar Pradesh. Key member of INDIA bloc."
    },
    {
        name: "All India Trinamool Congress",
        abbr: "TMC",
        seats: 29,
        percentage: 5.3,
        voteShare: 4.4,
        symbol: "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c0/All_India_Trinamool_Congress_symbol.svg/240px-All_India_Trinamool_Congress_symbol.svg.png",
        desc: "Dominant governing party in West Bengal. Led by Mamata Banerjee."
    },
    {
        name: "Dravida Munnetra Kazhagam",
        abbr: "DMK",
        seats: 22,
        percentage: 4.1,
        voteShare: 2.0,
        symbol: "https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/DMK_Flag.svg/240px-DMK_Flag.svg.png",
        desc: "Governing party of Tamil Nadu. Ideology: Social Justice, Dravidianism."
    },
    {
        name: "Telugu Desam Party",
        abbr: "TDP",
        seats: 16,
        percentage: 2.9,
        voteShare: 2.0,
        symbol: "https://upload.wikimedia.org/wikipedia/commons/thumb/4/42/Telugu_Desam_Party_Flag.svg/240px-Telugu_Desam_Party_Flag.svg.png",
        desc: "Ruling party of Andhra Pradesh. Key ally in the NDA government."
    },
    {
        name: "Janata Dal (United)",
        abbr: "JD(U)",
        seats: 12,
        percentage: 2.2,
        voteShare: 1.3,
        symbol: "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Janata_Dal_%28United%29_Flag.svg/240px-Janata_Dal_%28United%29_Flag.svg.png",
        desc: "Governing party in Bihar. Led by Nitish Kumar, NDA ally."
    },
    {
        name: "Shiv Sena (UBT)",
        abbr: "SS(UBT)",
        seats: 9,
        percentage: 1.7,
        voteShare: 2.5,
        symbol: "https://upload.wikimedia.org/wikipedia/commons/thumb/6/65/Shiv_Sena_%28Uddhav_Balasaheb_Thackeray%29_logo.svg/240px-Shiv_Sena_%28Uddhav_Balasaheb_Thackeray%29_logo.svg.png",
        desc: "Faction led by Uddhav Thackeray. Part of MVA (INDIA) in Maharashtra."
    },
    {
        name: "NCP (Sharadchandra Pawar)",
        abbr: "NCP(SP)",
        seats: 8,
        percentage: 1.5,
        voteShare: 1.0,
        symbol: "https://upload.wikimedia.org/wikipedia/commons/thumb/8/86/NCP_Sharad_Pawar_Flag.svg/240px-NCP_Sharad_Pawar_Flag.svg.png",
        desc: "Faction led by Sharad Pawar. Part of MVA (INDIA) in Maharashtra."
    },
    {
        name: "Shiv Sena",
        abbr: "SHS",
        seats: 7,
        percentage: 1.3,
        voteShare: 1.9,
        symbol: "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4a/Shiv_Sena_Logo.svg/180px-Shiv_Sena_Logo.svg.png",
        desc: "Faction led by Eknath Shinde. NDA ally in Maharashtra."
    },
    {
        name: "Lok Janshakti Party (RV)",
        abbr: "LJP(RV)",
        seats: 5,
        percentage: 0.9,
        voteShare: 0.5,
        symbol: "https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/LJP_Ram_Vilas_Symbol.svg/180px-LJP_Ram_Vilas_Symbol.svg.png",
        desc: "Bihar-based party led by Chirag Paswan. NDA ally."
    },
    {
        name: "CPI (Marxist)",
        abbr: "CPI(M)",
        seats: 4,
        percentage: 0.7,
        voteShare: 1.8,
        symbol: "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Cpm_election_symbol.svg/200px-Cpm_election_symbol.svg.png",
        desc: "Leading Left party, governs Kerala. Part of INDIA bloc."
    },
    {
        name: "Aam Aadmi Party",
        abbr: "AAP",
        seats: 3,
        percentage: 0.6,
        voteShare: 1.1,
        symbol: "https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/Aam_Aadmi_Party_logo_%28English%29.svg/240px-Aam_Aadmi_Party_logo_%28English%29.svg.png",
        desc: "Governing Delhi & Punjab. Part of INDIA bloc."
    },
    {
        name: "JMM",
        abbr: "JMM",
        seats: 3,
        percentage: 0.6,
        voteShare: 0.4,
        symbol: "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a4/Jharkhand_Mukti_Morcha_flag.svg/240px-Jharkhand_Mukti_Morcha_flag.svg.png",
        desc: "Ruling party in Jharkhand. Part of INDIA bloc."
    },
    {
        name: "Communist Party of India",
        abbr: "CPI",
        seats: 2,
        percentage: 0.4,
        voteShare: 0.5,
        symbol: "https://upload.wikimedia.org/wikipedia/commons/thumb/1/18/CPI-banner.svg/240px-CPI-banner.svg.png",
        desc: "Left wing party. Part of INDIA bloc."
    },
    {
        name: "AIMIM",
        abbr: "AIMIM",
        seats: 1,
        percentage: 0.2,
        voteShare: 0.3,
        symbol: "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c4/All_India_Majlis-e-Ittehadul_Muslimeen.svg/240px-All_India_Majlis-e-Ittehadul_Muslimeen.svg.png",
        desc: "Hyderabad based party led by Asaduddin Owaisi."
    }
];

const stateVotesData = {
    'IN-UP': { name: 'Uttar Pradesh', total: 80, results: [{ p: 'Samajwadi Party', s: 37, c: '#d92c2c' }, { p: 'BJP', s: 33, c: '#ff9933' }, { p: 'INC', s: 6, c: '#19aaed' }, { p: 'Others', s: 4, c: '#999' }] },
    'IN-MH': { name: 'Maharashtra', total: 48, results: [{ p: 'INC', s: 13, c: '#19aaed' }, { p: 'BJP', s: 9, c: '#ff9933' }, { p: 'Shiv Sena (UBT)', s: 9, c: '#ffc107' }, { p: 'NCP (SP)', s: 8, c: '#ff9933' }, { p: 'Others', s: 9, c: '#999' }] },
    'IN-WB': { name: 'West Bengal', total: 42, results: [{ p: 'TMC', s: 29, c: '#22c55e' }, { p: 'BJP', s: 12, c: '#ff9933' }, { p: 'INC', s: 1, c: '#19aaed' }] },
    'IN-TN': { name: 'Tamil Nadu', total: 39, results: [{ p: 'DMK', s: 22, c: '#d92c2c' }, { p: 'INC', s: 9, c: '#19aaed' }, { p: 'VCK', s: 2, c: '#333' }, { p: 'CPI', s: 2, c: '#d92c2c' }, { p: 'CPI(M)', s: 2, c: '#d92c2c' }] },
    'IN-BR': { name: 'Bihar', total: 40, results: [{ p: 'JD(U)', s: 12, c: '#22c55e' }, { p: 'BJP', s: 12, c: '#ff9933' }, { p: 'LJP (RV)', s: 5, c: '#ff9933' }, { p: 'RJD', s: 4, c: '#22c55e' }, { p: 'INC', s: 3, c: '#19aaed' }] },
    'IN-KA': { name: 'Karnataka', total: 28, results: [{ p: 'BJP', s: 17, c: '#ff9933' }, { p: 'INC', s: 9, c: '#19aaed' }, { p: 'JD(S)', s: 2, c: '#22c55e' }] },
    'IN-GJ': { name: 'Gujarat', total: 26, results: [{ p: 'BJP', s: 25, c: '#ff9933' }, { p: 'INC', s: 1, c: '#19aaed' }] },
    'IN-RJ': { name: 'Rajasthan', total: 25, results: [{ p: 'BJP', s: 14, c: '#ff9933' }, { p: 'INC', s: 8, c: '#19aaed' }, { p: 'Others', s: 3, c: '#999' }] },
    'IN-AP': { name: 'Andhra Pradesh', total: 25, results: [{ p: 'TDP', s: 16, c: '#ffeb3b' }, { p: 'YSRCP', s: 4, c: '#19aaed' }, { p: 'BJP', s: 3, c: '#ff9933' }, { p: 'JSP', s: 2, c: '#d92c2c' }] },
    'IN-MP': { name: 'Madhya Pradesh', total: 29, results: [{ p: 'BJP', s: 29, c: '#ff9933' }] },
    'IN-OR': { name: 'Odisha', total: 21, results: [{ p: 'BJP', s: 20, c: '#ff9933' }, { p: 'INC', s: 1, c: '#19aaed' }] },
    'IN-KL': { name: 'Kerala', total: 20, results: [{ p: 'INC', s: 14, c: '#19aaed' }, { p: 'IUML', s: 2, c: '#22c55e' }, { p: 'CPI(M)', s: 1, c: '#d92c2c' }, { p: 'BJP', s: 1, c: '#ff9933' }] },
    'IN-TG': { name: 'Telangana', total: 17, results: [{ p: 'BJP', s: 8, c: '#ff9933' }, { p: 'INC', s: 8, c: '#19aaed' }, { p: 'AIMIM', s: 1, c: '#22c55e' }] },
    'IN-CT': { name: 'Chhattisgarh', total: 11, results: [{ p: 'BJP', s: 10, c: '#ff9933' }, { p: 'INC', s: 1, c: '#19aaed' }] },
    'IN-JH': { name: 'Jharkhand', total: 14, results: [{ p: 'BJP', s: 8, c: '#ff9933' }, { p: 'JMM', s: 3, c: '#22c55e' }, { p: 'INC', s: 2, c: '#19aaed' }] },
    'IN-PB': { name: 'Punjab', total: 13, results: [{ p: 'INC', s: 7, c: '#19aaed' }, { p: 'AAP', s: 3, c: '#ffc107' }, { p: 'SAD', s: 1, c: '#999' }] },
    'IN-DL': { name: 'Delhi', total: 7, results: [{ p: 'BJP', s: 7, c: '#ff9933' }] },
    'IN-HR': { name: 'Haryana', total: 10, results: [{ p: 'BJP', s: 5, c: '#ff9933' }, { p: 'INC', s: 5, c: '#19aaed' }] },
    'IN-UT': { name: 'Uttarakhand', total: 5, results: [{ p: 'BJP', s: 5, c: '#ff9933' }] },
    'IN-HP': { name: 'Himachal Pradesh', total: 4, results: [{ p: 'BJP', s: 4, c: '#ff9933' }] },
    'IN-JK': { name: 'Jammu & Kashmir', total: 5, results: [{ p: 'JKNC', s: 2, c: '#22c55e' }, { p: 'BJP', s: 2, c: '#ff9933' }, { p: 'IND', s: 1, c: '#999' }] },
    'IN-AS': { name: 'Assam', total: 14, results: [{ p: 'BJP', s: 9, c: '#ff9933' }, { p: 'INC', s: 3, c: '#19aaed' }, { p: 'UPPL', s: 1, c: '#22c55e' }, { p: 'AGP', s: 1, c: '#22c55e' }] },
    'IN-GA': { name: 'Goa', total: 2, results: [{ p: 'BJP', s: 1, c: '#ff9933' }, { p: 'INC', s: 1, c: '#19aaed' }] },
    'IN-AR': { name: 'Arunachal Pradesh', total: 2, results: [{ p: 'BJP', s: 2, c: '#ff9933' }] },
    'IN-MN': { name: 'Manipur', total: 2, results: [{ p: 'INC', s: 2, c: '#19aaed' }] },
    'IN-ML': { name: 'Meghalaya', total: 2, results: [{ p: 'VPP', s: 1, c: '#333' }, { p: 'INC', s: 1, c: '#19aaed' }] },
    'IN-MZ': { name: 'Mizoram', total: 1, results: [{ p: 'ZPM', s: 1, c: '#22c55e' }] },
    'IN-NL': { name: 'Nagaland', total: 1, results: [{ p: 'INC', s: 1, c: '#19aaed' }] },
    'IN-SK': { name: 'Sikkim', total: 1, results: [{ p: 'SKM', s: 1, c: '#22c55e' }] },
    'IN-TR': { name: 'Tripura', total: 2, results: [{ p: 'BJP', s: 2, c: '#ff9933' }] },
    'IN-CH': { name: 'Chandigarh', total: 1, results: [{ p: 'INC', s: 1, c: '#19aaed' }] },
    'IN-LD': { name: 'Lakshadweep', total: 1, results: [{ p: 'INC', s: 1, c: '#19aaed' }] },
    'IN-AN': { name: 'Andaman & Nicobar', total: 1, results: [{ p: 'BJP', s: 1, c: '#ff9933' }] },
    'IN-LA': { name: 'Ladakh', total: 1, results: [{ p: 'IND', s: 1, c: '#999' }] },
    'IN-DN': { name: 'Dadra & Nagar Haveli', total: 2, results: [{ p: 'BJP', s: 1, c: '#ff9933' }, { p: 'IND', s: 1, c: '#999' }] },
    'IN-PY': { name: 'Puducherry', total: 1, results: [{ p: 'INC', s: 1, c: '#19aaed' }] }
};

// Render National Grid (Collapsible)
document.addEventListener('DOMContentLoaded', () => {
    const grid = document.getElementById('nationalGrid');
    if (!grid) return;

    // Initial Render
    renderParties(nationalStats.slice(0, 3), grid);

    // Add Toggle Button
    const btnContainer = document.createElement('div');
    btnContainer.style.width = '100%';
    btnContainer.style.textAlign = 'center';
    btnContainer.style.marginTop = '2rem';
    btnContainer.style.gridColumn = '1 / -1'; // Span full width

    const toggleBtn = document.createElement('button');
    toggleBtn.className = 'btn-primary';
    toggleBtn.innerHTML = 'Show All Parties ▼';
    toggleBtn.style.padding = '0.8rem 2rem';

    let isExpanded = false;

    toggleBtn.onclick = () => {
        if (isExpanded) {
            // Collapse
            grid.innerHTML = '';
            renderParties(nationalStats.slice(0, 3), grid);
            toggleBtn.innerHTML = 'Show All Parties ▼';
            grid.appendChild(btnContainer); // Re-append button
        } else {
            // Expand
            grid.innerHTML = '';
            renderParties(nationalStats, grid);
            toggleBtn.innerHTML = 'Show Less ▲';
            grid.appendChild(btnContainer);
        }
        isExpanded = !isExpanded;
    };

    btnContainer.appendChild(toggleBtn);
    grid.appendChild(btnContainer);
});

function renderParties(parties, container) {
    parties.forEach(p => {
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
        container.appendChild(div);
    });
}

function drawMap() {
    document.getElementById('loadingMap').style.display = 'none';

    var data = new google.visualization.DataTable();
    data.addColumn('string', 'State Code');
    data.addColumn('number', 'Seats'); // Dummy for color intensity if needed, or total seats
    data.addColumn({ type: 'string', role: 'tooltip', p: { html: true } });

    const rows = [];

    // Default color scale: 0 (No Data), 1 (BJP Lead), 2 (INC Lead), 3 (Regional Lead), 4 (Mixed)
    // Actually simplicity: We'll just define color buckets.
    // Let's iterate ISO codes.

    for (const [code, info] of Object.entries(stateVotesData)) {
        // Construct detailed HTML tooltip
        let rowsHtml = '';
        info.results.forEach(r => {
            rowsHtml += `
            <div style="display:flex; justify-content:space-between; margin-bottom:4px;">
                <span style="color: ${r.c}; font-weight:600;">${r.p}</span>
                <span style="margin-left:12px; font-weight:bold;">${r.s}</span>
            </div>`;
        });

        const tooltip = `
            <div style="padding: 12px; min-width: 150px; font-family: 'Inter', sans-serif;">
                <h4 style="margin:0 0 8px 0; border-bottom:1px solid #ddd; padding-bottom:4px; font-size:14px; color:#333;">${info.name}</h4>
                <div style="font-size:12px; color:#444;">
                    ${rowsHtml}
                </div>
                <div style="margin-top:6px; pt-1; font-size:11px; color:#666; text-align:right;">
                    Total: ${info.total}
                </div>
            </div>
        `;

        // Simple heuristic for color index:
        // 1: BJP Dominated (>50% seats)
        // 2: INC Dominated
        // 3: Regional/Other Dominated
        // 4: Mixed / Close Fight

        let colorVal = 4;
        const winner = info.results.reduce((prev, current) => (prev.s > current.s) ? prev : current);

        if (winner.p.includes('BJP')) colorVal = 1;
        else if (winner.p.includes('INC')) colorVal = 2;
        else if (['SP', 'TMC', 'DMK', 'TDP', 'BJD', 'AAP', 'JMM', 'JKNC'].some(x => winner.p.includes(x))) colorVal = 3;

        rows.push([code, colorVal, tooltip]);
    }

    data.addRows(rows);

    var options = {
        region: 'IN',
        domain: 'IN', // Force Indian political view
        displayMode: 'regions',
        resolution: 'provinces',
        backgroundColor: { fill: 'transparent' },
        datalessRegionColor: '#1e293b',
        colorAxis: {
            colors: ['#3b82f6', '#fb923c', '#3b82f6', '#10b981', '#a855f7'],
            values: [0, 1, 2, 3, 4]
        },
        // 1=Orange(BJP), 2=Blue(INC), 3=Green(Regional), 4=Purple(Mixed)
        legend: 'none', // Hide default legend
        tooltip: { isHtml: true }, // Enable HTML tooltips
        keepAspectRatio: true,
        width: '100%'
    };

    var chart = new google.visualization.GeoChart(document.getElementById('regions_div'));

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
    const data = stateVotesData[stateCode];

    if (!data) {
        body.innerHTML = `<h2>${stateCode}</h2><p>Detailed data coming soon.</p>`;
        modal.classList.add('open');
        return;
    }

    // Build Chart using simple HTML bars
    let barsHtml = '';
    data.results.forEach(r => {
        const percent = (r.s / data.total) * 100;
        barsHtml += `
            <div style="margin-bottom: 1rem;">
                <div style="display:flex; justify-content:space-between; margin-bottom:0.3rem;">
                    <strong>${r.p}</strong>
                    <span>${r.s} Seats</span>
                </div>
                <div style="background: rgba(255,255,255,0.1); height: 10px; border-radius: 5px; overflow: hidden;">
                    <div style="width: ${percent}%; background: ${r.c}; height: 100%;"></div>
                </div>
            </div>
        `;
    });

    body.innerHTML = `
        <h2 style="margin-bottom:0.5rem;">${data.name}</h2>
        <p style="color:var(--text-muted); margin-bottom:1.5rem;">Total Seats: ${data.total}</p>
        <div style="background:rgba(0,0,0,0.2); padding:1.5rem; border-radius:12px; border:1px solid var(--glass-border);">
            ${barsHtml}
        </div>
    `;

    modal.classList.add('open');
}
function closeStateModal() {
    document.getElementById('stateModal').classList.remove('open');
}

window.onclick = function (event) {
    if (event.target.classList.contains('modal-overlay')) { // Check correct class if using overlay div
        // Logic handled by specific close buttons usually, but legacy support:
    }
    const m1 = document.getElementById('criteriaModal');
    const m2 = document.getElementById('stateModal');
    if (event.target == m1) closeCriteriaModal();
    if (event.target == m2) closeStateModal();
}
