"""Product bundle recommendation tool for DukaanPilot AI."""

import os
from typing import Any, Dict
import pandas as pd


def recommend_product_bundle(
    bundle_name: str,
    primary_product_id: str,
    complementary_product_id: str,
    bundle_discount_pct: float = 5.0,
    data_dir: str = "data",
) -> Dict[str, Any]:
    """Generate a product bundle recommendation for Sneha Bhandar.

    NOTE: This is a safe local demonstration tool. No physical inventory repackaging
    or real POS modification is performed.

    Args:
        bundle_name: Marketing title of the bundle
        primary_product_id: Main anchor product (e.g., Red Label Tea)
        complementary_product_id: Cross-sell product (e.g., Parle-G Biscuits)
        bundle_discount_pct: Combo discount percentage (1-20%)
        data_dir: Synthetic data directory

    Returns:
        Dict[str, Any]: Structured bundle proposal with pricing and margin analysis.
    """
    if bundle_discount_pct < 0 or bundle_discount_pct > 20:
        raise ValueError(f"Bundle discount {bundle_discount_pct}% exceeds safe range (0-20%).")

    prod_path = os.path.join(data_dir, "products.csv")
    if not os.path.exists(prod_path):
        raise FileNotFoundError(f"Products dataset not found at: {prod_path}")

    df_prods = pd.read_csv(prod_path)
    prod1 = df_prods[df_prods["product_id"] == primary_product_id]
    prod2 = df_prods[df_prods["product_id"] == complementary_product_id]

    if prod1.empty:
        raise ValueError(f"Primary product '{primary_product_id}' not found in catalog.")
    if prod2.empty:
        raise ValueError(f"Complementary product '{complementary_product_id}' not found in catalog.")

    p1 = prod1.iloc[0]
    p2 = prod2.iloc[0]

    standalone_price = round(float(p1["selling_price"] + p2["selling_price"]), 2)
    bundle_price = round(standalone_price * (1 - bundle_discount_pct / 100), 2)
    combined_cost = round(float(p1["unit_cost"] + p2["unit_cost"]), 2)
    bundle_margin_inr = round(bundle_price - combined_cost, 2)
    bundle_margin_pct = round((bundle_margin_inr / bundle_price) * 100, 2) if bundle_price > 0 else 0.0

    customer_savings_inr = round(standalone_price - bundle_price, 2)

    details = {
        "bundle_id": f"BNDL-{primary_product_id}-{complementary_product_id}",
        "bundle_name": bundle_name,
        "items": [
            {"product_id": primary_product_id, "name": p1["product_name"], "price": float(p1["selling_price"])},
            {"product_id": complementary_product_id, "name": p2["product_name"], "price": float(p2["selling_price"])},
        ],
        "standalone_total_inr": standalone_price,
        "bundle_price_inr": bundle_price,
        "customer_savings_inr": customer_savings_inr,
        "combined_cost_inr": combined_cost,
        "bundle_gross_margin_inr": bundle_margin_inr,
        "bundle_gross_margin_pct": bundle_margin_pct,
        "estimated_basket_size_uplift_pct": round(bundle_discount_pct * 2.0, 1),
        "is_simulated": True,
    }

    return {
        "status": "success",
        "tool": "recommend_product_bundle",
        "action": "Bundle Formulated (Simulated)",
        "details": details,
        "message": f"Simulated bundle '{bundle_name}' created: {p1['product_name']} + {p2['product_name']} for ₹{bundle_price} (Save ₹{customer_savings_inr}).",
    }
