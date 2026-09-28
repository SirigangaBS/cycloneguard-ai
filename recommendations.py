"""
recommendations.py
Module to generate actionable emergency recommendations for infrastructure assets 
based on asset type, AI predicted risk level, and hazard risk factors.
"""

def get_recommendations(asset_type: str, ai_risk_category: str, risk_factors: dict = None) -> str:
    """
    Returns 1-2 concise, actionable recommendations based on asset type and risk level.
    """
    asset_type = str(asset_type).lower()
    ai_risk_category = str(ai_risk_category).upper()
    
    if risk_factors is None:
        risk_factors = {}

    wind_hazard = risk_factors.get("wind_hazard", "LOW")
    flood_hazard = risk_factors.get("flood_hazard", "LOW")

    if ai_risk_category == "HIGH" or ai_risk_category == "CRITICAL":
        if asset_type == "hospital":
            if flood_hazard in ["HIGH", "CRITICAL"]:
                return "Prepare backup power; relocate ICU patients to upper floors and secure emergency medical supplies."
            return "Prepare generators and stock emergency oxygen; mobilize extra trauma staff."

        elif asset_type == "shelter":
            if flood_hazard in ["HIGH", "CRITICAL"]:
                return "Elevate ground supplies; inspect roof waterproofing and activate emergency water filtration."
            return "Verify capacity limits, restock emergency rations, and establish satellite communications."

        elif asset_type == "road":
            if flood_hazard in ["HIGH", "CRITICAL"]:
                return "Deploy flood barriers; identify alternate evacuation routes and pre-position clearing crews."
            return "Clear roadside drainage channels and place high-wind warning advisories."

        elif asset_type == "power_station":
            if flood_hazard in ["HIGH", "CRITICAL"]:
                return "Deploy submersible pumps around transformer yards; prepare remote grid islanding."
            return "Conduct emergency structural checks; initiate controlled load shedding if wind exceeds safety limits."

        else:
            return "Deploy rapid response team; conduct immediate safety and operational check."

    elif ai_risk_category == "MEDIUM":
        if asset_type == "hospital":
            return "Check generator fuel levels and verify emergency comms link with local control centers."
        elif asset_type == "shelter":
            return "Mark facility ready as secondary evacuation shelter; check food and medical kits."
        elif asset_type == "road":
            return "Monitor traffic density along evacuation corridor; stage tow vehicles."
        elif asset_type == "power_station":
            return "Inspect feeder lines and maintain backup power readiness for adjacent shelters."
        else:
            return "Monitor weather updates and inspect primary control systems."

    else:  # LOW risk
        if asset_type == "shelter":
            return "Designate facility as primary safe evacuation center."
        elif asset_type == "hospital":
            return "Maintain standard operational readiness to receive transfers from vulnerable zones."
        elif asset_type == "road":
            return "Maintain open traffic flow for primary evacuation routes."
        elif asset_type == "power_station":
            return "Maintain standard grid output to support critical coastal facilities."
        else:
            return "Standard operational status; monitor regional storm progress."
