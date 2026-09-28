# How to run:
# streamlit run app.py

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
st.caption("Map and dataset visualization for coastal infrastructure in Odisha")

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
# Folium Map Setup
# ---------------------------------------------------------
# Map centered on Odisha coast (lat 19.5, lon 85.5, zoom 7)
m = folium.Map(location=[19.5, 85.5], zoom_start=7, tiles="OpenStreetMap")

color_map = {
    "hospital": "red",
    "shelter": "green",
    "road": "blue",
    "power_station": "purple"
}

for _, row in df_assets.iterrows():
    popup_text = f"""
    <b>{row['name']}</b><br>
    ID: {row['id']}<br>
    Type: {row['type']}<br>
    Elevation: {row['elevation_m']} m<br>
    Importance: {row['importance']}/5<br>
    Capacity: {row['capacity']}
    """
    
    folium.Marker(
        location=[row["lat"], row["lon"]],
        popup=folium.Popup(popup_text, max_width=250),
        tooltip=f"{row['name']} ({row['type']})",
        icon=folium.Icon(
            color=color_map.get(row["type"], "gray"),
            icon="info-sign"
        )
    ).add_to(m)

# Render map in Streamlit
st_folium(m, width="100%", height=500)

# ---------------------------------------------------------
# Asset Data Table
# ---------------------------------------------------------
st.subheader("Infrastructure Assets Table")
st.dataframe(df_assets, use_container_width=True)
