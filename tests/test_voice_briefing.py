"""Unit and integration tests for AI Voice Business Briefing report generator."""

import pytest
from agents.business_analyst import BusinessAnalyst
from agents.voice_briefing import generate_business_briefing_report
from database.data_loader import load_all_data
from workflow.config import TARGET_MONTHLY_REVENUE


@pytest.fixture
def analyst() -> BusinessAnalyst:
    """Fixture providing initialized BusinessAnalyst with store datasets."""
    data = load_all_data("data")
    return BusinessAnalyst(
        sales_df=data["sales"],
        products_df=data["products"],
        expenses_df=data["expenses"],
        customers_df=data["customers"],
        promotions_df=data["promotions"],
    )


def test_briefing_report_contains_all_nine_sections(analyst):
    """Verify that the generated report contains all 9 required business sections in both languages."""
    for lang in ("en", "hi"):
        report = generate_business_briefing_report(analyst, lang=lang)
        assert len(report["sections"]) == 9
        sec_ids = [s["id"] for s in report["sections"]]
        expected_ids = [
            "financials",
            "goal",
            "products",
            "inventory",
            "customers",
            "opportunities_risks",
            "recommendations",
            "impact_costs",
            "distinction",
        ]
        assert sec_ids == expected_ids
        assert len(report["full_text"]) > 200


def test_briefing_report_preserves_factual_integrity_without_inventing_data(analyst):
    """Verify that actual recorded numbers are preserved and customer counter anonymity is noted."""
    rep_en = generate_business_briefing_report(analyst, lang="en")
    
    # Financial metrics verified
    total_rev = analyst.get_total_revenue()
    assert f"₹{total_rev:,.2f}" in rep_en["sections"][0]["text"]
    assert "₹10,000" in rep_en["sections"][1]["text"]

    # Customer patterns: explicitly states counter sales are anonymous cash/UPI purchases
    cust_sec = rep_en["sections"][4]["text"]
    assert "anonymous" in cust_sec.lower() or "cash" in cust_sec.lower()

    # Distinction between recorded figures and estimates
    dist_sec = rep_en["sections"][8]["text"]
    assert "actual records" in dist_sec.lower() or "recorded" in dist_sec.lower()
    assert "estimates" in dist_sec.lower() or "ai" in dist_sec.lower()


def test_briefing_report_hindi_natural_language(analyst):
    """Verify that the Hindi report uses respectful, natural shopkeeper language and preserves product names."""
    rep_hi = generate_business_briefing_report(analyst, lang="hi")
    
    assert "नमस्ते" in rep_hi["sections"][0]["text"]
    assert "स्नेहा भंडार" in rep_hi["sections"][0]["text"]
    assert "₹" in rep_hi["sections"][0]["text"]
    assert "लक्ष्य" in rep_hi["sections"][1]["text"]
    assert "सावधानी" in rep_hi["sections"][3]["text"] or "स्टॉक" in rep_hi["sections"][3]["text"]


def test_briefing_report_integrates_workflow_proposed_actions(analyst):
    """Verify that proposed actions from LangGraph workflow state are correctly included."""
    mock_workflow_state = {
        "proposed_actions": [
            {
                "action_id": "ACT-TEST-01",
                "action_name": "Special Mustard Oil & Salt Deal",
                "tool_name": "create_bundled_offer",
                "business_rationale": "High velocity kitchen staple bundle.",
                "expected_impact": "Estimated impact: +₹320 monthly sales",
                "estimated_cost": 25.0,
                "risks_or_constraints": "Ensure enough oil bottles.",
            }
        ]
    }

    report = generate_business_briefing_report(
        analyst, workflow_state=mock_workflow_state, lang="en"
    )
    rec_text = report["sections"][6]["text"]
    assert "Special Mustard Oil & Salt Deal" in rec_text
    assert "High velocity kitchen staple bundle" in rec_text
