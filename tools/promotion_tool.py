"""Simulated promotion creation tool for DukaanPilot AI."""

from datetime import date, timedelta
import os
from typing import Any, Dict
import pandas as pd


def create_simulated_promotion(
    promotion_name: str,
    category: str,
    discount_percentage: float,
    duration_days: int = 7,
    data_dir: str = "data",
) -> Dict[str, Any]:
    """Create a simulated promotional campaign record for Sneha Bhandar.

    NOTE: This is a safe local demonstration tool. No real advertising or customer
    outreach is performed.

    Args:
        promotion_name: Descriptive title of promotion
        category: Targeted product category or 'All'
        discount_percentage: Promotional discount percent (1-30%)
        duration_days: Length of the simulated promotion in days
        data_dir: Path to synthetic data folder

    Returns:
        Dict[str, Any]: Structured execution outcome with projected impacts.
    """
    if discount_percentage <= 0 or discount_percentage > 30:
        raise ValueError(f"Discount percentage {discount_percentage}% is out of safe range (1-30%).")

    if duration_days <= 0 or duration_days > 60:
        raise ValueError(f"Duration {duration_days} days is out of allowed range (1-60 days).")

    start = date.today()
    end = start + timedelta(days=duration_days)
    prom_id = f"PROM-SIM-{start.strftime('%m%d%H%M')}"

    # Estimate simulated reach & uplift
    est_volume_uplift_pct = round(discount_percentage * 1.5, 1)
    est_gross_revenue_impact_inr = round(150.0 * duration_days * (est_volume_uplift_pct / 100), 2)

    record = {
        "promotion_id": prom_id,
        "promotion_name": promotion_name,
        "start_date": start.strftime("%Y-%m-%d"),
        "end_date": end.strftime("%Y-%m-%d"),
        "discount_percentage": float(discount_percentage),
        "applicable_category": category,
        "status": "Simulated Active",
        "is_simulated": True,
        "estimated_volume_uplift_pct": est_volume_uplift_pct,
        "estimated_revenue_uplift_inr": est_gross_revenue_impact_inr,
    }

    return {
        "status": "success",
        "tool": "create_simulated_promotion",
        "action": "Promotion Created (Simulated)",
        "details": record,
        "message": f"Simulated promotion '{promotion_name}' scheduled for {category} ({discount_percentage}% off for {duration_days} days).",
    }
