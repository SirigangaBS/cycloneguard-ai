import math
import random
import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# ---------------------------------------------------------
# Haversine distance calculation
# ---------------------------------------------------------
def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371.0  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def get_wind_hazard(wind_speed):
    if wind_speed < 63:
        return 0  # LOW
    elif 63 <= wind_speed < 118:
        return 1  # MEDIUM
    elif 118 <= wind_speed < 167:
        return 2  # HIGH
    else:
        return 3  # CRITICAL

def get_flood_hazard(elevation, rainfall):
    if elevation < 5 and rainfall > 10:
        return 2  # HIGH
    elif elevation < 10 and rainfall > 5:
        return 1  # MEDIUM
    else:
        return 0  # LOW

ORDINAL_TO_HAZARD = {0: "LOW", 1: "MEDIUM", 2: "HIGH", 3: "CRITICAL"}

# ---------------------------------------------------------
# Generate Synthetic Dataset (1000 samples for robust AI training)
# ---------------------------------------------------------
np.random.seed(42)
random.seed(42)

types = ["hospital", "shelter", "road", "power_station"]
rows = []

# Generate multiple cyclone scenarios
scenarios = [
    {"lat": 19.0, "lon": 86.0, "max_wind": 150, "rainfall": 12},
    {"lat": 19.8, "lon": 85.2, "max_wind": 180, "rainfall": 15},
    {"lat": 18.5, "lon": 84.8, "max_wind": 130, "rainfall": 8},
    {"lat": 20.1, "lon": 86.5, "max_wind": 165, "rainfall": 20},
    {"lat": 19.2, "lon": 85.8, "max_wind": 110, "rainfall": 6},
]

for i in range(1000):
    scen = random.choice(scenarios)
    asset_type = random.choice(types)
    lat = 19.5 + random.uniform(-1.2, 1.2)
    lon = 85.5 + random.uniform(-1.2, 1.2)
    elevation = round(random.uniform(1.0, 40.0), 1)
    importance = random.randint(1, 5)
    capacity = random.randint(100, 5000)

    dist = haversine_distance(lat, lon, scen["lat"], scen["lon"])
    wind = scen["max_wind"] * math.exp(-dist / 150.0)

    w_hazard = get_wind_hazard(wind)
    f_hazard = get_flood_hazard(elevation, scen["rainfall"])
    comb_hazard = max(w_hazard, f_hazard)

    # High risk target: 1 if comb_hazard is HIGH (2) or CRITICAL (3), else 0
    high_risk = 1 if comb_hazard >= 2 else 0

    # 10% random label flip for realistic noise
    if random.random() < 0.10:
        high_risk = 1 - high_risk

    rows.append({
        "id": f"AST-{i+1:04d}",
        "type": asset_type,
        "lat": lat,
        "lon": lon,
        "elevation_m": elevation,
        "importance": importance,
        "capacity": capacity,
        "cyclone_lat": scen["lat"],
        "cyclone_lon": scen["lon"],
        "max_wind_kmh": scen["max_wind"],
        "rainfall_mm_h": scen["rainfall"],
        "distance_to_cyclone_km": dist,
        "wind_speed": wind,
        "wind_hazard": w_hazard,
        "flood_hazard": f_hazard,
        "rule_based_risk": comb_hazard,
        "high_risk": high_risk
    })

df = pd.DataFrame(rows)

# ---------------------------------------------------------
# Feature Engineering (One-Hot Encoding & Alignment)
# ---------------------------------------------------------
# One-hot encode asset_type explicitly
for t in ["hospital", "shelter", "road", "power_station"]:
    df[f"type_{t}"] = (df["type"] == t).astype(int)

feature_cols = [
    "wind_speed",
    "rainfall_mm_h",
    "elevation_m",
    "distance_to_cyclone_km",
    "type_hospital",
    "type_shelter",
    "type_road",
    "type_power_station",
    "importance",
    "rule_based_risk"
]

X = df[feature_cols]
y = df["high_risk"]

# ---------------------------------------------------------
# Train / Test Split & Model Training
# ---------------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42, stratify=y)

model = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
model.fit(X_train, y_train)

# ---------------------------------------------------------
# Model Evaluation
# ---------------------------------------------------------
y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
prec = precision_score(y_test, y_pred)
rec = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)

print(f"--- Model Performance ---")
print(f"Accuracy:  {acc:.4f}")
print(f"Precision: {prec:.4f}")
print(f"Recall:    {rec:.4f}")
print(f"F1-Score:  {f1:.4f}")

# ---------------------------------------------------------
# Save Model to Project Root
# ---------------------------------------------------------
model_path = os.path.join("..", "risk_model.pkl") if os.path.exists("..") and os.path.basename(os.getcwd()) == "notebooks" else "risk_model.pkl"
joblib.dump(model, model_path)
print(f"Model saved successfully to {os.path.abspath(model_path)}")
