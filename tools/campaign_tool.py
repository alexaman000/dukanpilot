"""Customer segment campaign drafting tool for DukaanPilot AI."""

import os
from typing import Any, Dict
import pandas as pd


def draft_customer_campaign(
    target_segment: str,
    campaign_title: str,
    message_template: str,
    channel: str = "WhatsApp",
    data_dir: str = "data",
) -> Dict[str, Any]:
    """Draft a targeted customer communication message for Sneha Bhandar.

    NOTE: This is a safe local demonstration tool. No real SMS, WhatsApp,
    or phone communications are sent.

    Args:
        target_segment: Customer segment name (e.g., 'Weekly Family Shopper')
        campaign_title: Descriptive campaign name
        message_template: Text template with placeholder support
        channel: Communication medium (e.g., 'WhatsApp', 'SMS')
        data_dir: Synthetic data directory

    Returns:
        Dict[str, Any]: Structured campaign draft with segment sizing.
    """
    cust_path = os.path.join(data_dir, "customers.csv")
    if not os.path.exists(cust_path):
        raise FileNotFoundError(f"Customers dataset not found at: {cust_path}")

    df_cust = pd.read_csv(cust_path)
    matching_custs = df_cust[df_cust["customer_segment"].str.lower() == target_segment.lower()]

    target_count = len(matching_custs)
    avg_aov = round(float(matching_custs["average_order_value"].mean()), 2) if target_count > 0 else 0.0

    rendered_message = (
        message_template.replace("{shop_name}", "Sneha Bhandar")
        .replace("{location}", "Shiv Shakti Nagar, Booty More, Ranchi")
        .replace("{segment}", target_segment)
    )

    details = {
        "campaign_id": f"CMP-{channel[:3].upper()}-{len(matching_custs)}",
        "campaign_title": campaign_title,
        "target_segment": target_segment,
        "targeted_customer_count": target_count,
        "segment_average_order_value_inr": avg_aov,
        "channel": channel,
        "rendered_message": rendered_message,
        "estimated_footfall_uplift_pct": 12.0 if target_count > 0 else 0.0,
        "is_simulated": True,
    }

    return {
        "status": "success",
        "tool": "draft_customer_campaign",
        "action": "Campaign Drafted (Simulated)",
        "details": details,
        "message": f"Drafted simulated {channel} message '{campaign_title}' targeting {target_count} '{target_segment}' customers.",
    }
