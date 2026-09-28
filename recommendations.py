"""
recommendations.py
Generates specific emergency recommendations based on asset type and AI predicted risk level.
"""

def get_recommendations(asset_type: str, ai_risk_category: str, risk_factors: list = None) -> list:
    """
    Returns a list of 1-2 recommendation strings based on asset type and risk category.
    """
    asset_type = str(asset_type).lower().strip()
    ai_risk_category = str(ai_risk_category).upper().strip()

    if asset_type == 'hospital':
        if ai_risk_category == 'HIGH':
            return [
                'Prepare backup power and generators.',
                'Move critical patients to upper floors; secure medical equipment.'
            ]
        else:
            return ['Monitor situation; ensure emergency protocols are ready.']

    elif asset_type == 'road':
        if ai_risk_category == 'HIGH':
            return [
                'Identify alternate routes for emergency vehicles.',
                'Pre-position repair crews and equipment.'
            ]
        else:
            return ['Keep under observation; prepare for rapid closure if needed.']

    elif asset_type == 'shelter':
        if ai_risk_category in ['LOW', 'MEDIUM']:
            return ['Mark as suitable evacuation center; verify capacity and access.']
        else:
            return ['Do not use as primary shelter; identify alternative safe locations.']

    elif asset_type == 'power_station':
        if ai_risk_category == 'HIGH':
            return [
                'Conduct emergency inspection; secure critical equipment.',
                'Prepare backup power arrangements for nearby hospitals.'
            ]
        else:
            return ['Ensure standby teams are ready; monitor grid stability.']

    else:
        if ai_risk_category == 'HIGH':
            return ['Deploy rapid response team; conduct immediate safety check.']
        else:
            return ['Monitor weather updates and maintain standard protocols.']
