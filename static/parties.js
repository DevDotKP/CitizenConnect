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
    'IN-HP': { name: 'Himachal Pradesh', total: 4, results: [{ p: 'BJP', s: 4, c: '#ff9933' }] }
};

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
        // Construct detailed tooltip
        let tip = `${info.name}\nTotal Seats: ${info.total}\n\n`;
        info.results.forEach(r => {
            tip += `${r.p}: ${r.s}\n`;
        });

        // Simple heuristic for color index:
        // 1: BJP Dominated (>50% seats)
        // 2: INC Dominated
        // 3: Regional/Other Dominated
        // 4: Mixed / Close Fight

        let colorVal = 4;
        const winner = info.results.reduce((prev, current) => (prev.s > current.s) ? prev : current);

        if (winner.p.includes('BJP')) colorVal = 1;
        else if (winner.p.includes('INC')) colorVal = 2;
        else if (['SP', 'TMC', 'DMK', 'TDP', 'BJD', 'AAP'].some(x => winner.p.includes(x))) colorVal = 3;

        rows.push([code, colorVal, tip]);
    }

    data.addRows(rows);

    var options = {
        region: 'IN',
        displayMode: 'regions',
        resolution: 'provinces',
        backgroundColor: { fill: 'transparent' },
        datalessRegionColor: '#1e293b',
        colorAxis: {
            colors: ['#3b82f6', '#fb923c', '#3b82f6', '#10b981', '#a855f7'],
            values: [0, 1, 2, 3, 4]
        },
        // 1=Orange(BJP), 2=Blue(INC), 3=Green(Regional), 4=Purple(Mixed)
        tooltip: { textStyle: { color: '#333' }, showColorCode: false },
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
