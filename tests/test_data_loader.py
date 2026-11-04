"""Unit and integration tests for data loading and integrity validation."""

import os
import tempfile
import pandas as pd
import pytest

from database.data_loader import (
    DataLoadError,
    DataValidationError,
    load_all_data,
    load_customers,
    load_expenses,
    load_products,
    load_promotions,
    load_sales,
)


@pytest.fixture
def sample_valid_dir(tmp_path):
    """Create a temporary directory with minimal valid CSV files."""
    # Products
    products_csv = tmp_path / "products.csv"
    products_csv.write_text(
        "product_id,product_name,category,unit_cost,selling_price,stock_quantity,reorder_level\n"
        "P-001,Atta 5kg,Staples,200.0,240.0,10,5\n"
        "P-002,Milk 500ml,Dairy,24.0,27.0,3,5\n"
    )

    # Sales
    sales_csv = tmp_path / "sales.csv"
    sales_csv.write_text(
        "date,transaction_id,product_id,quantity,unit_price,total_amount,payment_method\n"
        "2024-01-01,TXN-1,P-001,1,240.0,240.0,Cash\n"
        "2024-01-02,TXN-2,P-002,2,27.0,54.0,UPI\n"
    )

    # Customers
    customers_csv = tmp_path / "customers.csv"
    customers_csv.write_text(
        "customer_id,customer_segment,visit_frequency,average_order_value,preferred_category\n"
        "C-001,Daily Regular,Daily,50.0,Dairy\n"
    )

    # Expenses
    expenses_csv = tmp_path / "expenses.csv"
    expenses_csv.write_text(
        "date,expense_category,amount,description\n"
        "2024-01-01,Shop Rent,800.0,Monthly premises rent\n"
    )

    # Promotions
    promotions_csv = tmp_path / "promotions.csv"
    promotions_csv.write_text(
        "promotion_id,promotion_name,start_date,end_date,discount_percentage,applicable_category,status\n"
        "PR-001,New Year Kickoff,2024-01-01,2024-01-07,5.0,Staples,Completed\n"
    )

    return str(tmp_path)


def test_load_all_real_data():
    """Verify loading and integrity of the real synthetic data directory."""
    data = load_all_data("data")
    assert "products" in data
    assert "sales" in data
    assert "customers" in data
    assert "expenses" in data
    assert "promotions" in data

    assert len(data["products"]) == 20
    assert len(data["sales"]) > 0
    assert len(data["customers"]) == 40
    assert len(data["expenses"]) == 15
    assert len(data["promotions"]) == 5


def test_sales_product_id_consistency():
    """Ensure every product_id in sales.csv exists in products.csv."""
    products = load_products("data")
    sales = load_sales("data", products_df=products)

    valid_product_ids = set(products["product_id"])
    sales_product_ids = set(sales["product_id"])

    assert sales_product_ids.issubset(valid_product_ids)


def test_sales_total_amount_integrity():
    """Verify total_amount matches quantity * unit_price across all sales."""
    sales = load_sales("data")
    expected = (sales["quantity"] * sales["unit_price"]).round(2)
    diff = (sales["total_amount"] - expected).abs()
    assert (diff < 0.01).all()


def test_missing_file_raises_error(tmp_path):
    """Test that missing CSV files raise DataLoadError."""
    with pytest.raises(DataLoadError, match="Products file not found"):
        load_products(str(tmp_path))


def test_missing_required_column(tmp_path):
    """Test that a missing required column raises DataValidationError."""
    bad_products = tmp_path / "products.csv"
    bad_products.write_text(
        "product_id,product_name,category,unit_cost\n"  # missing selling_price, stock_quantity, reorder_level
        "P-001,Atta 5kg,Staples,200.0\n"
    )
    with pytest.raises(DataValidationError, match="missing required columns"):
        load_products(str(tmp_path))


def test_negative_values_rejected(tmp_path):
    """Test that negative costs or prices trigger validation error."""
    bad_products = tmp_path / "products.csv"
    bad_products.write_text(
        "product_id,product_name,category,unit_cost,selling_price,stock_quantity,reorder_level\n"
        "P-001,Atta 5kg,Staples,-50.0,240.0,10,5\n"
    )
    with pytest.raises(DataValidationError, match="negative cost or price"):
        load_products(str(tmp_path))


def test_mismatched_sales_total_rejected(tmp_path):
    """Test that sales records with incorrect total_amount are rejected."""
    bad_sales = tmp_path / "sales.csv"
    bad_sales.write_text(
        "date,transaction_id,product_id,quantity,unit_price,total_amount,payment_method\n"
        "2024-01-01,TXN-1,P-001,2,50.0,999.0,Cash\n"  # expected 100.0, got 999.0
    )
    with pytest.raises(DataValidationError, match="total_amount != quantity"):
        load_sales(str(tmp_path))


def test_invalid_foreign_product_id_rejected(sample_valid_dir):
    """Test that sales referencing nonexistent product ID is rejected when validated against products."""
    products = load_products(sample_valid_dir)

    # Overwrite sales with an unlisted product ID
    sales_file = os.path.join(sample_valid_dir, "sales.csv")
    with open(sales_file, "a") as f:
        f.write("2024-01-03,TXN-99,GHOST-PROD,1,100.0,100.0,Cash\n")

    with pytest.raises(DataValidationError, match="not found in products.csv"):
        load_sales(sample_valid_dir, products_df=products)
