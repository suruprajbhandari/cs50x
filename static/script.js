// CS50x Final Project - Developed by Surup Rajbhandari (Kathmandu, Nepal). Built with assistance from Antigravity IDE / AI tools for UI scaffolding and route structuring, in accordance with CS50x Final Project AI policy.

let map;
let layerGroups = {
    earthquakes: L.layerGroup(),
    hydro: L.layerGroup(),
    community: L.layerGroup()
};
let currentFilter = 'all';
let searchKeyword = '';
let communityDataCache = [];

// Initialize Map
function initMap() {
    // Centered on Nepal
    map = L.map('map').setView([28.3949, 84.1240], 7);

    // Standard OSM Tiles (Inverted via CSS for dark mode)
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors',
        maxZoom: 20
    }).addTo(map);

    // Add layer groups to map
    layerGroups.earthquakes.addTo(map);
    layerGroups.hydro.addTo(map);
    layerGroups.community.addTo(map);

    // Map click event for coordinate selection
    map.on('click', function(e) {
        document.getElementById('latitude').value = e.latlng.lat.toFixed(6);
        document.getElementById('longitude').value = e.latlng.lng.toFixed(6);
        // Highlight form momentarily
        const form = document.getElementById('report-form');
        form.style.boxShadow = '0 0 15px rgba(56, 189, 248, 0.5)';
        setTimeout(() => form.style.boxShadow = 'none', 1000);
    });
}

// Fetch Community Reports
async function fetchCommunityReports() {
    try {
        const response = await fetch('/api/reports');
        const reports = await response.json();
        communityDataCache = reports;
        renderCommunityData();
        renderIncidentFeed();
    } catch (error) {
        console.error("Error fetching reports:", error);
    }
}

// Fetch Live Feeds (USGS & Open-Meteo)
async function fetchLiveFeeds() {
    try {
        const response = await fetch('/api/live-feeds');
        const data = await response.json();
        
        renderEarthquakes(data.earthquakes);
        renderHydrology(data.hydrology);
        
        const badge = document.getElementById('api-status');
        if (badge) {
            badge.textContent = 'Connected';
            badge.style.color = '#10b981';
        }
    } catch (error) {
        console.error("Error fetching live feeds:", error);
        const badge = document.getElementById('api-status');
        if (badge) {
            badge.textContent = 'Error';
            badge.style.color = '#ef4444';
        }
    }
}

// Render Earthquake Markers
function renderEarthquakes(geojsonData) {
    layerGroups.earthquakes.clearLayers();
    
    if (geojsonData && geojsonData.features) {
        geojsonData.features.forEach(feature => {
            const coords = feature.geometry.coordinates; // [lng, lat, depth]
            const props = feature.properties;
            
            // Size by magnitude
            const radius = props.mag * 3;
            
            const marker = L.circleMarker([coords[1], coords[0]], {
                radius: radius,
                fillColor: '#ef4444',
                color: '#7f1d1d',
                weight: 1,
                opacity: 1,
                fillOpacity: 0.6
            });
            
            const time = new Date(props.time).toLocaleString();
            marker.bindPopup(`
                <strong>Live Earthquake Alert</strong><br>
                Magnitude: ${props.mag}<br>
                Location: ${props.place}<br>
                Time: ${time}
            `);
            
            layerGroups.earthquakes.addLayer(marker);
        });
    }
}

// Render Hydrology Markers
function renderHydrology(hydroData) {
    layerGroups.hydro.clearLayers();
    
    if (hydroData) {
        hydroData.forEach(site => {
            const marker = L.circleMarker([site.latitude, site.longitude], {
                radius: 8,
                fillColor: '#38bdf8',
                color: '#0284c7',
                weight: 2,
                opacity: 1,
                fillOpacity: 0.8
            });
            
            marker.bindPopup(`
                <strong>Hydrology / Weather Station</strong><br>
                Location: ${site.location}<br>
                Precipitation: ${site.precipitation} mm<br>
                Rain: ${site.rain} mm<br>
                Wind: ${site.windspeed} km/h
            `);
            
            layerGroups.hydro.addLayer(marker);
        });
    }
}

// Render Community Data Markers
function renderCommunityData() {
    layerGroups.community.clearLayers();
    
    let filteredData = communityDataCache;
    
    // Apply search filter if active
    if (searchKeyword) {
        const lowerKeyword = searchKeyword.toLowerCase();
        filteredData = filteredData.filter(item => 
            item.location_name.toLowerCase().includes(lowerKeyword) || 
            item.title.toLowerCase().includes(lowerKeyword) ||
            item.description.toLowerCase().includes(lowerKeyword)
        );
    }

    filteredData.forEach(report => {
        let color = '#38bdf8'; // Moderate / Default
        if (report.severity === 'Critical') color = '#ef4444';
        else if (report.severity === 'High') color = '#f59e0b';
        
        const marker = L.circleMarker([report.latitude, report.longitude], {
            radius: 10,
            fillColor: color,
            color: '#fff',
            weight: 1,
            opacity: 1,
            fillOpacity: 0.9
        });
        
        marker.bindPopup(`
            <strong>${report.title}</strong><br>
            Category: ${report.category}<br>
            Severity: ${report.severity}<br>
            Location: ${report.location_name}<br>
            Reported by: ${report.reporter_name}
        `);
        
        layerGroups.community.addLayer(marker);
    });
}

// Render Incident Feed Sidebar
function renderIncidentFeed() {
    const feedContainer = document.getElementById('incident-feed');
    feedContainer.innerHTML = '';
    
    let filteredData = communityDataCache;
    
    if (searchKeyword) {
        const lowerKeyword = searchKeyword.toLowerCase();
        filteredData = filteredData.filter(item => 
            item.location_name.toLowerCase().includes(lowerKeyword) || 
            item.title.toLowerCase().includes(lowerKeyword) ||
            item.description.toLowerCase().includes(lowerKeyword)
        );
    }

    filteredData.forEach(report => {
        const severityClass = report.severity.toLowerCase();
        
        const card = document.createElement('div');
        card.className = 'incident-card';
        card.innerHTML = `
            <div class="incident-header">
                <div class="incident-title">${report.title}</div>
                <span class="badge ${severityClass}">${report.severity}</span>
            </div>
            <div class="incident-location">📍 ${report.location_name}</div>
            <div class="incident-desc">${report.description}</div>
            <div class="incident-footer">
                <span class="reporter">👤 ${report.reporter_name} • ${new Date(report.timestamp).toLocaleDateString()}</span>
                <button class="upvote-btn" onclick="upvoteReport(${report.id})">👍 Verify (<span id="upvotes-${report.id}">${report.upvotes}</span>)</button>
            </div>
        `;
        feedContainer.appendChild(card);
    });
}

// Upvote Report API Call
async function upvoteReport(id) {
    try {
        const response = await fetch(`/api/reports/${id}/upvote`, {
            method: 'POST'
        });
        const result = await response.json();
        
        if (result.success) {
            document.getElementById(`upvotes-${id}`).textContent = result.upvotes;
            // Update cache silently
            const report = communityDataCache.find(r => r.id === id);
            if (report) report.upvotes = result.upvotes;
        }
    } catch (error) {
        console.error("Error upvoting:", error);
    }
}

// Setup Event Listeners
function setupEventListeners() {
    // Form Submission
    document.getElementById('report-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = {
            title: document.getElementById('title').value,
            category: document.getElementById('category').value,
            severity: document.getElementById('severity').value,
            location_name: document.getElementById('location_name').value,
            latitude: document.getElementById('latitude').value,
            longitude: document.getElementById('longitude').value,
            description: document.getElementById('description').value,
            reporter_name: document.getElementById('reporter_name').value
        };
        
        try {
            const response = await fetch('/api/reports', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });
            
            if (response.ok) {
                alert("Report submitted successfully!");
                document.getElementById('report-form').reset();
                fetchCommunityReports(); // Refresh data
            } else {
                alert("Error submitting report.");
            }
        } catch (error) {
            console.error("Error:", error);
            alert("Connection error.");
        }
    });

    // Filtering
    const filterBtns = document.querySelectorAll('.filter-btn');
    filterBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            // Update active state
            filterBtns.forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            
            const filter = e.target.dataset.filter;
            currentFilter = filter;
            
            // Toggle layers
            if (filter === 'all') {
                map.addLayer(layerGroups.earthquakes);
                map.addLayer(layerGroups.hydro);
                map.addLayer(layerGroups.community);
            } else if (filter === 'earthquakes') {
                map.addLayer(layerGroups.earthquakes);
                map.removeLayer(layerGroups.hydro);
                map.removeLayer(layerGroups.community);
            } else if (filter === 'hydro') {
                map.removeLayer(layerGroups.earthquakes);
                map.addLayer(layerGroups.hydro);
                map.removeLayer(layerGroups.community);
            } else if (filter === 'community') {
                map.removeLayer(layerGroups.earthquakes);
                map.removeLayer(layerGroups.hydro);
                map.addLayer(layerGroups.community);
            }
        });
    });

    // Search
    document.getElementById('search-input').addEventListener('input', (e) => {
        searchKeyword = e.target.value;
        renderCommunityData();
        renderIncidentFeed();
    });
}

// Initialization
document.addEventListener('DOMContentLoaded', () => {
    initMap();
    setupEventListeners();
    
    // Initial fetch
    fetchCommunityReports();
    fetchLiveFeeds();
    
    // Polling for live feeds every 5 minutes
    setInterval(fetchLiveFeeds, 300000);
});
