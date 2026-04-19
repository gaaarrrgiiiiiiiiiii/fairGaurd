from fastapi import APIRouter
import sqlite3
import json
from scipy.stats import ks_2samp
from app.models.database import DATABASE_URL

router = APIRouter()

@router.get("/status")
async def check_drift(tenant_id: str = "tenant_local_dev"):
    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
    # Fetch recent model confidences
    c.execute('SELECT original_decision FROM audit_logs WHERE tenant_id = ? ORDER BY timestamp DESC LIMIT 100', (tenant_id,))
    rows = c.fetchall()
    conn.close()
    
    if not rows or len(rows) < 10:
        return {
            "drift_detected": False,
            "p_value": 1.0,
            "message": "Insufficient data to perform KS test (need at least 10 records)."
        }
        
    recent_confidences = []
    for r in rows:
        try:
            decision_dict = json.loads(r[0])
            conf = decision_dict.get("confidence")
            if conf is not None:
                recent_confidences.append(float(conf))
        except:
            continue
            
    if len(recent_confidences) < 10:
        return {
            "drift_detected": False,
            "p_value": 1.0,
            "message": "Insufficient confidence scores parsed from audit logs."
        }
        
    # Mock reference distribution (e.g., from validation set during training)
    # Ideally, this would be computed from prep_adult_data and stored, but we approximate
    # a healthy distribution centered around 0.82 for approved and 0.70 for denied.
    import numpy as np
    np.random.seed(42)
    reference_distribution = np.concatenate([
        np.random.normal(0.85, 0.05, 50),
        np.random.normal(0.72, 0.05, 50)
    ]).tolist()
    
    # Perform Kolmogorov-Smirnov test for goodness of fit
    statistic, p_value = ks_2samp(recent_confidences, reference_distribution)
    
    # A p-value < 0.05 indicates the distributions are significantly different (drift occurred)
    drift_detected = bool(p_value < 0.05)
    
    return {
        "drift_detected": drift_detected,
        "ks_statistic": round(float(statistic), 4),
        "p_value": round(float(p_value), 4),
        "message": "Significant model drift detected!" if drift_detected else "Model output distribution is stable."
    }
