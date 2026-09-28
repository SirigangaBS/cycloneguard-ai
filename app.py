# How to run:
# streamlit run app.py

import math
import random
import pandas as pd
import folium
import streamlit as st
from streamlit_folium import st_folium

# ---------------------------------------------------------
# Page Configuration & Sidebar Setup
# ---------------------------------------------------------
st.set_page_config(
    page_title="CycloneGuard AI (Prototype)",
    page_icon="🌪️",
    layout="wide"
)

# Sidebar setup
st.sidebar.title("CycloneGuard AI (Prototype)")
st.sidebar.markdown(
    """
    Predicting cyclone impact on infrastructure to enable 
    proactive risk mitigation and disaster response planning.
    Visualizing assets across vulnerable coastal zones.
    """
)

# Main page title
st.title("Cyclone Infrastructure Risk Prototype")
st.caption("Simulate cyclone scenarios, estimate wind/flood hazards, and compute asset risk.")

# ---------------------------------------------------------
# Synthetic Data Generation (30-40 assets)
# ---------------------------------------------------------
@st.cache_data
def generate_synthetic_assets(num_assets=35):
    random.seed(42)
    center_lat = 19.5
    center_lon = 85.5

    types = ["hospital", "shelter", "road", "power_station"]
    
    name_prefixes = {
        "hospital": ["Central Hospital", "District Clinic", "Emergency Care", "Community Health Center"],
        "shelter": ["Cyclone Relief Shelter", "Community Evacuation Center", "Multi-purpose Shelter", "School Relief Center"],
        "road": ["Coastal Highway", "Evacuation Route A", "Main Trunk Road", "Harbor Link Road"],
        "power_station": ["Substation Grid 1", "Thermal Power Node", "Solar Substation", "Regional Transformer"]
    }

    assets = []
    for i in range(1, num_assets + 1):
        asset_type = random.choice(types)
        prefix = random.choice(name_prefixes[asset_type])
        lat = round(center_lat + random.uniform(-0.8, 0.8), 4)
        lon = round(center_lon + random.uniform(-0.8, 0.8), 4)
        elevation = round(random.uniform(1.5, 30.0), 1)
        importance = random.randint(1, 5)
        capacity = random.randint(100, 5000)

        assets.append({
            "id": f"AST-{i:03d}",
            "name": f"{prefix} {i}",
            "type": asset_type,
            "lat": lat,
            "lon": lon,
            "elevation_m": elevation,
            "importance": importance,
            "capacity": capacity
        })

    return pd.DataFrame(assets)

df_assets = generate_synthetic_assets(num_assets=35)

# ---------------------------------------------------------
# Distance & Hazard Calculation Functions
# ---------------------------------------------------------
def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371.0  # Earth radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def get_wind_hazard(wind_speed):
    if wind_speed < 63:
        return "LOW"
    elif 63 <= wind_speed < 118:
        return "MEDIUM"
    elif 118 <= wind_speed < 167:
        return "HIGH"
    else:
        return "CRITICAL"

def get_flood_hazard(elevation, rainfall):
    if elevation < 5 and rainfall > 10:
        return "HIGH"
    elif elevation < 10 and rainfall > 5:
        return "MEDIUM"
    else:
        return "LOW"

HAZARD_ORDINAL = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}
ORDINAL_TO_HAZARD = {0: "LOW", 1: "MEDIUM", 2: "HIGH", 3: "CRITICAL"}

def compute_impact_forecast(df, cyclone_lat, cyclone_lon, max_wind, rainfall):
    results = df.copy()
    distances = []
    winds = []
    wind_hazards = []
    flood_hazards = []
    combined_risks = []

    for _, row in results.iterrows():
        dist = haversine_distance(row["lat"], row["lon"], cyclone_lat, cyclone_lon)
        wind = max_wind * math.exp(-dist / 150.0)
        
        w_hazard = get_wind_hazard(wind)
        f_hazard = get_flood_hazard(row["elevation_m"], rainfall)
        
        comb_val = max(HAZARD_ORDINAL[w_hazard], HAZARD_ORDINAL[f_hazard])
        comb_risk = ORDINAL_TO_HAZARD[comb_val]

        distances.append(round(dist, 1))
        winds.append(round(wind, 1))
        wind_hazards.append(w_hazard)
        flood_hazards.append(f_hazard)
        combined_risks.append(comb_risk)

    results["distance_km"] = distances
    results["estimated_wind_kmh"] = winds
    results["wind_hazard"] = wind_hazards
    results["flood_hazard"] = flood_hazards
    results["rule_based_risk"] = combined_risks
    return results

# ---------------------------------------------------------
# Sidebar Controls & Forecast Scenario
# ---------------------------------------------------------
st.sidebar.subheader("Cyclone Scenario Parameters")
cyclone_lat = 19.0
cyclone_lon = 86.0
max_wind_kmh = 150
rainfall_mm_per_hour = 12

st.sidebar.markdown(
    f"""
    - **Center**: ({cyclone_lat}, {cyclone_lon})
    - **Max Wind**: {max_wind_kmh} km/h
    - **Rainfall**: {rainfall_mm_per_hour} mm/h
    """
)

run_button = st.sidebar.button("Run Impact Forecast", type="primary")

if "forecast_run" not in st.session_state:
    st.session_state["forecast_run"] = False

if run_button:
    st.session_state["forecast_run"] = True

if st.session_state["forecast_run"]:
    df_assets = compute_impact_forecast(
        df_assets, 
        cyclone_lat, 
        cyclone_lon, 
        max_wind_kmh, 
        rainfall_mm_per_hour
    )

# ---------------------------------------------------------
# Folium Map Setup
# ---------------------------------------------------------
m = folium.Map(location=[19.5, 85.5], zoom_start=7, tiles="OpenStreetMap")

risk_color_map = {
    "LOW": "green",
    "MEDIUM": "orange",
    "HIGH": "red",
    "CRITICAL": "darkred"
}

type_color_map = {
    "hospital": "red",
    "shelter": "green",
    "road": "blue",
    "power_station": "purple"
}

# Add Cyclone Eye Marker when forecast is active
if st.session_state["forecast_run"]:
    folium.Marker(
        location=[cyclone_lat, cyclone_lon],
        popup=f"<b>Cyclone Eye</b><br>Lat: {cyclone_lat}, Lon: {cyclone_lon}<br>Wind: {max_wind_kmh} km/h<br>Rain: {rainfall_mm_per_hour} mm/h",
        tooltip="Cyclone Center (Eye)",
        icon=folium.Icon(color="darkred", icon="warning-sign")
    ).add_to(m)

for _, row in df_assets.iterrows():
    if "rule_based_risk" in row:
        color = risk_color_map.get(row["rule_based_risk"], "gray")
        popup_text = f"""
        <b>{row['name']}</b><br>
        ID: {row['id']} | Type: {row['type']}<br>
        Elevation: {row['elevation_m']} m<br>
        Distance to Eye: {row['distance_km']} km<br>
        Estimated Wind: {row['estimated_wind_kmh']} km/h<br>
        Wind Hazard: {row['wind_hazard']}<br>
        Flood Hazard: {row['flood_hazard']}<br>
        <b>Risk: {row['rule_based_risk']}</b>
        """
        tooltip_text = f"{row['name']} | Risk: {row['rule_based_risk']}"
    else:
        color = type_color_map.get(row["type"], "gray")
        popup_text = f"""
        <b>{row['name']}</b><br>
        ID: {row['id']}<br>
        Type: {row['type']}<br>
        Elevation: {row['elevation_m']} m<br>
        Importance: {row['importance']}/5<br>
        Capacity: {row['capacity']}
        """
        tooltip_text = f"{row['name']} ({row['type']})"
    
    folium.Marker(
        location=[row["lat"], row["lon"]],
        popup=folium.Popup(popup_text, max_width=260),
        tooltip=tooltip_text,
        icon=folium.Icon(color=color, icon="info-sign")
    ).add_to(m)

# Render map in Streamlit
st_folium(m, width="100%", height=500)

# ---------------------------------------------------------
# Asset Data Table
# ---------------------------------------------------------
st.subheader("Infrastructure Assets Data")
if st.session_state["forecast_run"]:
    st.success("Impact forecast computed successfully!")

st.dataframe(df_assets)

