"""
Domain Registry — Phase 4A (Gap 2)

Defines three pre-built domains. Each DomainConfig provides:
  • dag_edges          — causal DAG for this domain's features
  • protected_attrs    — default protected attributes
  • decision_vocab     — valid decision labels for this domain
  • causal_paths       — human-readable causal path descriptions
  • default_row        — feature defaults for counterfactual generation
  • ace_fallbacks       — literature-informed Average Causal Effects

Usage:
    from app.services.domain_registry import get_domain, DOMAINS
    cfg = get_domain("healthcare")
"""
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Any


@dataclass(frozen=True)
class DomainConfig:
    name: str
    dag_edges: List[Tuple[str, str]]
    protected_attrs: List[str]
    decision_vocab: List[str]
    causal_paths: Dict[str, List[str]]
    default_row: Dict[str, Any]
    ace_fallbacks: Dict[str, float]
    description: str = ""


# ---------------------------------------------------------------------------
# Domain 1: Lending (original UCI Adult — preserved for backward compat)
# ---------------------------------------------------------------------------
_LENDING = DomainConfig(
    name="lending",
    description="Credit/loan approval decisions based on UCI Adult income dataset.",
    dag_edges=[
        ("sex",            "occupation"),
        ("sex",            "decision"),
        ("age",            "education-num"),
        ("age",            "decision"),
        ("race",           "occupation"),
        ("race",           "decision"),
        ("education-num",  "capital-gain"),
        ("occupation",     "capital-gain"),
        ("capital-gain",   "decision"),
        ("hours-per-week", "capital-gain"),
    ],
    protected_attrs=["sex", "race", "age"],
    decision_vocab=["approved", "denied"],
    causal_paths={
        "sex":  ["sex → occupation → capital-gain → decision",
                 "sex → decision (direct effect)"],
        "age":  ["age → education-num → capital-gain → decision",
                 "age → decision (direct effect)"],
        "race": ["race → occupation → capital-gain → decision",
                 "race → decision (direct effect)"],
    },
    default_row={
        "age": 35, "education-num": 10, "capital-gain": 0,
        "capital-loss": 0, "hours-per-week": 40,
        "sex": "Male", "race": "White", "occupation": "Prof-specialty",
    },
    ace_fallbacks={"sex": 0.162, "race": 0.098, "age": 0.045},
)

# ---------------------------------------------------------------------------
# Domain 2: Healthcare — diagnosis / treatment recommendation
# ---------------------------------------------------------------------------
_HEALTHCARE = DomainConfig(
    name="healthcare",
    description="Clinical diagnosis and treatment recommendation fairness.",
    dag_edges=[
        ("race",       "diagnosis"),
        ("race",       "treatment"),
        ("sex",        "diagnosis"),
        ("age",        "comorbidity_score"),
        ("age",        "diagnosis"),
        ("disability", "treatment"),
        ("disability", "diagnosis"),
        ("comorbidity_score", "diagnosis"),
        ("insurance_type",   "treatment"),
        ("diagnosis",        "treatment"),
    ],
    protected_attrs=["race", "sex", "age", "disability"],
    decision_vocab=["treatment_recommended", "watchful_waiting", "referral_only"],
    causal_paths={
        "race":       ["race → diagnosis → treatment (mediation)",
                       "race → treatment (direct effect)"],
        "sex":        ["sex → diagnosis → treatment (mediation)"],
        "age":        ["age → comorbidity_score → diagnosis → treatment"],
        "disability": ["disability → treatment (direct effect)",
                       "disability → diagnosis → treatment"],
    },
    default_row={
        "age": 50, "comorbidity_score": 2, "insurance_type": "private",
        "race": "White", "sex": "Male", "disability": 0,
    },
    ace_fallbacks={"race": 0.185, "sex": 0.142, "age": 0.072, "disability": 0.231},
)

# ---------------------------------------------------------------------------
# Domain 3: Criminal Justice — recidivism / bail / sentencing
# ---------------------------------------------------------------------------
_CRIMINAL_JUSTICE = DomainConfig(
    name="criminal_justice",
    description="Recidivism risk scoring and bail/sentencing recommendations.",
    dag_edges=[
        ("race",          "prior_convictions"),
        ("race",          "decision"),
        ("sex",           "decision"),
        ("age",           "prior_convictions"),
        ("age",           "decision"),
        ("prior_convictions", "risk_score"),
        ("socioeconomic", "prior_convictions"),
        ("risk_score",    "decision"),
    ],
    protected_attrs=["race", "sex", "age"],
    decision_vocab=["low_risk", "medium_risk", "high_risk"],
    causal_paths={
        "race": ["race → prior_convictions → risk_score → decision",
                 "race → decision (direct effect — structural bias)"],
        "sex":  ["sex → decision (direct effect)"],
        "age":  ["age → prior_convictions → risk_score → decision",
                 "age → decision (direct effect)"],
    },
    default_row={
        "age": 28, "prior_convictions": 1, "risk_score": 0.4,
        "socioeconomic": "low", "race": "White", "sex": "Male",
    },
    ace_fallbacks={"race": 0.247, "sex": 0.119, "age": 0.088},
)

# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------
DOMAINS: Dict[str, DomainConfig] = {
    "lending":          _LENDING,
    "healthcare":       _HEALTHCARE,
    "criminal_justice": _CRIMINAL_JUSTICE,
}

_DEFAULT_DOMAIN = "lending"


def get_domain(name: str) -> DomainConfig:
    """Return a DomainConfig by name; falls back to 'lending' if unknown."""
    return DOMAINS.get(name, DOMAINS[_DEFAULT_DOMAIN])


def list_domains() -> List[Dict[str, str]]:
    """Return summary list for the API /v1/domains endpoint."""
    return [
        {
            "name": cfg.name,
            "description": cfg.description,
            "protected_attributes": cfg.protected_attrs,
            "decision_vocab": cfg.decision_vocab,
        }
        for cfg in DOMAINS.values()
    ]
