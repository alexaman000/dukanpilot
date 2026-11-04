"""Unit tests for the BusinessAnalyst calculation engine."""

import pandas as pd
import pytest

from agents.business_analyst import BusinessAnalyst
from database.data_loader import load_all_data


@pytest.fixture
def sample_business_data():
    """Create controlled sample DataFrames for exact numerical verification."""
    products = pd.DataFrame([
        {
            "product_id": "P-1",
            "product_name": "Product Alpha",
            "category": "Staples",
            "unit_cost": 80.0,
            "selling_price": 100.0,
            "stock_quantity": 4,
            "reorder_level": 5,  # Low stock: 4 <= 5
        },
        {
            "product_id": "P-2",
            "product_name": "Product Beta",
            "category": "Snacks",
            "unit_cost": 15.0,
            "selling_price": 20.0,
            "stock_quantity": 25,
            "reorder_level": 10,  # Healthy stock
        },
        {
            "product_id": "P-3",
            "product_name": "Product Gamma",
            "category": "Snacks",
            "unit_cost": 40.0,
            "selling_price": 50.0,
            "stock_quantity": 2,
            "reorder_level": 2,  # Low stock: 2 <= 2
        },
    ])

    sales = pd.DataFrame([
        # Day 1
        {"date": "2024-01-01", "transaction_id": "T-1", "product_id": "P-1", "quantity": 2, "unit_price": 100.0, "total_amount": 200.0, "payment_method": "Cash"},
        {"date": "2024-01-01", "transaction_id": "T-1", "product_id": "P-2", "quantity": 3, "unit_price": 20.0, "total_amount": 60.0, "payment_method": "Cash"},
        # Day 2
        {"date": "2024-01-02", "transaction_id": "T-2", "product_id": "P-2", "quantity": 5, "unit_price": 20.0, "total_amount": 100.0, "payment_method": "UPI"},
        # Month 2
        {"date": "2024-02-01", "transaction_id": "T-3", "product_id": "P-3", "quantity": 1, "unit_price": 50.0, "total_amount": 50.0, "payment_method": "Credit"},
    ])

    expenses = pd.DataFrame([
        {"date": "2024-01-01", "expense_category": "Rent", "amount": 100.0, "description": "Jan rent"},
        {"date": "2024-02-01", "expense_category": "Rent", "amount": 100.0, "description": "Feb rent"},
    ])

    return BusinessAnalyst(sales_df=sales, products_df=products, expenses_df=expenses)


def test_total_revenue(sample_business_data):
    """Verify total revenue matches sum of all sales."""
    # 200 + 60 + 100 + 50 = 410.0
    assert sample_business_data.get_total_revenue() == 410.0


def test_total_revenue_date_filter(sample_business_data):
    """Verify total revenue respects date range filter."""
    jan_revenue = sample_business_data.get_total_revenue(start_date="2024-01-01", end_date="2024-01-31")
    assert jan_revenue == 360.0  # 200 + 60 + 100


def test_revenue_by_month(sample_business_data):
    """Verify revenue aggregation by month."""
    monthly = sample_business_data.get_revenue_by_month()
    assert len(monthly) == 2

    jan = monthly[monthly["month"] == "2024-01"].iloc[0]
    assert jan["revenue"] == 360.0
    assert jan["transactions"] == 2
    assert jan["units_sold"] == 10

    feb = monthly[monthly["month"] == "2024-02"].iloc[0]
    assert feb["revenue"] == 50.0
    assert feb["transactions"] == 1


def test_revenue_by_category(sample_business_data):
    """Verify revenue aggregation by product category."""
    cat_df = sample_business_data.get_revenue_by_category()
    # Staples: 200 (P-1)
    # Snacks: 60 (P-2) + 100 (P-2) + 50 (P-3) = 210
    staples = cat_df[cat_df["category"] == "Staples"].iloc[0]
    snacks = cat_df[cat_df["category"] == "Snacks"].iloc[0]

    assert staples["revenue"] == 200.0
    assert snacks["revenue"] == 210.0
    assert round(staples["share_pct"] + snacks["share_pct"], 1) == 100.0


def test_average_transaction_value(sample_business_data):
    """Verify average transaction / basket calculation across distinct transaction IDs."""
    # T-1: 200 + 60 = 260
    # T-2: 100
    # T-3: 50
    # Mean: (260 + 100 + 50) / 3 = 410 / 3 = 136.67
    aov = sample_business_data.get_average_transaction_value()
    assert aov == 136.67


def test_gross_profit_calculation(sample_business_data):
    """Verify COGS and gross profit using product unit costs."""
    # P-1: 2 units * cost 80 = 160 (rev 200)
    # P-2: 8 units * cost 15 = 120 (rev 160)
    # P-3: 1 unit * cost 40 = 40 (rev 50)
    # Total Rev = 410.0
    # Total COGS = 160 + 120 + 40 = 320.0
    # Gross Profit = 410 - 320 = 90.0
    # Margin = 90 / 410 = 21.95%
    gp = sample_business_data.get_gross_profit()
    assert gp["total_revenue"] == 410.0
    assert gp["total_cogs"] == 320.0
    assert gp["gross_profit"] == 90.0
    assert gp["gross_margin_pct"] == 21.95


def test_net_profit_calculation(sample_business_data):
    """Verify operating expenses deduction to produce net profit."""
    # Gross Profit = 90.0
    # Total Expenses = 200.0 (100 Jan + 100 Feb)
    # Net Profit = 90.0 - 200.0 = -110.0
    np_res = sample_business_data.get_net_profit()
    assert np_res["gross_profit"] == 90.0
    assert np_res["total_expenses"] == 200.0
    assert np_res["estimated_net_profit"] == -110.0


def test_low_stock_detection(sample_business_data):
    """Verify identification of products below or equal to reorder level."""
    low_stock = sample_business_data.get_low_stock_products()
    # P-1 (stock 4, reorder 5) -> deficit 1
    # P-3 (stock 2, reorder 2) -> deficit 0
    # P-2 (stock 25, reorder 10) -> healthy
    assert len(low_stock) == 2
    assert set(low_stock["product_id"]) == {"P-1", "P-3"}


def test_growth_target_comparison(sample_business_data):
    """Verify comparison against monthly baseline (₹8,000) and target (₹10,000)."""
    comparison = sample_business_data.compare_to_growth_target(
        baseline_monthly=8000.0, target_monthly=10000.0
    )
    # Avg monthly revenue across Jan (360) and Feb (50) = 205.0
    assert comparison["baseline_monthly_inr"] == 8000.0
    assert comparison["target_monthly_inr"] == 10000.0
    assert comparison["actual_monthly_avg_inr"] == 205.0
    assert comparison["gap_to_target_inr"] == 10000.0 - 205.0


def test_real_dataset_calculations():
    """Verify calculations execute cleanly against the real synthetic dataset."""
    data = load_all_data("data")
    analyst = BusinessAnalyst(
        sales_df=data["sales"],
        products_df=data["products"],
        expenses_df=data["expenses"],
        customers_df=data["customers"],
        promotions_df=data["promotions"],
    )

    summary = analyst.generate_executive_summary()
    assert summary["financials"]["total_revenue"] > 0
    assert summary["financials"]["gross_profit"] > 0
    assert summary["growth_status"]["actual_monthly_avg_inr"] > 0
    assert summary["low_stock_alert_count"] >= 1
    assert len(summary["top_products"]) == 3
    assert len(summary["slow_products"]) == 3
