# ============================================
# KADALAI - AI-Powered Marine Plastic Prevention
# Tamil Nadu Fishing Boat Tracking System
# WITH LIVE DASHBOARD ON RIGHT SIDE
# ============================================

import folium
import random
import webbrowser
import os
import json
from datetime import datetime

print("="*60)
print("🌊 KADALAI - AI Ocean Plastic Prevention System")
print("="*60)
print("Tracking fishing boats in Gulf of Mannar, Tamil Nadu")
print("="*60)

class KadalAI:
    def __init__(self):
        """Initialize the KadalAI system"""
        
        # Fishing villages in Gulf of Mannar, Tamil Nadu
        self.villages = {
            'Nagapattinam': {'lat': 10.7649, 'lng': 79.8428, 'boats': 320},
            'Thoothukudi': {'lat': 8.7642, 'lng': 78.1348, 'boats': 380},
            'Rameswaram': {'lat': 9.2876, 'lng': 79.3129, 'boats': 280},
            'Kanyakumari': {'lat': 8.0883, 'lng': 77.5385, 'boats': 210},
            'Mandapam': {'lat': 9.2833, 'lng': 79.1167, 'boats': 150},
            'Pamban': {'lat': 9.2500, 'lng': 79.2167, 'boats': 120},
            'Kilakarai': {'lat': 9.2333, 'lng': 78.7833, 'boats': 180},
            'Tiruvarur': {'lat': 10.7667, 'lng': 79.6333, 'boats': 200},
            'Pudukkottai': {'lat': 10.3833, 'lng': 79.3667, 'boats': 150}
        }
        
        # Dumping zones - ALL in SEA
        self.dumping_zones = [
            {'lat': 8.95, 'lng': 78.55, 'name': 'Tuticorin Offshore', 'risk': 'Critical', 'area': '548 m² debris', 'color': 'darkred'},
            {'lat': 9.45, 'lng': 79.65, 'name': 'Gulf of Mannar Core', 'risk': 'High', 'area': '1,152 m² affected', 'color': 'red'},
            {'lat': 9.35, 'lng': 79.40, 'name': 'Mandapam Reef', 'risk': 'High', 'area': 'Ghost nets reported', 'color': 'red'},
            {'lat': 8.65, 'lng': 78.30, 'name': 'Kanyakumari Waters', 'risk': 'Medium', 'area': 'Plastic accumulation', 'color': 'orange'},
            {'lat': 10.65, 'lng': 80.30, 'name': 'Nagai Basin', 'risk': 'High', 'area': 'Fishing debris hotspot', 'color': 'red'}
        ]
        
        self.reward_per_kg = 20
        print("✅ KadalAI System Initialized!")
    
    def create_boats(self):
        """Create boats placed in WATER (offshore)"""
        
        boats = []
        
        for village, data in self.villages.items():
            # Create 4-6 boats per village
            num_boats = random.randint(4, 6)
            
            for i in range(num_boats):
                # Place boats in water (offshore)
                lat_offset = random.uniform(0.8, 2.0)
                lng_offset = random.uniform(0.5, 1.5)
                
                risk_score = random.randint(10, 95)
                
                boat = {
                    'id': f"TN-{village[:3]}{i+1:03d}",
                    'village': village,
                    'lat': data['lat'] + lat_offset,
                    'lng': data['lng'] + lng_offset,
                    'risk_score': risk_score,
                    'plastic_dumped': 0,
                    'plastic_collected': 0,
                    'reward': 0
                }
                
                if risk_score > 70:
                    boat['status'] = 'dumping'
                    boat['plastic_dumped'] = random.randint(15, 70)
                    boat['status_text'] = 'HIGH RISK - DUMPING'
                    boat['status_color'] = 'red'
                elif risk_score > 40:
                    boat['status'] = 'warning'
                    boat['plastic_dumped'] = random.randint(3, 20)
                    boat['status_text'] = 'MEDIUM RISK - MONITOR'
                    boat['status_color'] = 'orange'
                else:
                    boat['status'] = 'clean'
                    boat['plastic_collected'] = random.randint(8, 40)
                    boat['reward'] = boat['plastic_collected'] * self.reward_per_kg
                    boat['status_text'] = 'LOW RISK - CLEAN'
                    boat['status_color'] = 'green'
                
                boats.append(boat)
        
        return boats
    
    def create_map_with_dashboard(self, boats, stats):
        """Create HTML map with right-side dashboard"""
        
        # Convert boats data to JSON for JavaScript
        boats_json = []
        for boat in boats:
            boats_json.append({
                'id': boat['id'],
                'village': boat['village'],
                'lat': boat['lat'],
                'lng': boat['lng'],
                'risk_score': boat['risk_score'],
                'status': boat['status'],
                'status_text': boat['status_text'],
                'plastic_dumped': boat.get('plastic_dumped', 0),
                'plastic_collected': boat.get('plastic_collected', 0),
                'reward': boat.get('reward', 0)
            })
        
        # Create base map
        m = folium.Map(location=[9.0, 79.0], zoom_start=8, control_scale=True)
        
        # ========== ADD DUMPING ZONES ==========
        for zone in self.dumping_zones:
            folium.Circle(
                radius=15000,
                location=[zone['lat'], zone['lng']],
                color=zone['color'],
                fill=True,
                fill_color=zone['color'],
                fill_opacity=0.4,
                weight=3,
                popup=f"""
                <div style="font-family: Arial; width: 280px; padding: 12px;">
                    <h3 style="color: #dc3545;">⚠️ {zone['name']}</h3>
                    <b>Risk:</b> {zone['risk']}<br>
                    <b>Area:</b> {zone['area']}<br>
                    <b>Source:</b> SDMRI Survey 2023
                </div>
                """
            ).add_to(m)
        
        # ========== ADD VILLAGES ==========
        for village, data in self.villages.items():
            folium.Marker(
                location=[data['lat'], data['lng']],
                popup=f"<b>🏘️ {village}</b><br>🚢 Boats: {data['boats']}",
                icon=folium.Icon(color='blue', icon='info-sign')
            ).add_to(m)
        
        # ========== ADD BOATS ==========
        for boat in boats:
            if boat['status'] == 'dumping':
                boat_emoji = '🔴🚤'
                popup_html = f"""
                <div style="width: 300px; padding: 12px; background: #ffe6e6;">
                    <h3 style="color: red;">🔴 {boat['id']}</h3>
                    <b>Village:</b> {boat['village']}<br>
                    <b>Risk Score:</b> <span style="color: red; font-size: 18px;">{boat['risk_score']}%</span><br>
                    <b>Status:</b> DUMPING SUSPECTED<br>
                    <b>Plastic Dumped:</b> {boat['plastic_dumped']} kg<br>
                    <b>Action:</b> Alert Authorities
                </div>
                """
            elif boat['status'] == 'warning':
                boat_emoji = '🟡🚤'
                popup_html = f"""
                <div style="width: 300px; padding: 12px; background: #fff0e0;">
                    <h3 style="color: orange;">🟡 {boat['id']}</h3>
                    <b>Village:</b> {boat['village']}<br>
                    <b>Risk Score:</b> <span style="color: orange; font-size: 18px;">{boat['risk_score']}%</span><br>
                    <b>Status:</b> UNDER OBSERVATION<br>
                    <b>Plastic Dumped:</b> {boat['plastic_dumped']} kg
                </div>
                """
            else:
                boat_emoji = '🟢🚤'
                popup_html = f"""
                <div style="width: 300px; padding: 12px; background: #e6ffe6;">
                    <h3 style="color: green;">🟢 {boat['id']}</h3>
                    <b>Village:</b> {boat['village']}<br>
                    <b>Risk Score:</b> <span style="color: green; font-size: 18px;">{boat['risk_score']}%</span><br>
                    <b>Status:</b> CLEAN BOAT<br>
                    <b>Plastic Collected:</b> {boat['plastic_collected']} kg<br>
                    <b>Reward:</b> ₹{boat['reward']}
                </div>
                """
            
            folium.Marker(
                location=[boat['lat'], boat['lng']],
                popup=folium.Popup(popup_html, max_width=350),
                tooltip=f"{boat_emoji} {boat['id']} - {boat['risk_score']}%",
                icon=folium.DivIcon(
                    html=f'<div style="font-size: 26px;">{boat_emoji}</div>'
                )
            ).add_to(m)
        
        # ========== ADD CUSTOM HTML DASHBOARD ==========
        dashboard_html = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                .dashboard {{
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    width: 320px;
                    background: white;
                    border-radius: 12px;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
                    z-index: 1000;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    overflow: hidden;
                }}
                .dashboard-header {{
                    background: linear-gradient(135deg, #006994, #004d66);
                    color: white;
                    padding: 15px;
                    text-align: center;
                }}
                .dashboard-header h2 {{
                    margin: 0;
                    font-size: 20px;
                }}
                .dashboard-header p {{
                    margin: 5px 0 0;
                    font-size: 11px;
                    opacity: 0.9;
                }}
                .stats-container {{
                    padding: 15px;
                }}
                .stat-card {{
                    background: #f8f9fa;
                    border-radius: 10px;
                    padding: 12px;
                    margin-bottom: 12px;
                    border-left: 4px solid;
                    transition: transform 0.2s;
                }}
                .stat-card:hover {{
                    transform: translateX(-5px);
                }}
                .stat-title {{
                    font-size: 12px;
                    color: #666;
                    margin-bottom: 5px;
                }}
                .stat-value {{
                    font-size: 28px;
                    font-weight: bold;
                    color: #2c3e50;
                }}
                .stat-unit {{
                    font-size: 12px;
                    color: #999;
                }}
                .risk-list {{
                    max-height: 250px;
                    overflow-y: auto;
                }}
                .risk-item {{
                    padding: 10px;
                    border-bottom: 1px solid #eee;
                    cursor: pointer;
                }}
                .risk-item:hover {{
                    background: #f0f0f0;
                }}
                .risk-badge {{
                    display: inline-block;
                    width: 10px;
                    height: 10px;
                    border-radius: 50%;
                    margin-right: 8px;
                }}
                .risk-high {{ background: #dc3545; }}
                .risk-medium {{ background: #ffc107; }}
                .risk-low {{ background: #28a745; }}
                .refresh-btn {{
                    background: #e67e22;
                    color: white;
                    border: none;
                    padding: 10px;
                    width: 100%;
                    cursor: pointer;
                    font-size: 14px;
                    font-weight: bold;
                    transition: background 0.3s;
                }}
                .refresh-btn:hover {{
                    background: #d35400;
                }}
                .timestamp {{
                    text-align: center;
                    font-size: 10px;
                    color: #999;
                    padding: 10px;
                    border-top: 1px solid #eee;
                }}
                .section-title {{
                    font-size: 14px;
                    font-weight: bold;
                    margin: 10px 0;
                    color: #2c3e50;
                }}
            </style>
        </head>
        <body>
            <div class="dashboard">
                <div class="dashboard-header">
                    <h2>🌊 KADALAI DASHBOARD</h2>
                    <p>AI-Powered Marine Monitoring | Gulf of Mannar</p>
                </div>
                
                <div class="stats-container">
                    <div class="stat-card" style="border-left-color: #006994;">
                        <div class="stat-title">🚢 TOTAL BOATS TRACKED</div>
                        <div class="stat-value">{stats['total_boats']}</div>
                    </div>
                    
                    <div class="stat-card" style="border-left-color: #dc3545;">
                        <div class="stat-title">🔴 DUMPING EVENTS (HIGH RISK)</div>
                        <div class="stat-value">{stats['dumping_boats']}</div>
                        <div class="stat-unit">suspected dumping boats</div>
                    </div>
                    
                    <div class="stat-card" style="border-left-color: #ffc107;">
                        <div class="stat-title">🟡 SUSPENDED BOATS (MEDIUM RISK)</div>
                        <div class="stat-value">{stats['warning_boats']}</div>
                        <div class="stat-unit">under observation</div>
                    </div>
                    
                    <div class="stat-card" style="border-left-color: #28a745;">
                        <div class="stat-title">🟢 CLEAN BOATS</div>
                        <div class="stat-value">{stats['clean_boats']}</div>
                        <div class="stat-unit">rewarded for clean behavior</div>
                    </div>
                    
                    <div class="stat-card" style="border-left-color: #e67e22;">
                        <div class="stat-title">💰 REWARDS DISTRIBUTED</div>
                        <div class="stat-value">₹{stats['total_rewards']:,}</div>
                    </div>
                    
                    <div class="stat-card" style="border-left-color: #17a2b8;">
                        <div class="stat-title">♻️ PLASTIC COLLECTED</div>
                        <div class="stat-value">{stats['plastic_collected']} <span class="stat-unit">kg</span></div>
                    </div>
                    
                    <div class="stat-card" style="border-left-color: #20c997;">
                        <div class="stat-title">🐠 MARINE ANIMALS SAVED</div>
                        <div class="stat-value">{stats['animals_saved']}</div>
                    </div>
                    
                    <div class="section-title">⚠️ HIGH RISK BOATS (Priority)</div>
                    <div class="risk-list" id="riskList">
                        {self.generate_risk_list_html(boats)}
                    </div>
                </div>
                
                <button class="refresh-btn" onclick="location.reload()">
                    🔄 REFRESH DATA
                </button>
                
                <div class="timestamp">
                    Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
                    Data Source: SDMRI Gulf of Mannar Survey 2023
                </div>
            </div>
            
            <style>
                .folium-map {{
                    margin-right: 340px;
                }}
            </style>
        </body>
        </html>
        '''
        
        # Add dashboard to map
        m.get_root().html.add_child(folium.Element(dashboard_html))
        
        # Add title
        title_html = '''
        <div style="position: fixed; top: 20px; left: 20px; z-index: 1000; background: white; padding: 8px 15px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.2); font-family: Arial;">
            <b>🌊 KADALAI</b> | AI Marine Monitoring
        </div>
        '''
        m.get_root().html.add_child(folium.Element(title_html))
        
        # Add legend
        legend_html = '''
        <div style="position: fixed; bottom: 20px; left: 20px; z-index: 1000; background: white; padding: 8px 12px; border-radius: 8px; font-size: 11px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
            <b>📌 LEGEND</b><br>
            🔴 Red Circle = Dumping Zone<br>
            🟢🚤 Green = Clean Boat<br>
            🟡🚤 Yellow = Monitor<br>
            🔴🚤 Red = Dumping Suspect<br>
            🔵 Blue = Fishing Village
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        
        return m
    
    def generate_risk_list_html(self, boats):
        """Generate HTML for high risk boats list"""
        
        # Get high risk boats (risk > 70)
        high_risk = [b for b in boats if b['risk_score'] > 70]
        high_risk.sort(key=lambda x: x['risk_score'], reverse=True)
        
        html = ""
        for boat in high_risk[:10]:  # Show top 10
            html += f'''
            <div class="risk-item" onclick="alert('Boat: {boat['id']}\\nVillage: {boat['village']}\\nRisk: {boat['risk_score']}%\\nPlastic Dumped: {boat.get('plastic_dumped', 0)} kg')">
                <span class="risk-badge risk-high"></span>
                <strong>{boat['id']}</strong><br>
                <small>{boat['village']} | Risk: {boat['risk_score']}%</small>
            </div>
            '''
        
        if not html:
            html = '<div style="padding: 10px; text-align: center; color: #999;">No high risk boats detected</div>'
        
        return html
    
    def calculate_stats(self, boats):
        """Calculate statistics"""
        
        total_boats = len(boats)
        dumping_boats = len([b for b in boats if b['status'] == 'dumping'])
        warning_boats = len([b for b in boats if b['status'] == 'warning'])
        clean_boats = len([b for b in boats if b['status'] == 'clean'])
        total_rewards = sum(b.get('reward', 0) for b in boats)
        plastic_collected = sum(b.get('plastic_collected', 0) for b in boats)
        plastic_dumped = sum(b.get('plastic_dumped', 0) for b in boats)
        
        return {
            'total_boats': total_boats,
            'dumping_boats': dumping_boats,
            'warning_boats': warning_boats,
            'clean_boats': clean_boats,
            'total_rewards': total_rewards,
            'plastic_collected': plastic_collected,
            'plastic_dumped': plastic_dumped,
            'animals_saved': int(plastic_collected / 2)
        }

# ============================================
# RUN THE SYSTEM
# ============================================

print("\n🚀 Starting KadalAI System...\n")

# Initialize
kadal = KadalAI()

# Create boats
print("📡 Creating fishing boats in Gulf of Mannar waters...")
boats = kadal.create_boats()

# Calculate stats
stats = kadal.calculate_stats(boats)

# Print summary
print("\n" + "="*60)
print("📊 KADALAI - LIVE STATISTICS")
print("="*60)
print(f"🚢 Total Boats Tracked: {stats['total_boats']}")
print(f"🔴 Dumping Events (High Risk): {stats['dumping_boats']}")
print(f"🟡 Suspended Boats (Medium Risk): {stats['warning_boats']}")
print(f"🟢 Clean Boats: {stats['clean_boats']}")
print(f"💰 Total Rewards: ₹{stats['total_rewards']:,}")
print(f"♻️ Plastic Collected: {stats['plastic_collected']} kg")
print(f"🗑️ Plastic Dumped Prevented: {stats['plastic_dumped']} kg")
print(f"🐠 Marine Animals Saved: {stats['animals_saved']}")
print("="*60)

# Create map with dashboard
print("\n🗺️ Creating interactive map with dashboard...")
map_html = kadal.create_map_with_dashboard(boats, stats)

# Save map
map_file = 'kadalai_map.html'
map_html.save(map_file)
print(f"✅ Map saved as '{map_file}'")

# Open map automatically
print("\n🌐 Opening map in browser...")
webbrowser.open('file://' + os.path.abspath(map_file))

print("\n" + "="*60)
print("✅ KADALAI SYSTEM READY!")
print("="*60)
print("\n📊 DASHBOARD FEATURES:")
print("   📍 Right side dashboard shows:")
print("      • Total boats tracked")
print("      • Dumping events (high risk)")
print("      • Suspended boats (medium risk)")
print("      • Clean boats with rewards")
print("      • Rewards distributed")
print("      • Plastic collected")
print("      • Marine animals saved")
print("      • List of high risk boats")
print("\n📝 Click on any boat or red zone for details")
print("\n🌊 KadalAI - Track Boats. Catch Dumpers. Reward Cleaners. Save Oceans.")
print("="*60)