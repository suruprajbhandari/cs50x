# CS50x Final Project - Developed by Surup Rajbhandari (Kathmandu, Nepal). Built with assistance from Antigravity IDE / AI tools for UI scaffolding and route structuring, in accordance with CS50x Final Project AI policy.

import sqlite3
import datetime
from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)
DB_NAME = 'disaster.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            category TEXT,
            severity TEXT,
            location_name TEXT,
            latitude REAL,
            longitude REAL,
            description TEXT,
            reporter_name TEXT,
            upvotes INTEGER DEFAULT 1,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Check if table is empty
    c.execute('SELECT COUNT(*) FROM reports')
    count = c.fetchone()[0]
    
    if count == 0:
        # Seed initial data
        seeds = [
            ("Bhotekoshi / Rasuwa Flash Flood Watch", "Flood", "Critical", "Bhotekoshi River", 27.9405, 85.8903, "High water level observed after heavy rainfall in the catchment area. Residents advised to stay alert.", "System Admin"),
            ("Mugling-Narayangadh Highway Landslide Alert", "Landslide", "High", "Mugling", 27.8504, 84.5501, "Minor landslide blocking one lane. Authorities are clearing the debris.", "Traffic Police"),
            ("Kathmandu Valley Seismic Sensor Check", "Earthquake", "Moderate", "Kathmandu", 27.7172, 85.3240, "Routine sensor check triggered a moderate alert. No actual shaking felt.", "Seismic Center"),
            ("Koshi Barrage High Water Level", "Flood", "High", "Koshi Barrage", 26.5239, 86.9272, "Water level approaching warning mark. All sluice gates are being monitored.", "Water Authority"),
            ("Pokhara Heavy Monsoon Advisory", "Flood", "Moderate", "Pokhara", 28.2096, 83.9856, "Heavy continuous rainfall expected for the next 24 hours. Possibility of localized waterlogging.", "Met Dept")
        ]
        
        c.executemany('''
            INSERT INTO reports (title, category, severity, location_name, latitude, longitude, description, reporter_name)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', seeds)
        
    conn.commit()
    conn.close()

# Initialize DB on startup
init_db()

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM reports')
    total_reports = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM reports WHERE severity = 'Critical'")
    critical_alerts = c.fetchone()[0]
    conn.close()
    
    return render_template('index.html', total_reports=total_reports, critical_alerts=critical_alerts)

@app.route('/api/reports', methods=['GET'])
def get_reports():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM reports ORDER BY timestamp DESC')
    reports = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(reports)

@app.route('/api/reports', methods=['POST'])
def add_report():
    data = request.json
    try:
        title = data['title']
        category = data['category']
        severity = data['severity']
        location_name = data['location_name']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        description = data['description']
        reporter_name = data['reporter_name']
        
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('''
            INSERT INTO reports (title, category, severity, location_name, latitude, longitude, description, reporter_name)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (title, category, severity, location_name, latitude, longitude, description, reporter_name))
        conn.commit()
        report_id = c.lastrowid
        conn.close()
        
        return jsonify({'success': True, 'id': report_id}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/reports/<int:report_id>/upvote', methods=['POST'])
def upvote_report(report_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('UPDATE reports SET upvotes = upvotes + 1 WHERE id = ?', (report_id,))
    conn.commit()
    
    c.execute('SELECT upvotes FROM reports WHERE id = ?', (report_id,))
    row = c.fetchone()
    conn.close()
    
    if row:
        return jsonify({'success': True, 'upvotes': row['upvotes']})
    else:
        return jsonify({'success': False, 'error': 'Report not found'}), 404

@app.route('/api/live-feeds', methods=['GET'])
def get_live_feeds():
    headers = {"User-Agent": "CS50x-DisasterTracker/1.0 (suruprajbhandari)"}
    
    # 1. USGS Earthquake Data
    try:
        past_180 = (datetime.datetime.now() - datetime.timedelta(days=180)).strftime('%Y-%m-%d')
        usgs_url = f'https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime={past_180}&minlatitude=20.0&maxlatitude=35.0&minlongitude=75.0&maxlongitude=95.0&minmagnitude=2.5&limit=30'
        usgs_response = requests.get(usgs_url, headers=headers, timeout=8)
        usgs_data = usgs_response.json()
        
        # If API returned 0 results, trigger fallback
        if not usgs_data.get("features"):
            raise ValueError("No USGS features found")
            
    except Exception:
        # Fallback 6 seismic events
        usgs_data = {
            "type": "FeatureCollection",
            "features": [
                {"type": "Feature", "properties": {"mag": 4.5, "place": "Offline Fallback: 20km N of Kathmandu, Nepal", "time": int(datetime.datetime.now().timestamp() * 1000)}, "geometry": {"type": "Point", "coordinates": [85.3240, 27.9172, 10.0]}},
                {"type": "Feature", "properties": {"mag": 5.1, "place": "Offline Fallback: 15km SE of Pokhara, Nepal", "time": int(datetime.datetime.now().timestamp() * 1000)}, "geometry": {"type": "Point", "coordinates": [84.1556, 28.1130, 15.0]}},
                {"type": "Feature", "properties": {"mag": 3.8, "place": "Offline Fallback: 10km W of Namche Bazaar, Nepal", "time": int(datetime.datetime.now().timestamp() * 1000)}, "geometry": {"type": "Point", "coordinates": [86.6111, 27.8069, 5.0]}},
                {"type": "Feature", "properties": {"mag": 6.0, "place": "Offline Fallback: 50km NE of Gorkha, Nepal", "time": int(datetime.datetime.now().timestamp() * 1000)}, "geometry": {"type": "Point", "coordinates": [84.6298, 28.3949, 12.0]}},
                {"type": "Feature", "properties": {"mag": 4.2, "place": "Offline Fallback: 25km S of Dharan, Nepal", "time": int(datetime.datetime.now().timestamp() * 1000)}, "geometry": {"type": "Point", "coordinates": [87.2764, 26.8125, 8.0]}},
                {"type": "Feature", "properties": {"mag": 3.5, "place": "Offline Fallback: 5km E of Jomsom, Nepal", "time": int(datetime.datetime.now().timestamp() * 1000)}, "geometry": {"type": "Point", "coordinates": [83.7400, 28.7846, 18.0]}},
            ]
        }
        
    # 2. Open-Meteo Data for key river basins
    try:
        meteo_url = 'https://api.open-meteo.com/v1/forecast?latitude=27.71,28.21,27.98,26.81&longitude=85.32,83.99,85.42,87.28&current=precipitation,rain,weather_code,wind_speed_10m'
        meteo_response = requests.get(meteo_url, headers=headers, timeout=8)
        meteo_data_raw = meteo_response.json()
        
        locations = ["Kathmandu Basin", "Pokhara Basin", "Rasuwa/Bhotekoshi", "Koshi/Dharan"]
        hydro_data = []
        
        if not isinstance(meteo_data_raw, list):
            raise ValueError("Unexpected Open-Meteo format")
            
        for i, data in enumerate(meteo_data_raw):
            if isinstance(data, dict) and "current" in data:
                hydro_data.append({
                    "location": locations[i],
                    "latitude": data["latitude"],
                    "longitude": data["longitude"],
                    "precipitation": data["current"]["precipitation"],
                    "rain": data["current"]["rain"],
                    "windspeed": data["current"]["wind_speed_10m"],
                    "time": data["current"]["time"]
                })
        
        if not hydro_data:
             raise ValueError("No hydrology data parsed")
             
    except Exception:
        # Fallback 5 river stations
        hydro_data = [
            {"location": "Offline Fallback: Kathmandu Basin", "latitude": 27.71, "longitude": 85.32, "precipitation": 12.5, "rain": 10.0, "windspeed": 5.0, "time": "Live"},
            {"location": "Offline Fallback: Pokhara Basin", "latitude": 28.21, "longitude": 83.99, "precipitation": 45.0, "rain": 40.0, "windspeed": 12.0, "time": "Live"},
            {"location": "Offline Fallback: Rasuwa/Bhotekoshi", "latitude": 27.98, "longitude": 85.42, "precipitation": 5.0, "rain": 5.0, "windspeed": 8.0, "time": "Live"},
            {"location": "Offline Fallback: Koshi/Dharan", "latitude": 26.81, "longitude": 87.28, "precipitation": 0.0, "rain": 0.0, "windspeed": 3.0, "time": "Live"},
            {"location": "Offline Fallback: Karnali River", "latitude": 29.0, "longitude": 81.5, "precipitation": 2.0, "rain": 1.5, "windspeed": 6.5, "time": "Live"}
        ]
        
    return jsonify({
        "earthquakes": usgs_data,
        "hydrology": hydro_data
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
