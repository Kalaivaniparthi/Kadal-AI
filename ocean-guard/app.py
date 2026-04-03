# ============================================
# OCEANGUARD - Flask Backend Server
# Layer 1: GPS+AIS | Layer 2: Community | Layer 3: Coast Guard
# Fisher Dashboard: Complaints + QR Bag Rewards
# ============================================

import json
import uuid
from flask import Flask, render_template, jsonify, request, redirect, url_for, session
from flask_cors import CORS
import database

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.secret_key = 'oceanguard_secret_2024'
CORS(app)

database.init_db()
database.generate_sample_data()

print("="*60)
print("🌊 OCEANGUARD BACKEND SERVER")
print("="*60)
print("Server:       http://localhost:5000")
print("Admin:        http://localhost:5000/admin  (admin/admin123)")
print("Fisher:       http://localhost:5000/fisher (fisher1/fish123)")
print("="*60)

# ── Page Routes ──────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin():
    if not session.get('logged_in') or session.get('role') != 'admin':
        return redirect(url_for('login'))
    return render_template('admin.html')

@app.route('/fisher')
def fisher():
    if not session.get('logged_in') or session.get('role') != 'fisher':
        return redirect(url_for('fisher_login'))
    return render_template('fisher.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('username') == 'admin' and request.form.get('password') == 'admin123':
            session['logged_in'] = True
            session['role']      = 'admin'
            return redirect(url_for('admin'))
        return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/fisher-login', methods=['GET', 'POST'])
def fisher_login():
    if request.method == 'POST':
        user = database.get_fisher_by_credentials(
            request.form.get('username'), request.form.get('password')
        )
        if user and user[3] == 'fisher':
            session['logged_in']   = True
            session['role']        = 'fisher'
            session['fisher_name'] = user[1]
            session['boat_id']     = user[4]
            session['village']     = user[5]
            return redirect(url_for('fisher'))
        return render_template('fisher_login.html', error='Invalid credentials')
    return render_template('fisher_login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# ── API: Core ────────────────────────────────────────────────

@app.route('/api/stats')
def api_stats():
    return jsonify(database.get_dashboard_stats())

@app.route('/api/boats')
def api_boats():
    boats     = database.get_all_boats()
    boat_list = []
    for boat in boats:
        spotter_count = database.get_spotter_count(boat[1])
        boat_list.append({
            'id':                boat[1],
            'village':           boat[2],
            'lat':               boat[3],
            'lng':               boat[4],
            'risk_score':        boat[5],
            'status':            boat[6],
            'plastic_dumped':    boat[7],
            'plastic_collected': boat[8],
            'reward':            boat[9],
            'ai_reason':         json.loads(boat[10]) if boat[10] else {},
            'transmission_type': boat[11],
            'spotter_reports':   spotter_count,
        })
    return jsonify(boat_list)

@app.route('/api/dumping-events')
def api_dumping_events():
    events = database.get_recent_dumping_events()
    return jsonify([{
        'id': e[0], 'boat_id': e[1], 'lat': e[2], 'lng': e[3],
        'risk_score': e[4], 'plastic_kg': e[5], 'detected_at': e[6]
    } for e in events])

@app.route('/api/rewards')
def api_rewards():
    rewards = database.get_reward_history()
    return jsonify([{
        'id': r[0], 'boat_id': r[1], 'plastic_kg': r[2],
        'amount': r[3], 'rewarded_at': r[4]
    } for r in rewards])

# ── API: Layer 2 — Community Spotter ────────────────────────

@app.route('/api/spotter-report', methods=['POST'])
def api_spotter_report():
    data = request.get_json()
    if not data or not data.get('boat_id') or not data.get('description'):
        return jsonify({'error': 'boat_id and description required'}), 400
    database.add_spotter_report(
        data['boat_id'], data.get('reporter_name', 'Anonymous'),
        data['description'], data.get('lat', 0), data.get('lng', 0)
    )
    return jsonify({'success': True, 'message': 'Report submitted. Thank you!'})

@app.route('/api/spotter-reports')
def api_spotter_reports():
    reports = database.get_spotter_reports()
    return jsonify([{
        'id': r[0], 'boat_id': r[1], 'reporter_name': r[2],
        'description': r[3], 'lat': r[4], 'lng': r[5],
        'status': r[6], 'reported_at': r[7]
    } for r in reports])

# ── API: Layer 3 — Coast Guard Patrol ───────────────────────

@app.route('/api/patrol-action', methods=['POST'])
def api_patrol_action():
    data = request.get_json()
    if not data or not data.get('boat_id'):
        return jsonify({'error': 'boat_id required'}), 400
    database.add_patrol_action(
        data['boat_id'], data.get('action', 'Inspection dispatched'),
        data.get('officer', 'Officer on duty'), data.get('result', 'Pending')
    )
    return jsonify({'success': True})

@app.route('/api/patrol-actions')
def api_patrol_actions():
    actions = database.get_patrol_actions()
    return jsonify([{
        'id': a[0], 'boat_id': a[1], 'action': a[2],
        'officer': a[3], 'result': a[4], 'actioned_at': a[5]
    } for a in actions])

# ── API: Fisher — Complaints ─────────────────────────────────

@app.route('/api/fisher/complaint', methods=['POST'])
def api_fisher_complaint():
    data = request.get_json()
    if not data or not data.get('description'):
        return jsonify({'error': 'description required'}), 400
    database.add_fisher_complaint(
        data.get('boat_id', session.get('boat_id', 'Unknown')),
        data.get('fisher_name', session.get('fisher_name', 'Anonymous')),
        data.get('complaint_type', 'General'),
        data['description']
    )
    return jsonify({'success': True, 'message': 'Complaint submitted successfully!'})

@app.route('/api/fisher/complaints')
def api_fisher_complaints():
    boat_id    = request.args.get('boat_id') or session.get('boat_id')
    complaints = database.get_fisher_complaints(boat_id)
    return jsonify([{
        'id': c[0], 'boat_id': c[1], 'fisher_name': c[2],
        'complaint_type': c[3], 'description': c[4],
        'status': c[5], 'submitted_at': c[6]
    } for c in complaints])

@app.route('/api/admin/complaints')
def api_admin_complaints():
    complaints = database.get_fisher_complaints()
    return jsonify([{
        'id': c[0], 'boat_id': c[1], 'fisher_name': c[2],
        'complaint_type': c[3], 'description': c[4],
        'status': c[5], 'submitted_at': c[6]
    } for c in complaints])

# ── API: Fisher — QR Bags ────────────────────────────────────

@app.route('/api/fisher/qr-bags')
def api_fisher_qr_bags():
    boat_id = request.args.get('boat_id') or session.get('boat_id')
    bags    = database.get_qr_bags(boat_id)
    return jsonify([{
        'id': b[0], 'qr_code': b[1], 'boat_id': b[2],
        'issued_at': b[3], 'scanned_at': b[4],
        'plastic_kg': b[5], 'reward_amount': b[6], 'status': b[7]
    } for b in bags])

@app.route('/api/fisher/scan-qr', methods=['POST'])
def api_scan_qr():
    data = request.get_json()
    if not data or not data.get('qr_code') or not data.get('plastic_kg'):
        return jsonify({'error': 'qr_code and plastic_kg required'}), 400
    reward, msg = database.scan_qr_bag(data['qr_code'], float(data['plastic_kg']))
    if reward is None:
        return jsonify({'error': msg}), 400
    return jsonify({'success': True, 'reward_amount': reward, 'message': f'✅ ₹{reward} reward credited!'})

@app.route('/api/fisher/issue-qr', methods=['POST'])
def api_issue_qr():
    data    = request.get_json()
    boat_id = data.get('boat_id') or session.get('boat_id')
    if not boat_id:
        return jsonify({'error': 'boat_id required'}), 400
    qr_code = f"OG-{boat_id}-{uuid.uuid4().hex[:8].upper()}"
    database.issue_qr_bag(qr_code, boat_id)
    return jsonify({'success': True, 'qr_code': qr_code})

@app.route('/api/fisher/boat-status')
def api_fisher_boat_status():
    boat_id = request.args.get('boat_id') or session.get('boat_id')
    boat    = database.get_boat_by_id(boat_id)
    if not boat:
        return jsonify({'error': 'Boat not found'}), 404
    spotter_count = database.get_spotter_count(boat[1])
    return jsonify({
        'id': boat[1], 'village': boat[2], 'lat': boat[3], 'lng': boat[4],
        'risk_score': boat[5], 'status': boat[6],
        'plastic_dumped': boat[7], 'plastic_collected': boat[8],
        'reward': boat[9], 'transmission_type': boat[11],
        'spotter_reports': spotter_count,
        'ai_reason': json.loads(boat[10]) if boat[10] else {}
    })

@app.route('/api/fisher/rewards')
def api_fisher_rewards():
    boat_id = request.args.get('boat_id') or session.get('boat_id')
    rewards = database.get_fisher_rewards(boat_id)
    return jsonify([{
        'id': r[0], 'boat_id': r[1], 'plastic_kg': r[2],
        'amount': r[3], 'rewarded_at': r[4]
    } for r in rewards])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
