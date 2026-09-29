# Nepal & Cross-Border Disaster Tracking Dashboard
#### Video Demo: https://youtu.be/R_y7d0ORZK0
#### Description:

## Motivation & Context
Nepal, nestled in the heart of the Himalayas, is a country of breathtaking beauty but also extreme geographical and climatic volatility. Its location on the boundary of the Indian and Eurasian tectonic plates makes it highly susceptible to devastating earthquakes. Furthermore, the steep topography combined with intense monsoon rains leads to frequent and severe landslides, flash floods, and debris flows. These hazards do not respect national borders; a glacial lake outburst flood (GLOF) in the higher Himalayas or intense localized precipitation can cause devastating downstream flooding in neighboring cross-border basins such as those shared with India. Recent devastating flash floods across the Bhotekoshi river corridor in Rasuwa, inundation along the Bagmati river in the Kathmandu Valley, and recurring monsoon highway blockages along the Mugling-Narayangadh lifeline underscore the urgent need for accessible, real-time hazard tracking.

Given this context, timely information dissemination is a matter of life and death. The "Nepal & Cross-Border Disaster Tracking Dashboard" is conceived to bridge the gap between official sensor telemetry (like seismic arrays and hydrological stations) and on-the-ground reality, which is often first witnessed by local communities. This project serves as a centralized, interactive command center that aggregates real-time instrumental data with crowdsourced community hazard reports. It is designed to aid emergency responders, local authorities, and citizens by providing a unified operational picture of emerging threats.

## System Architecture & Technologies Used
This dashboard is a full-stack web application built using a robust, lightweight, and highly portable technology stack:
- **Backend**: Python with the Flask web framework. Flask was chosen for its simplicity and elegance in setting up robust REST API endpoints and serving dynamic HTML templates.
- **Database**: SQLite3. The standard library `sqlite3` module is utilized to ensure that the application is fully self-contained and portable without the need to install or configure external database engines like PostgreSQL or MySQL.
- **Frontend/UI**: HTML5, CSS3, and JavaScript. The UI is built entirely without heavy frontend frameworks to demonstrate core web development proficiencies, utilizing standard Fetch API for asynchronous communications.
- **Mapping Engine**: Leaflet.js combined with CartoDB dark tiles to provide a modern, highly interactive map interface. Leaflet is lightweight and mobile-friendly, ideal for a dashboard.
- **External APIs**: The dashboard integrates live earthquake data from the USGS (United States Geological Survey) Earthquake Hazards Program API, and hydrological/weather proxy data via the Open-Meteo API.

## File Breakdown and Responsibilities

### 1. `app.py`
This is the heart of the backend application. It serves multiple critical functions:
- **Application Setup**: Initializes the Flask application and configures basic parameters.
- **Database Initialization (`init_db`)**: On startup, it checks if `disaster.db` exists. If not, it creates the database and the `reports` table. Crucially, if the table is empty, it seeds the database with five realistic records representing diverse hazards (floods, landslides, earthquakes) across key locations in Nepal. This ensures the dashboard is visually populated and functional immediately upon first deployment.
- **Route Definitions**:
  - `GET /`: The main entry point. It queries the SQLite database to compute summary statistics (total reports, number of critical alerts) and renders `index.html`.
  - `GET /api/reports`: Fetches all community reports from the SQLite database, formats them as a list of dictionaries, and returns them as a JSON payload for the frontend to render.
  - `POST /api/reports`: Handles incoming form submissions for new hazard reports. It extracts form data, performs basic validation, and inserts a new record into the `reports` table.
  - `POST /api/reports/<id>/upvote`: A custom endpoint to increment the 'upvote' counter of a specific report, implementing a crowd-verification mechanism where users can validate the authenticity of a community report.
  - `GET /api/live-feeds`: Acts as a backend proxy to fetch live data from USGS and Open-Meteo. It includes `try-except` blocks to provide graceful fallback data (offline stubs) ensuring the dashboard never crashes during a demo if external network connectivity drops.

### 2. `disaster.db` & Database Schema Design
The SQLite database consists of a single, comprehensive table named `reports`. The schema choices are deliberate:
- `id`: INTEGER PRIMARY KEY AUTOINCREMENT. Ensures a unique identifier for every report.
- `title`, `description`, `reporter_name`: TEXT fields for capturing the narrative context of the hazard.
- `category` & `severity`: TEXT fields constrained by the frontend application logic (e.g., Flood, Landslide; Critical, High, Moderate).
- `location_name`: TEXT for a human-readable location.
- `latitude` & `longitude`: REAL (floating-point) fields crucial for accurate geospatial plotting on the Leaflet map.
- `upvotes`: INTEGER with a default of 1. Used for community verification.
- `timestamp`: DATETIME defaulting to CURRENT_TIMESTAMP to automatically track exactly when a report was submitted.

### 3. `templates/index.html`
This file contains the core HTML structure of the dashboard. It is designed using a modern grid layout, broken down into three main sections:
- **Header**: Displays the application title and dynamic summary statistics passed down from Flask via Jinja2 templating.
- **Sidebar (Left)**: Contains the interactive controls. This includes a text search bar, category filter buttons, and the comprehensive "Report a Hazard" form. The form is designed with user experience in mind, including a helper text indicating that clicking on the map will auto-fill coordinates.
- **Map Container (Center)**: The div where Leaflet.js renders the interactive map.
- **Feed Sidebar (Right)**: A dynamically populated feed of "Recent Incidents" that mirrors the data shown on the map but in a readable, scrollable list format.

### 4. `static/style.css`
The stylesheet implements a modern, dark-themed "command-center" aesthetic (slate/dark-navy palette) using CSS Variables (`:root`) for consistent color management. Key design choices include:
- **Flexbox and CSS Grid**: Used extensively to create a responsive, fluid layout that maximizes map visibility while keeping controls accessible.
- **Glassmorphism/Modern UI**: Features subtle borders, hover effects with slight translations (`transform: translateY(-2px)`), and glowing drop shadows for critical alerts.
- **Color Coding**: Severity levels (Critical, High, Moderate) are strictly color-coded across the application (red, amber, blue) on both map markers and feed badges for immediate visual recognition.

### 5. `static/script.js`
This file handles all frontend interactivity and asynchronous communication with the Flask backend. 
- **Map Initialization**: Sets up the Leaflet map, configures the CartoDB dark tiles, and creates distinct Layer Groups for Earthquakes, Hydrology, and Community Reports. This layered approach allows users to toggle specific data types on and off.
- **Map Click Event**: Implements a crucial UX feature—when a user clicks anywhere on the Leaflet map, an event listener extracts the `latlng` and auto-populates the hidden latitude/longitude fields in the submission form.
- **Asynchronous Data Fetching**: Utilizes the modern `fetch`/`await` API to pull data from `/api/reports` and `/api/live-feeds`.
- **Dynamic Rendering**: Iterates through JSON payloads to create Leaflet `L.circleMarker` objects and inject HTML fragments into the Incident Feed sidebar.
- **Client-Side Filtering**: The search bar and filter buttons do not query the backend; instead, they filter a cached array of JSON data (`communityDataCache`) and trigger re-renders of the map markers and feed, resulting in an ultra-fast, snappy user experience.

### 6. `requirements.txt`
A simple text file listing the Python dependencies (`Flask` and `requests`) required to run the application, ensuring reproducibility across different environments.

## Conclusion and AI Policy Statement
This dashboard represents a comprehensive integration of web technologies to solve a real-world problem. By combining server-side routing, database management, external API integration, and interactive geospatial frontend scripting, it fulfills all requirements of a full-stack web application.

*CS50x Final Project - Developed by Surup Rajbhandari (Kathmandu, Nepal). Built with assistance from Antigravity IDE / AI tools for UI scaffolding and route structuring, in accordance with CS50x Final Project AI policy.*
