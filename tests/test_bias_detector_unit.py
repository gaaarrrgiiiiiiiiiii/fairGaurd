"""
Unit tests for BiasDetector service.

Tests cover:
  - _pad_features merging logic
  - calculate_icd with real model (if available) vs fallback
  - calculate_cas proportionality
  - evaluate() return shape and types
  - population metrics are NOT hardcoded
"""
import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

FEMALE_DENIED = {
    "applicant_features": {"age": 35, "income": 55000, "sex": "Female"},
    "model_output": {"decision": "denied", "confidence": 0.73},
    "protected_attributes": ["sex"],
}

MALE_APPROVED = {
    "applicant_features": {"age": 35, "income": 55000, "sex": "Male"},
    "model_output": {"decision": "approved", "confidence": 0.89},
    "protected_attributes": ["sex"],
}


# ---------------------------------------------------------------------------
# BiasDetector unit tests
# ---------------------------------------------------------------------------

class TestPadFeatures:
    def test_income_maps_to_capital_gain(self, detector):
        df = detector._pad_features({"income": 75000})
        assert df["capital-gain"].iloc[0] == 75000.0

    def test_custom_age_overrides_default(self, detector):
        df = detector._pad_features({"age": 62})
        assert df["age"].iloc[0] == 62

    def test_unknown_key_ignored(self, detector):
        # Should not raise
        df = detector._pad_features({"foobar": 999})
        assert "foobar" not in df.columns

    def test_sex_override(self, detector):
        df = detector._pad_features({"sex": "Female"})
        assert df["sex"].iloc[0] == "Female"


class TestICD:
    def test_icd_is_float(self, detector):
        icd = detector.calculate_icd(
            {"age": 35, "income": 55000, "sex": "Female"}, ["sex"]
        )
        assert isinstance(icd, float)
        assert 0.0 <= icd <= 1.0

    def test_icd_sex_flip(self, detector):
        icd_f = detector.calculate_icd({"age": 35, "income": 55000, "sex": "Female"}, ["sex"])
        icd_m = detector.calculate_icd({"age": 35, "income": 55000, "sex": "Male"},   ["sex"])
        # Both should be the same absolute disparity (symmetric by design)
        assert abs(icd_f - icd_m) < 0.01, "ICD should be symmetric w.r.t. sex flip"

    def test_icd_age_flip(self, detector):
        icd = detector.calculate_icd({"age": 25, "income": 40000, "sex": "Male"}, ["age"])
        assert isinstance(icd, float)
        assert icd >= 0.0

    def test_icd_unknown_attr_returns_zero(self, detector):
        icd = detector.calculate_icd({"age": 35, "sex": "Female"}, ["hair_colour"])
        assert icd == 0.0

    def test_icd_no_attrs_returns_zero(self, detector):
        icd = detector.calculate_icd({"age": 35, "sex": "Female"}, [])
        assert icd == 0.0


class TestCAS:
    def test_cas_proportional_to_icd(self, detector):
        for icd_val in [0.0, 0.1, 0.25, 0.5]:
            cas = detector.calculate_cas(icd_val)
            assert abs(cas - icd_val * 1.25) < 1e-6

    def test_cas_zero_when_icd_zero(self, detector):
        assert detector.calculate_cas(0.0) == 0.0


class TestEvaluate:
    def test_evaluate_returns_all_keys(self, detector):
        result = detector.evaluate(
            {"age": 35, "income": 55000, "sex": "Female"},
            {"decision": "denied", "confidence": 0.73},
            ["sex"],
        )
        assert set(result.keys()) == {"DPD", "EOD", "ICD", "CAS"}

    def test_evaluate_values_are_floats(self, detector):
        result = detector.evaluate(
            {"age": 35, "income": 55000, "sex": "Female"},
            {"decision": "denied", "confidence": 0.73},
            ["sex"],
        )
        for k, v in result.items():
            assert isinstance(v, float), f"{k} should be float, got {type(v)}"

    def test_dpd_is_not_hardcoded_018(self, detector):
        """Regression test: DPD must come from real data, not hardcoded 0.18."""
        result = detector.evaluate(
            {"age": 35, "sex": "Female"},
            {"decision": "denied", "confidence": 0.73},
            ["sex"],
        )
        assert result["DPD"] != 0.18, (
            "DPD is still returning the old hardcoded value 0.18 — "
            "population metrics are not being computed from real data."
        )

    def test_eod_is_not_hardcoded_012(self, detector):
        """Regression test: EOD must come from real data, not hardcoded 0.12."""
        result = detector.evaluate(
            {"age": 35, "sex": "Female"},
            {"decision": "denied", "confidence": 0.73},
            ["sex"],
        )
        assert result["EOD"] != 0.12, (
            "EOD is still returning the old hardcoded value 0.12."
        )

    def test_evaluate_race_attribute(self, detector):
        result = detector.evaluate(
            {"age": 35, "race": "Black"},
            {"decision": "denied", "confidence": 0.81},
            ["race"],
        )
        assert "DPD" in result
        assert result["DPD"] >= 0.0

    def test_no_protected_attrs_returns_zeros(self, detector):
        result = detector.evaluate(
            {"age": 35},
            {"decision": "approved", "confidence": 0.9},
            [],
        )
        # ICD and CAS should be 0 — no attributes to flip
        assert result["ICD"] == 0.0
        assert result["CAS"] == 0.0
