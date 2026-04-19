import asyncio
import time
from fastapi import APIRouter, Security, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.models.schemas import DecisionRequest, DecisionResponse
from app.models.database import create_audit_log
from app.services.bias_detector import bias_detector
from app.services.causal_engine import causal_engine
from app.services.corrector import corrector
from app.services.threshold_config import get_tenant_thresholds
from app.auth.jwt_handler import verify_token

router = APIRouter()
security = HTTPBearer(auto_error=False)

@router.post("/decision", response_model=DecisionResponse)
async def evaluate_decision(request: DecisionRequest, credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials if credentials else None
    
    tenant_id = verify_token(token)
    if not tenant_id:
        # Fallback to dev tenant if no valid token in this sandbox version, or we could raise 401
        # For hackathon ease of use, we default to local dev if none provided.
        tenant_id = "tenant_local_dev"
        
    thresholds = get_tenant_thresholds(tenant_id)
    
    protected_attrs = request.protected_attributes or []
    
    # Fast path if no protected attributes specified
    if not protected_attrs:
        audit_id = create_audit_log(tenant_id, request.model_output, request.model_output, {}, "No protected attributes provided.", [])
        return DecisionResponse(
            original_decision=request.model_output,
            corrected_decision=request.model_output,
            bias_detected=False,
            explanation="Passed through. No protected attributes evaluated.",
            audit_id=audit_id
        )
        
    # Rate limiting placeholder
    # if rate_limit_exceeded(tenant_id): return 429 response
    
    try:
        # Phase 2: Async Parallel Pipeline
        async def get_causal():
            await asyncio.sleep(0.01)
            return causal_engine.discover_paths(request.applicant_features, protected_attrs)

        async def get_metrics():
            await asyncio.sleep(0.01)
            return bias_detector.evaluate(request.applicant_features, request.model_output, protected_attrs)
            
        causal_paths, bias_scores = await asyncio.gather(get_causal(), get_metrics())
        
        # Check thresholds
        bias_detected = False
        intervention_required = False
        
        if bias_scores["DPD"] > thresholds.DPD_THRESHOLD or bias_scores["EOD"] > thresholds.EOD_THRESHOLD:
            bias_detected = True
            
        if bias_scores["ICD"] > thresholds.ICD_THRESHOLD or bias_scores["CAS"] > thresholds.CAS_THRESHOLD:
            bias_detected = True
            intervention_required = True
            
        explanation = "No statistically significant bias detected."
        corrected_decision = request.model_output
        
        # Phase 2: Correction
        if intervention_required:
            corrected_decision, explanation = corrector.apply_correction(
                features=request.applicant_features,
                model_output=request.model_output,
                protected_attributes=protected_attrs,
                bias_scores=bias_scores
            )
        elif bias_detected:
            explanation = "Bias alert triggered on population metrics, but individual intervention threshold not met."
            
        # Audit log
        audit_id = create_audit_log(
            tenant_id=tenant_id,
            original_decision=request.model_output,
            corrected_decision=corrected_decision,
            bias_scores=bias_scores,
            explanation=explanation,
            protected_attributes=protected_attrs
        )
        
        return DecisionResponse(
            original_decision=request.model_output,
            corrected_decision=corrected_decision,
            bias_detected=bias_detected,
            explanation=explanation,
            audit_id=audit_id
        )
        
    except Exception as e:
        # Phase 5: Graceful Degradation. 
        # If the ML pipeline entirely fails (timeout, out of memory, bug), 
        # we MUST NOT crash the client's system. We pass through their decision and log the failure.
        print(f"ML Pipeline Failure: {str(e)}")
        
        audit_id = create_audit_log(
            tenant_id=tenant_id, 
            original_decision=request.model_output, 
            corrected_decision=request.model_output, 
            bias_scores={}, 
            explanation=f"SYSTEM_ERROR: Pipeline degraded gracefully. {str(e)}", 
            protected_attributes=protected_attrs
        )
        
        return DecisionResponse(
            original_decision=request.model_output,
            corrected_decision=request.model_output,
            bias_detected=False,
            explanation="Safety Passthrough: ML engine was unable to evaluate request.",
            audit_id=audit_id
        )
