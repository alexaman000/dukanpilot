"""Low-stock reorder suggestion tool for DukaanPilot AI."""

import os
from typing import Any, Dict
import pandas as pd


def create_reorder_suggestion(
    product_id: str,
    suggested_quantity: int = 10,
    data_dir: str = "data",
) -> Dict[str, Any]:
    """Generate a low-stock purchase order suggestion for Sneha Bhandar.

    NOTE: This is a safe local demonstration tool. No real supplier communication,
    financial transaction, or vendor booking is performed.

    Args:
        product_id: Product ID requiring inventory replenishment
        suggested_quantity: Number of units proposed to order
        data_dir: Path to synthetic data directory

    Returns:
        Dict[str, Any]: Structured purchase draft with stockout risk analysis.
    """
    if suggested_quantity <= 0 or suggested_quantity > 100:
        raise ValueError(f"Suggested quantity {suggested_quantity} must be between 1 and 100 units.")

    prod_path = os.path.join(data_dir, "products.csv")
    if not os.path.exists(prod_path):
        raise FileNotFoundError(f"Products dataset not found at: {prod_path}")

    df_prods = pd.read_csv(prod_path)
    match = df_prods[df_prods["product_id"] == product_id]
    if match.empty:
        raise ValueError(f"Product '{product_id}' not found in catalog.")

    item = match.iloc[0]
    unit_cost = float(item["unit_cost"])
    current_stock = int(item["stock_quantity"])
    reorder_level = int(item["reorder_level"])

    est_order_cost_inr = round(suggested_quantity * unit_cost, 2)
    stock_deficit = max(0, reorder_level - current_stock)
    is_critical = current_stock <= reorder_level

    details = {
        "order_id": f"PO-DRAFT-{product_id}",
        "product_id": product_id,
        "product_name": item["product_name"],
        "category": item["category"],
        "current_stock": current_stock,
        "reorder_level": reorder_level,
        "stock_deficit": stock_deficit,
        "suggested_units": suggested_quantity,
        "unit_wholesale_cost_inr": unit_cost,
        "estimated_procurement_cost_inr": est_order_cost_inr,
        "stockout_risk_averted": is_critical,
        "supplier_location": "Daily Market Mandi, Ranchi",
        "is_simulated": True,
    }

    return {
        "status": "success",
        "tool": "create_reorder_suggestion",
        "action": "Procurement Draft Created (Simulated)",
        "details": details,
        "message": f"Draft order generated for {item['product_name']}: {suggested_quantity} units @ ₹{unit_cost}/unit (Est. Cost: ₹{est_order_cost_inr}).",
    }
