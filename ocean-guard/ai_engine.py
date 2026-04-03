# ============================================
# OCEANGUARD - AI Engine
# Layer 1: GPS + AIS behaviour scoring
# No hardware sensors — GPS is the truth
# ============================================
import random

# ── 1. Pattern Recognition AI ────────────────────────────────
def detect_dumping_patterns(boat_id, plastic_dumped, plastic_collected, spotter_reports=0):
    """
    Detects suspicious behaviour using:
    - GPS stop patterns (simulated from boat_id seed for demo)
    - AIS signal gaps
    - Community spotter reports
    - Collection history
    """
    patterns = []
    seed = sum(ord(c) for c in boat_id)
    rng  = random.Random(seed)

    # GPS behaviour signals
    if rng.random() > 0.40:
        patterns.append("GPS: Boat stationary >30 min inside known dumping zone")
    if rng.random() > 0.50:
        patterns.append("GPS: Night-time stop (10 PM–4 AM) far from fishing grounds")
    if rng.random() > 0.55:
        patterns.append("GPS: Same hotspot visited 3+ times this week")
    if rng.random() > 0.60:
        patterns.append("GPS: Unusual route deviation through restricted marine zone")
    if rng.random() > 0.65:
        patterns.append("GPS: Speed drop to <1 knot in open sea for >20 min")

    # AIS signals
    if rng.random() > 0.60:
        patterns.append("AIS: Signal gap >45 min — transponder possibly switched off")
    if rng.random() > 0.75:
        patterns.append("AIS: Position mismatch between AIS and GPS log")

    # Community spotter reports
    if spotter_reports >= 2:
        patterns.append(f"Community: {spotter_reports} verified spotter reports filed against this boat")
    elif spotter_reports == 1:
        patterns.append("Community: 1 spotter report filed — under review")

    # Positive signals
    if plastic_collected > 20:
        patterns.append(f"Positive: {plastic_collected} kg plastic returned to harbour")
    if plastic_collected > 0 and plastic_dumped == 0:
        patterns.append("Positive: Zero dumping history — consistent clean record")
    if plastic_dumped == 0 and plastic_collected == 0 and spotter_reports == 0:
        patterns.append("No suspicious patterns detected in current monitoring period")

    return patterns if patterns else ["No suspicious patterns detected"]


# ── 2. Scoring Algorithm AI ──────────────────────────────────
def calculate_risk_score(patterns, plastic_dumped, plastic_collected, spotter_reports=0):
    """
    GPS behaviour + AIS gaps + community reports = risk score
    """
    score     = 0
    breakdown = {}

    # GPS stop in dumping zone — strongest signal
    high_gps = [
        "GPS: Boat stationary >30 min inside known dumping zone",
        "GPS: Night-time stop (10 PM–4 AM) far from fishing grounds",
        "GPS: Same hotspot visited 3+ times this week",
    ]
    medium_gps = [
        "GPS: Unusual route deviation through restricted marine zone",
        "GPS: Speed drop to <1 knot in open sea for >20 min",
    ]
    gps_pts = 0
    for p in patterns:
        if p in high_gps:
            gps_pts += 15
        elif p in medium_gps:
            gps_pts += 8
    gps_pts = min(gps_pts, 45)
    breakdown["GPS behaviour signals"] = gps_pts
    score += gps_pts

    # AIS gap signals
    ais_pts = 0
    if "AIS: Signal gap >45 min — transponder possibly switched off" in patterns:
        ais_pts += 15
    if "AIS: Position mismatch between AIS and GPS log" in patterns:
        ais_pts += 10
    ais_pts = min(ais_pts, 25)
    breakdown["AIS signal analysis"] = ais_pts
    score += ais_pts

    # Community spotter reports
    spotter_pts = min(spotter_reports * 12, 24)
    if spotter_pts > 0:
        breakdown["Community spotter reports"] = spotter_pts
        score += spotter_pts

    # Plastic dumped history
    dump_pts = min(plastic_dumped * 0.3, 15)
    if dump_pts > 0:
        breakdown["Historical dumping record"] = round(dump_pts)
        score += dump_pts

    # Plastic collected reduces risk
    collect_pts = min(plastic_collected * 0.5, 20)
    if collect_pts > 0:
        breakdown["Clean collection record (negative risk)"] = -round(collect_pts)
        score -= collect_pts

    return max(0, min(100, round(score))), breakdown


# ── 3. Classification AI ─────────────────────────────────────
def classify_boat_risk(risk_score):
    if risk_score >= 71:
        return "dumping", "HIGH RISK — Immediate coast guard action required"
    elif risk_score >= 41:
        return "warning", "MEDIUM RISK — Increased GPS monitoring + inspection"
    else:
        return "clean",   "LOW RISK — Compliant behaviour, eligible for reward"


# ── 4. Decision AI ───────────────────────────────────────────
def get_action(status, spotter_reports=0):
    if status == "dumping":
        base = (
            "🚨 Flag for immediate coast guard patrol. "
            "GPS logs show repeated stops in dumping zones. "
            "Suspend fishing licence pending physical inspection."
        )
        if spotter_reports > 0:
            base += f" {spotter_reports} community report(s) support this flag."
        return base
    elif status == "warning":
        return (
            "📡 Increase GPS ping frequency to every 10 min. "
            "Schedule harbour inspection within 48 hours. "
            "Issue formal advisory notice to boat owner. "
            "Monitor AIS feed for further signal gaps."
        )
    else:
        return (
            "✅ No action required. "
            "Eligible for monthly clean-boat reward. "
            "Continue standard GPS monitoring schedule."
        )


# ── Master analyser ──────────────────────────────────────────
def analyse_boat(boat_id, plastic_dumped, plastic_collected, spotter_reports=0):
    patterns               = detect_dumping_patterns(boat_id, plastic_dumped, plastic_collected, spotter_reports)
    risk_score, breakdown  = calculate_risk_score(patterns, plastic_dumped, plastic_collected, spotter_reports)
    status, classification = classify_boat_risk(risk_score)
    action                 = get_action(status, spotter_reports)

    return {
        "risk_score":       risk_score,
        "status":           status,
        "patterns":         patterns,
        "score_breakdown":  breakdown,
        "classification":   classification,
        "action":           action,
        "spotter_reports":  spotter_reports,
    }
