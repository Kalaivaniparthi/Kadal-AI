// ── Shared constants ──────────────────────────────────────────
const DUMPING_ZONES = [
    { lat: 8.95,  lng: 78.55, name: 'Tuticorin Offshore',  risk: 'Critical' },
    { lat: 9.45,  lng: 79.65, name: 'Gulf of Mannar Core', risk: 'High'     },
    { lat: 9.35,  lng: 79.40, name: 'Mandapam Reef',       risk: 'High'     },
    { lat: 8.65,  lng: 78.30, name: 'Kanyakumari Waters',  risk: 'Medium'   },
    { lat: 10.65, lng: 80.30, name: 'Nagai Basin',         risk: 'High'     }
];

const VILLAGES = [
    { name: 'Nagapattinam', lat: 10.7649, lng: 79.8428 },
    { name: 'Thoothukudi',  lat: 8.7642,  lng: 78.1348 },
    { name: 'Rameswaram',   lat: 9.2876,  lng: 79.3129 },
    { name: 'Kanyakumari',  lat: 8.0883,  lng: 77.5385 },
    { name: 'Mandapam',     lat: 9.2833,  lng: 79.1167 },
    { name: 'Pamban',       lat: 9.2500,  lng: 79.2167 },
    { name: 'Kilakarai',    lat: 9.2333,  lng: 78.7833 }
];

// ── Helpers ───────────────────────────────────────────────────
function boatColor(status) {
    return status === 'dumping' ? '#e74c3c' : status === 'warning' ? '#f39c12' : '#27ae60';
}

function makeBoatIcon(status) {
    const color = boatColor(status);
    const pulse = status === 'dumping' ? `<div class="pulse-ring"></div>` : '';
    return L.divIcon({
        html: `<div style="position:relative;width:18px;height:18px;">
                 ${pulse}
                 <div style="width:18px;height:18px;border-radius:50%;
                   background:${color};border:2.5px solid rgba(255,255,255,0.9);
                   box-shadow:0 0 8px ${color}88;position:relative;z-index:1;">
                 </div>
               </div>`,
        iconSize: [18, 18],
        className: ''
    });
}

function boatPopupHtml(boat) {
    const color  = boatColor(boat.status);
    const ai     = boat.ai_reason || {};
    const statusLabel = boat.status === 'dumping' ? '🔴 DUMPING SUSPECTED'
                      : boat.status === 'warning'  ? '🟡 UNDER OBSERVATION'
                      : '🟢 CERTIFIED CLEAN';

    // AI Patterns
    const patterns = (ai.patterns || []).map(p =>
        `<li style="margin-bottom:3px;">• ${p}</li>`
    ).join('');

    // Score Breakdown
    const breakdown = Object.entries(ai.score_breakdown || {}).map(([k, v]) => {
        const sign   = v >= 0 ? '+' : '';
        const bcolor = v < 0  ? '#27ae60' : '#e74c3c';
        return `<div style="display:flex;justify-content:space-between;margin-bottom:2px;">
                    <span>${k}</span>
                    <span style="color:${bcolor};font-weight:600;">${sign}${v} pts</span>
                </div>`;
    }).join('');

    // Spotter badge
    const spotterBadge = (boat.spotter_reports > 0)
        ? `<span style="background:#fdecea;color:#c0392b;border:1px solid #f5c6cb;
               padding:2px 8px;border-radius:10px;font-size:10px;font-weight:700;margin-left:6px;">
               👥 ${boat.spotter_reports} report${boat.spotter_reports > 1 ? 's' : ''}
           </span>`
        : '';

    return `
        <div style="min-width:290px;max-width:330px;font-size:12.5px;line-height:1.7;color:#1a2a3a;">

            <div style="font-size:15px;font-weight:700;color:${color};margin-bottom:2px;">
                ${boat.id} ${spotterBadge}
            </div>
            <div style="font-size:11px;color:#5a7a96;margin-bottom:8px;">
                📍 ${boat.village} &nbsp;|&nbsp; 📶 ${boat.transmission_type || 'LoRa'}
            </div>
            <div style="border-top:1px solid #dce6f0;margin-bottom:10px;"></div>

            <!-- Status & Score -->
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
                <span style="background:${color}22;color:${color};border:1px solid ${color}55;
                    padding:3px 10px;border-radius:20px;font-size:11px;font-weight:700;">
                    ${statusLabel}
                </span>
                <span style="font-size:20px;font-weight:800;color:${color};">${boat.risk_score}%</span>
            </div>

            <!-- Layer 1: GPS + AIS Patterns -->
            <div style="background:#f5f8fc;border-radius:8px;padding:8px 10px;margin-bottom:8px;">
                <div style="font-size:10px;font-weight:700;text-transform:uppercase;
                    letter-spacing:0.5px;color:#5a7a96;margin-bottom:5px;">
                    🛰️ Layer 1 — GPS + AIS Pattern Recognition
                </div>
                <ul style="list-style:none;padding:0;margin:0;font-size:11.5px;color:#1a2a3a;">
                    ${patterns}
                </ul>
            </div>

            <!-- Score Breakdown -->
            <div style="background:#f5f8fc;border-radius:8px;padding:8px 10px;margin-bottom:8px;font-size:11.5px;">
                <div style="font-size:10px;font-weight:700;text-transform:uppercase;
                    letter-spacing:0.5px;color:#5a7a96;margin-bottom:5px;">
                    📊 Scoring Algorithm
                </div>
                ${breakdown}
            </div>

            <!-- Classification -->
            <div style="background:#f5f8fc;border-radius:8px;padding:8px 10px;margin-bottom:8px;font-size:11.5px;">
                <div style="font-size:10px;font-weight:700;text-transform:uppercase;
                    letter-spacing:0.5px;color:#5a7a96;margin-bottom:4px;">
                    🏷️ Classification
                </div>
                <span style="color:${color};font-weight:600;">${ai.classification || '—'}</span>
            </div>

            <!-- Layer 3: Decision / Action -->
            <div style="background:${color}11;border:1px solid ${color}33;
                border-radius:8px;padding:8px 10px;margin-bottom:8px;font-size:11.5px;">
                <div style="font-size:10px;font-weight:700;text-transform:uppercase;
                    letter-spacing:0.5px;color:#5a7a96;margin-bottom:4px;">
                    ⚡ Layer 3 — Coast Guard Decision
                </div>
                <span style="color:#1a2a3a;">${ai.action || '—'}</span>
            </div>

            <!-- Stats row -->
            <div style="border-top:1px solid #dce6f0;margin-top:8px;padding-top:8px;
                display:grid;grid-template-columns:1fr 1fr;gap:4px;font-size:11.5px;">
                <div>🗑️ Dumped: <b>${boat.plastic_dumped} kg</b></div>
                <div>♻️ Collected: <b>${boat.plastic_collected} kg</b></div>
                <div>💰 Reward: <b>₹${boat.reward.toLocaleString()}</b></div>
                <div>👥 Reports: <b style="color:${boat.spotter_reports > 0 ? '#c0392b' : '#1e7e34'}">
                    ${boat.spotter_reports}
                </b></div>
            </div>
        </div>`;
}

// ── Base map initializer ──────────────────────────────────────
function initBaseMap(elementId, center, zoom) {
    const map = L.map(elementId, { zoomControl: true }).setView(center, zoom);

    L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
        attribution: '© OpenStreetMap | SDMRI 2023',
        subdomains: 'abcd',
        maxZoom: 19
    }).addTo(map);

    DUMPING_ZONES.forEach(z => {
        const color = z.risk === 'Critical' ? '#e74c3c' : z.risk === 'High' ? '#e67e22' : '#f39c12';
        L.circle([z.lat, z.lng], {
            radius: 14000,
            color, fillColor: color, fillOpacity: 0.10, weight: 1.5, dashArray: '6 4'
        }).addTo(map).bindTooltip(`⚠️ ${z.name} — ${z.risk} Risk`, { sticky: true });
    });

    VILLAGES.forEach(v => {
        L.circleMarker([v.lat, v.lng], {
            radius: 6, color: '#0a1628', fillColor: '#1e6fa5', fillOpacity: 0.9, weight: 2
        }).addTo(map).bindTooltip(`🏘️ ${v.name}`);
    });

    return map;
}
