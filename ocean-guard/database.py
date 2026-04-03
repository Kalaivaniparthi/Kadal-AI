# ============================================
# OCEANGUARD - Database Layer
# 3 Layers: GPS+AIS / Community Spotters / Coast Guard
# ============================================

import sqlite3
import random
import json
from datetime import datetime, timedelta
import ai_engine

DATABASE = 'kadalai.db'

def init_db():
    conn   = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS boats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            boat_id TEXT UNIQUE NOT NULL,
            village TEXT NOT NULL,
            lat REAL,
            lng REAL,
            risk_score INTEGER,
            status TEXT,
            plastic_dumped REAL DEFAULT 0,
            plastic_collected REAL DEFAULT 0,
            reward INTEGER DEFAULT 0,
            ai_reason TEXT DEFAULT '{}',
            transmission_type TEXT DEFAULT 'LoRa',
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dumping_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            boat_id TEXT,
            lat REAL,
            lng REAL,
            risk_score INTEGER,
            plastic_kg REAL,
            detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rewards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            boat_id TEXT,
            plastic_kg REAL,
            amount INTEGER,
            rewarded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Community spotter reports — Layer 3
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS spotter_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            boat_id TEXT,
            reporter_name TEXT,
            description TEXT,
            lat REAL,
            lng REAL,
            status TEXT DEFAULT 'pending',
            reported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Coast guard patrol actions — Layer 3
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patrol_actions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            boat_id TEXT,
            action TEXT,
            officer TEXT,
            result TEXT,
            actioned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'fisher',
            boat_id TEXT,
            village TEXT,
            phone TEXT
        )
    ''')

    # Fisher complaints table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fisher_complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            boat_id TEXT,
            fisher_name TEXT,
            complaint_type TEXT,
            description TEXT,
            status TEXT DEFAULT 'pending',
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # QR tagged bags table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS qr_bags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            qr_code TEXT UNIQUE NOT NULL,
            boat_id TEXT,
            issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            scanned_at TIMESTAMP,
            plastic_kg REAL DEFAULT 0,
            reward_amount INTEGER DEFAULT 0,
            status TEXT DEFAULT 'issued'
        )
    ''')

    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (username, password, role, boat_id, village) VALUES (?, ?, ?, ?, ?)",
                      ('admin', 'admin123', 'admin', None, None))

    # Sample fisher accounts
    sample_fishers = [
        ('fisher1', 'fish123', 'fisher', 'TN-Ram001', 'Rameswaram', '9876543210'),
        ('fisher2', 'fish123', 'fisher', 'TN-Tho002', 'Thoothukudi', '9876543211'),
        ('fisher3', 'fish123', 'fisher', 'TN-Nag003', 'Nagapattinam', '9876543212'),
    ]
    for f in sample_fishers:
        cursor.execute("SELECT * FROM users WHERE username = ?", (f[0],))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO users (username, password, role, boat_id, village, phone) VALUES (?, ?, ?, ?, ?, ?)", f)

    conn.commit()
    conn.close()
    print("✅ Database initialized!")


def get_all_boats():
    conn   = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM boats ORDER BY risk_score DESC")
    boats  = cursor.fetchall()
    conn.close()
    return boats


def add_boat(boat_id, village, lat, lng, risk_score, status,
             plastic_dumped=0, plastic_collected=0, reward=0,
             ai_reason='{}', transmission_type='LoRa'):
    conn   = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO boats
        (boat_id, village, lat, lng, risk_score, status,
         plastic_dumped, plastic_collected, reward, ai_reason, transmission_type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (boat_id, village, lat, lng, risk_score, status,
          plastic_dumped, plastic_collected, reward, ai_reason, transmission_type))
    conn.commit()
    conn.close()


def add_dumping_event(boat_id, lat, lng, risk_score, plastic_kg):
    conn   = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO dumping_events (boat_id, lat, lng, risk_score, plastic_kg)
        VALUES (?, ?, ?, ?, ?)
    ''', (boat_id, lat, lng, risk_score, plastic_kg))
    conn.commit()
    conn.close()


def add_reward(boat_id, plastic_kg, amount):
    conn   = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO rewards (boat_id, plastic_kg, amount) VALUES (?, ?, ?)
    ''', (boat_id, plastic_kg, amount))
    cursor.execute('''
        UPDATE boats SET plastic_collected = plastic_collected + ?, reward = reward + ?
        WHERE boat_id = ?
    ''', (plastic_kg, amount, boat_id))
    conn.commit()
    conn.close()


def add_spotter_report(boat_id, reporter_name, description, lat, lng):
    conn   = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO spotter_reports (boat_id, reporter_name, description, lat, lng)
        VALUES (?, ?, ?, ?, ?)
    ''', (boat_id, reporter_name, description, lat, lng))
    conn.commit()
    conn.close()


def get_spotter_reports(limit=20):
    conn   = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM spotter_reports ORDER BY reported_at DESC LIMIT ?
    ''', (limit,))
    reports = cursor.fetchall()
    conn.close()
    return reports


def get_spotter_count(boat_id):
    conn   = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM spotter_reports WHERE boat_id = ?", (boat_id,))
    count  = cursor.fetchone()[0]
    conn.close()
    return count


def add_patrol_action(boat_id, action, officer, result):
    conn   = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO patrol_actions (boat_id, action, officer, result)
        VALUES (?, ?, ?, ?)
    ''', (boat_id, action, officer, result))
    conn.commit()
    conn.close()


def get_patrol_actions(limit=20):
    conn   = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM patrol_actions ORDER BY actioned_at DESC LIMIT ?
    ''', (limit,))
    actions = cursor.fetchall()
    conn.close()
    return actions


def get_dashboard_stats():
    conn   = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM boats")
    total_boats = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM boats WHERE status = 'dumping'")
    dumping_boats = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM boats WHERE status = 'warning'")
    warning_boats = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM boats WHERE status = 'clean'")
    clean_boats = cursor.fetchone()[0]
    cursor.execute("SELECT SUM(reward) FROM boats")
    total_rewards = cursor.fetchone()[0] or 0
    cursor.execute("SELECT SUM(plastic_collected) FROM boats")
    plastic_collected = cursor.fetchone()[0] or 0
    cursor.execute("SELECT SUM(plastic_dumped) FROM boats")
    plastic_dumped = cursor.fetchone()[0] or 0
    cursor.execute("SELECT COUNT(*) FROM spotter_reports")
    total_reports = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM patrol_actions")
    total_patrols = cursor.fetchone()[0]

    conn.close()
    return {
        'total_boats':      total_boats,
        'dumping_boats':    dumping_boats,
        'warning_boats':    warning_boats,
        'clean_boats':      clean_boats,
        'total_rewards':    total_rewards,
        'plastic_collected': round(plastic_collected, 1),
        'plastic_dumped':   round(plastic_dumped, 1),
        'total_reports':    total_reports,
        'total_patrols':    total_patrols,
    }


def get_recent_dumping_events(limit=10):
    conn   = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM dumping_events ORDER BY detected_at DESC LIMIT ?
    ''', (limit,))
    events = cursor.fetchall()
    conn.close()
    return events


def get_reward_history(limit=10):
    conn   = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM rewards ORDER BY rewarded_at DESC LIMIT ?
    ''', (limit,))
    rewards = cursor.fetchall()
    conn.close()
    return rewards


def get_fisher_by_credentials(username, password):
    conn   = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user   = cursor.fetchone()
    conn.close()
    return user


def get_boat_by_id(boat_id):
    conn   = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM boats WHERE boat_id=?", (boat_id,))
    boat   = cursor.fetchone()
    conn.close()
    return boat


def add_fisher_complaint(boat_id, fisher_name, complaint_type, description):
    conn   = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO fisher_complaints (boat_id, fisher_name, complaint_type, description)
        VALUES (?, ?, ?, ?)
    ''', (boat_id, fisher_name, complaint_type, description))
    conn.commit()
    conn.close()


def get_fisher_complaints(boat_id=None, limit=20):
    conn   = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    if boat_id:
        cursor.execute("SELECT * FROM fisher_complaints WHERE boat_id=? ORDER BY submitted_at DESC LIMIT ?", (boat_id, limit))
    else:
        cursor.execute("SELECT * FROM fisher_complaints ORDER BY submitted_at DESC LIMIT ?", (limit,))
    complaints = cursor.fetchall()
    conn.close()
    return complaints


def issue_qr_bag(qr_code, boat_id):
    conn   = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO qr_bags (qr_code, boat_id) VALUES (?, ?)
    ''', (qr_code, boat_id))
    conn.commit()
    conn.close()


def scan_qr_bag(qr_code, plastic_kg):
    """Fisher scans QR bag at harbour — calculates and records reward."""
    conn   = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM qr_bags WHERE qr_code=? AND status='issued'", (qr_code,))
    bag = cursor.fetchone()
    if not bag:
        conn.close()
        return None, 'QR code not found or already scanned'
    reward_amount = int(plastic_kg * 20)
    cursor.execute('''
        UPDATE qr_bags SET scanned_at=CURRENT_TIMESTAMP, plastic_kg=?, reward_amount=?, status='redeemed'
        WHERE qr_code=?
    ''', (plastic_kg, reward_amount, qr_code))
    # Update boat reward
    cursor.execute('''
        UPDATE boats SET plastic_collected=plastic_collected+?, reward=reward+?
        WHERE boat_id=?
    ''', (plastic_kg, reward_amount, bag[2]))
    cursor.execute('''
        INSERT INTO rewards (boat_id, plastic_kg, amount) VALUES (?, ?, ?)
    ''', (bag[2], plastic_kg, reward_amount))
    conn.commit()
    conn.close()
    return reward_amount, 'success'


def get_qr_bags(boat_id, limit=20):
    conn   = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM qr_bags WHERE boat_id=? ORDER BY issued_at DESC LIMIT ?", (boat_id, limit))
    bags   = cursor.fetchall()
    conn.close()
    return bags


def get_fisher_rewards(boat_id, limit=10):
    conn   = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM rewards WHERE boat_id=? ORDER BY rewarded_at DESC LIMIT ?", (boat_id, limit))
    rewards = cursor.fetchall()
    conn.close()
    return rewards


def generate_qr_bags_for_boat(boat_id, count=5):
    """Issue QR bags to a boat during sample data generation."""
    import uuid
    for _ in range(count):
        qr_code = f"OG-{boat_id}-{uuid.uuid4().hex[:8].upper()}"
        issue_qr_bag(qr_code, boat_id)


def generate_sample_data():
    conn   = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM boats")
    count  = cursor.fetchone()[0]
    conn.close()

    if count > 0:
        print(f"✅ {count} boats already exist in database")
        return

    village_sea_zones = [
        ('Nagapattinam', [(10.55, 80.05), (10.65, 80.15), (10.75, 80.20), (10.60, 80.10)]),
        ('Thoothukudi',  [(8.70,  78.40), (8.80,  78.50), (8.60,  78.35), (8.75,  78.55)]),
        ('Rameswaram',   [(9.20,  79.50), (9.30,  79.60), (9.10,  79.45), (9.25,  79.55)]),
        ('Kanyakumari',  [(7.90,  77.80), (7.85,  77.70), (7.95,  77.90), (7.80,  77.75)]),
        ('Mandapam',     [(9.15,  79.20), (9.20,  79.30), (9.10,  79.15), (9.25,  79.25)]),
        ('Pamban',       [(9.20,  79.40), (9.15,  79.45), (9.25,  79.50), (9.10,  79.35)]),
        ('Kilakarai',    [(9.10,  78.90), (9.15,  79.00), (9.05,  78.85), (9.20,  78.95)]),
    ]

    # Sample spotter reporters
    reporter_names = ['Murugan K', 'Selvam R', 'Rajan P', 'Arumugam S', 'Kannan T']
    patrol_officers = ['Officer Vijay', 'Officer Priya', 'Officer Ravi']
    patrol_results  = [
        'Warning issued — boat owner cautioned',
        'Licence suspended for 30 days',
        'No evidence found — monitoring continues',
        'Fine of ₹5,000 imposed',
        'Boat impounded for inspection',
    ]

    for i in range(35):
        village, sea_points = random.choice(village_sea_zones)
        boat_id             = f"TN-{village[:3]}{i+1:03d}"
        base_lat, base_lng  = random.choice(sea_points)
        lat = base_lat + random.uniform(-0.04, 0.04)
        lng = base_lng + random.uniform(-0.04, 0.04)
        transmission_type   = 'LoRa' if random.random() > 0.15 else 'GSM'

        raw_score = random.randint(10, 95)
        if raw_score > 70:
            plastic_dumped    = round(random.uniform(15, 60), 1)
            plastic_collected = 0
            reward            = 0
            spotter_count     = random.randint(0, 3)
        elif raw_score > 40:
            plastic_dumped    = round(random.uniform(3, 18), 1)
            plastic_collected = 0
            reward            = 0
            spotter_count     = random.randint(0, 1)
        else:
            plastic_dumped    = 0
            plastic_collected = round(random.uniform(8, 40), 1)
            reward            = int(plastic_collected * 20)
            spotter_count     = 0

        # Add spotter reports for this boat
        for _ in range(spotter_count):
            add_spotter_report(
                boat_id,
                random.choice(reporter_names),
                random.choice([
                    "Saw this boat throwing plastic bags overboard at night",
                    "Boat stopped for 40 min in dumping zone, suspicious activity",
                    "Observed crew dumping nets and plastic waste into sea",
                    "Boat AIS was off, seen near restricted zone",
                ]),
                lat + random.uniform(-0.02, 0.02),
                lng + random.uniform(-0.02, 0.02)
            )

        analysis   = ai_engine.analyse_boat(boat_id, plastic_dumped, plastic_collected, spotter_count)
        risk_score = analysis['risk_score']
        status     = analysis['status']
        ai_reason  = json.dumps(analysis)

        if status == 'dumping':
            add_dumping_event(boat_id, lat, lng, risk_score, plastic_dumped)
            # Add a patrol action for some dumping boats
            if random.random() > 0.4:
                add_patrol_action(
                    boat_id,
                    'Coast guard inspection dispatched based on GPS flag',
                    random.choice(patrol_officers),
                    random.choice(patrol_results)
                )
        if status == 'clean' and plastic_collected > 0:
            add_reward(boat_id, plastic_collected, reward)

        add_boat(boat_id, village, lat, lng, risk_score, status,
                 plastic_dumped, plastic_collected, reward, ai_reason, transmission_type)

        # Issue QR bags to every boat
        generate_qr_bags_for_boat(boat_id, count=random.randint(3, 8))

    print("✅ Generated 35 sample boats in Gulf of Mannar!")


if __name__ == '__main__':
    init_db()
    generate_sample_data()
    stats = get_dashboard_stats()
    print(f"Total Boats: {stats['total_boats']}")
    print(f"Dumping: {stats['dumping_boats']} | Warning: {stats['warning_boats']} | Clean: {stats['clean_boats']}")
    print(f"Spotter Reports: {stats['total_reports']} | Patrols: {stats['total_patrols']}")
