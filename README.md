# 🌊 OceanGuard — AI-Powered Marine Plastic Prevention

> An AI-driven web application to detect, monitor, and prevent illegal plastic dumping by fishing boats in the **Gulf of Mannar, Tamil Nadu, India**.

---

## 📌 Overview

OceanGuard is a 3-layer marine pollution prevention system that uses **GPS behaviour analysis**, **community reporting**, and **coast guard coordination** to identify and act on illegal plastic dumping at sea.

It provides three separate dashboards:
- **Admin Dashboard** — Full monitoring, map, AI analysis, patrol management
- **Fisher Portal** — Complaint submission, QR bag rewards, dumping reports
- **Live Map** — Real-time boat tracking on Gulf of Mannar

---

## 🏗️ Project Structure

```
Kadal-AI/
│
├── ocean-guard/
│   ├── app.py              # Flask backend — all routes and API endpoints
│   ├── database.py         # SQLite database layer — all DB operations
│   ├── ai_engine.py        # AI engine — 4 detection functions
│   └── requirements.txt    # Python dependencies
│
├── templates/
│   ├── index.html          # Live map page with dashboard panel
│   ├── admin.html          # Admin dashboard — full monitoring
│   ├── login.html          # Admin login page
│   ├── fisher.html         # Fisher portal dashboard
│   └── fisher_login.html   # Fisher login page
│
├── static/
│   ├── style.css           # Shared Navy + White theme (all pages)
│   └── main.js             # Shared map utilities + boat popup logic
│
├── data/
│   └── sample_data.json    # Sample reference data
│
└── .gitignore
```

---

## 🧠 AI Engine — 4 Detection Functions

Located in `ocean-guard/ai_engine.py`

| # | Function | Role | Signals Used |
|---|---|---|---|
| 1 | `detect_dumping_patterns()` | Pattern Recognition AI | GPS stops, AIS gaps, community reports |
| 2 | `calculate_risk_score()` | Scoring Algorithm AI | Weighted scoring 0–100% |
| 3 | `classify_boat_risk()` | Classification AI | High / Medium / Low risk |
| 4 | `get_action()` | Decision AI | Recommended coast guard action |

### How the AI Works
```
GPS: Boat stationary >30 min in dumping zone
        +
AIS: Signal gap >45 min (transponder off)
        +
Community: 2 spotter reports filed
        =
Risk Score: 87% → Status: DUMPING
Action: 🚨 Alert Fisheries Department
```

---

## 🔒 3-Layer Detection System

```
Layer 1 — GPS + AIS Tracking
          Monitors all boats 24/7 across entire Gulf of Mannar
          AI scores behaviour patterns in real time
          Cost: ₹500–2,000/month AIS data feed

Layer 2 — Community Spotter Network
          Fishermen report suspicious boats via Fisher Portal
          GPS-tagged reports with description
          Verified reports earn ₹500 reward

Layer 3 — Coast Guard Patrol
          Admin flags high-risk boats from Layer 1 + 2
          Coast guard dispatched for targeted inspection
          Actions logged in dashboard
```

---

## 🗄️ Database Schema

Located in `ocean-guard/database.py` — SQLite (`kadalai.db`)

| Table | Purpose |
|---|---|
| `boats` | All 35 fishing boats with GPS, risk score, AI reason |
| `dumping_events` | GPS-flagged dumping incidents |
| `rewards` | Plastic collection reward payments |
| `spotter_reports` | Community dumping reports (Layer 2) |
| `patrol_actions` | Coast guard actions taken (Layer 3) |
| `fisher_complaints` | Complaints submitted by fishermen |
| `qr_bags` | QR-tagged plastic collection bags |
| `users` | Admin + fisher accounts |

---

## 🌐 API Endpoints

### Core
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/stats` | Dashboard statistics |
| GET | `/api/boats` | All boats with AI analysis |
| GET | `/api/dumping-events` | Recent GPS-flagged events |
| GET | `/api/rewards` | Reward payment history |

### Layer 2 — Community
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/spotter-report` | Submit a dumping report |
| GET | `/api/spotter-reports` | All spotter reports |

### Layer 3 — Coast Guard
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/patrol-action` | Log a patrol action |
| GET | `/api/patrol-actions` | All patrol actions |

### Fisher Portal
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/fisher/complaint` | Submit a complaint |
| GET | `/api/fisher/complaints` | Fisher's own complaints |
| GET | `/api/fisher/qr-bags` | Fisher's QR bags |
| POST | `/api/fisher/scan-qr` | Scan QR bag to claim reward |
| GET | `/api/fisher/boat-status` | Fisher's own boat AI status |
| GET | `/api/fisher/rewards` | Fisher's reward history |

---

## 🏷️ QR Bag Reward System

```
Harbour issues QR-coded bags to each boat
        ↓
Fisherman collects plastic at sea in tagged bag
        ↓
Returns to harbour — scans QR code + enters weight
        ↓
System credits ₹20 per kg automatically
        ↓
If bag found floating at sea → traced back to boat
```

Each QR code format: `OG-{BOAT_ID}-{UNIQUE_HEX}`
Example: `OG-TN-Ram001-AB12CD34`

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/Kalaivaniparthi/Kadal-AI.git
cd Kadal-AI

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Mac/Linux

# Install dependencies
pip install -r ocean-guard/requirements.txt

# Run the server
cd ocean-guard
python app.py
```

### Access the Application

| Page | URL | Credentials |
|---|---|---|
| Live Map | http://localhost:5000 | — |
| Admin Login | http://localhost:5000/login | `admin` / `admin123` |
| Admin Dashboard | http://localhost:5000/admin | — |
| Fisher Login | http://localhost:5000/fisher-login | `fisher1` / `fish123` |
| Fisher Portal | http://localhost:5000/fisher | — |

### Demo Fisher Accounts

| Username | Password | Village | Boat |
|---|---|---|---|
| `fisher1` | `fish123` | Rameswaram | TN-Ram001 |
| `fisher2` | `fish123` | Thoothukudi | TN-Tho002 |
| `fisher3` | `fish123` | Nagapattinam | TN-Nag003 |

---

## 🗺️ Coverage Area

**Gulf of Mannar, Tamil Nadu, India**

Monitoring 7 coastal fishing villages:
- Nagapattinam, Thoothukudi, Rameswaram
- Kanyakumari, Mandapam, Pamban, Kilakarai

5 known dumping hotspots (SDMRI Survey 2023):
- Tuticorin Offshore, Gulf of Mannar Core
- Mandapam Reef, Kanyakumari Waters, Nagai Basin

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask, Flask-CORS |
| Database | SQLite |
| Frontend | HTML, CSS, Vanilla JavaScript |
| Maps | Leaflet.js + CartoDB Voyager tiles |
| GPS Tracking | Simulated (LoRa / GSM per boat) |
| AI Engine | Custom rule-based scoring (Python) |

---

## 📊 Sample Data

On first startup, the system auto-generates:
- **35 fishing boats** across Gulf of Mannar sea zones
- **GPS behaviour patterns** seeded per boat ID
- **Spotter reports** for high-risk boats
- **Patrol actions** for flagged boats
- **QR bags** (3–8 per boat)
- **Reward records** for clean boats

---

## 🔮 Future Roadmap

- [ ] Real AIS data feed integration (MarineTraffic / INCOIS)
- [ ] Mobile app for fisher portal
- [ ] LoRa gateway integration for live GPS
- [ ] Photo upload for spotter reports
- [ ] SMS alerts to coast guard on high-risk flag
- [ ] Multi-language support (Tamil)

---

## 📄 Data Source

Dumping zone coordinates based on:
> **SDMRI Gulf of Mannar Marine Plastic Survey 2023**
> Sugar Durai Marine Research Institute, Tamil Nadu

---

## 👩‍💻 Author

**Kalaivani Parthi**
GitHub: [@Kalaivaniparthi](https://github.com/Kalaivaniparthi)

---

## 📜 License

This project is open source and available under the [MIT License](LICENSE).
