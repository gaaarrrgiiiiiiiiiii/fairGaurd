import datetime
import uuid
import json
import sqlite3

DATABASE_URL = "./fairguard.db"

def init_db():
    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS audit_logs (
            id TEXT PRIMARY KEY,
            tenant_id TEXT,
            timestamp TEXT,
            original_decision TEXT,
            corrected_decision TEXT,
            bias_scores TEXT,
            explanation TEXT,
            protected_attributes TEXT
        )
    ''')
    conn.commit()
    conn.close()

def create_audit_log(
    tenant_id: str, 
    original_decision: dict, 
    corrected_decision: dict, 
    bias_scores: dict, 
    explanation: str, 
    protected_attributes: list
) -> str:
    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
    audit_id = str(uuid.uuid4())
    now = datetime.datetime.utcnow().isoformat()
    
    c.execute('''
        INSERT INTO audit_logs (id, tenant_id, timestamp, original_decision, corrected_decision, bias_scores, explanation, protected_attributes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        audit_id, 
        tenant_id, 
        now, 
        json.dumps(original_decision), 
        json.dumps(corrected_decision), 
        json.dumps(bias_scores), 
        explanation, 
        json.dumps(protected_attributes)
    ))
    conn.commit()
    conn.close()
    return audit_id

def get_tenant_analytics(tenant_id: str) -> dict:
    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM audit_logs WHERE tenant_id = ?', (tenant_id,))
    total_decisions = c.fetchone()[0]
    
    # Simple intervention heuristic: if explanation is present, an intervention occurred.
    c.execute('SELECT COUNT(*) FROM audit_logs WHERE tenant_id = ? AND explanation IS NOT NULL', (tenant_id,))
    interventions = c.fetchone()[0]
    
    conn.close()
    compliance_rate = 100.0 if total_decisions == 0 else round(100.0 * (total_decisions - interventions) / total_decisions, 2)
    
    return {
        "total_decisions": total_decisions,
        "interventions": interventions,
        "compliance_rate": compliance_rate
    }
