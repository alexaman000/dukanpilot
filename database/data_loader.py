"""Data access and validation layer for DukaanPilot AI."""

from dataclasses import dataclass
import os
from typing import Dict, List, Optional
import pandas as pd


class DataLoadError(Exception):
    """Raised when a dataset file is missing or unreadable."""
    pass


class DataValidationError(Exception):
    """Raised when a dataset fails schema or integrity constraints."""
    pass


REQUIRED_COLUMNS: Dict[str, List[str]] = {
    "products.csv": [
        "product_id",
        "product_name",
        "category",
        "unit_cost",
        "selling_price",
        "stock_quantity",
        "reorder_level",
    ],
    "sales.csv": [
        "date",
        "transaction_id",
        "product_id",
        "quantity",
        "unit_price",
        "total_amount",
        "payment_method",
    ],
    "customers.csv": [
        "customer_id",
        "customer_segment",
        "visit_frequency",
        "average_order_value",
        "preferred_category",
    ],
    "expenses.csv": [
        "date",
        "expense_category",
        "amount",
        "description",
    ],
    "promotions.csv": [
        "promotion_id",
        "promotion_name",
        "start_date",
        "end_date",
        "discount_percentage",
        "applicable_category",
        "status",
    ],
}


def _validate_columns(df: pd.DataFrame, filename: str) -> None:
    """Validate that required columns are present in dataframe."""
    required = REQUIRED_COLUMNS.get(filename, [])
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise DataValidationError(
            f"File '{filename}' is missing required columns: {missing}. Found columns: {list(df.columns)}"
        )


def load_products(data_dir: str = "data") -> pd.DataFrame:
    """Load and validate products dataset.

    Returns:
        pd.DataFrame: Cleaned products DataFrame.
    """
    file_path = os.path.join(data_dir, "products.csv")
    if not os.path.exists(file_path):
        raise DataLoadError(f"Products file not found at: {file_path}")

    try:
        df = pd.read_csv(file_path)
    except Exception as exc:
        raise DataLoadError(f"Failed to read {file_path}: {exc}") from exc

    _validate_columns(df, "products.csv")

    if df.empty:
        raise DataValidationError("Products dataset cannot be empty.")

    # Convert and validate numeric types
    df["unit_cost"] = pd.to_numeric(df["unit_cost"], errors="coerce")
    df["selling_price"] = pd.to_numeric(df["selling_price"], errors="coerce")
    df["stock_quantity"] = pd.to_numeric(df["stock_quantity"], errors="coerce")
    df["reorder_level"] = pd.to_numeric(df["reorder_level"], errors="coerce")

    if df[["unit_cost", "selling_price", "stock_quantity", "reorder_level"]].isna().any().any():
        raise DataValidationError("Products contains non-numeric or NaN values in numeric columns.")

    if (df["unit_cost"] < 0).any() or (df["selling_price"] < 0).any():
        raise DataValidationError("Products cannot have negative cost or price values.")

    if df["product_id"].duplicated().any():
        duplicates = df[df["product_id"].duplicated()]["product_id"].tolist()
        raise DataValidationError(f"Duplicate product IDs detected: {duplicates}")

    return df


def load_sales(data_dir: str = "data", products_df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """Load and validate sales dataset.

    Args:
        data_dir: Directory containing sales.csv
        products_df: Optional preloaded products DataFrame for cross-validation

    Returns:
        pd.DataFrame: Cleaned sales DataFrame with datetime parsed.
    """
    file_path = os.path.join(data_dir, "sales.csv")
    if not os.path.exists(file_path):
        raise DataLoadError(f"Sales file not found at: {file_path}")

    try:
        df = pd.read_csv(file_path)
    except Exception as exc:
        raise DataLoadError(f"Failed to read {file_path}: {exc}") from exc

    _validate_columns(df, "sales.csv")

    if df.empty:
        raise DataValidationError("Sales dataset cannot be empty.")

    # Parse and validate dates
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    if df["date"].isna().any():
        raise DataValidationError("Sales contains invalid date values.")

    # Validate numerics
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")
    df["total_amount"] = pd.to_numeric(df["total_amount"], errors="coerce")

    if df[["quantity", "unit_price", "total_amount"]].isna().any().any():
        raise DataValidationError("Sales contains non-numeric or NaN values.")

    if (df["quantity"] <= 0).any():
        raise DataValidationError("Sales quantity must be strictly positive.")

    # Consistency check: total_amount == quantity * unit_price
    expected_total = df["quantity"] * df["unit_price"]
    discrepancy = (df["total_amount"] - expected_total).abs()
    if (discrepancy > 0.05).any():
        mismatch_count = (discrepancy > 0.05).sum()
        raise DataValidationError(f"Found {mismatch_count} sales records where total_amount != quantity * unit_price")

    # Cross-reference with products if provided
    if products_df is not None:
        valid_product_ids = set(products_df["product_id"].unique())
        invalid_ids = set(df["product_id"].unique()) - valid_product_ids
        if invalid_ids:
            raise DataValidationError(f"Sales contains product IDs not found in products.csv: {invalid_ids}")

    return df


def load_customers(data_dir: str = "data") -> pd.DataFrame:
    """Load and validate customers dataset.

    Returns:
        pd.DataFrame: Cleaned customers DataFrame.
    """
    file_path = os.path.join(data_dir, "customers.csv")
    if not os.path.exists(file_path):
        raise DataLoadError(f"Customers file not found at: {file_path}")

    try:
        df = pd.read_csv(file_path)
    except Exception as exc:
        raise DataLoadError(f"Failed to read {file_path}: {exc}") from exc

    _validate_columns(df, "customers.csv")

    if df.empty:
        raise DataValidationError("Customers dataset cannot be empty.")

    df["average_order_value"] = pd.to_numeric(df["average_order_value"], errors="coerce")
    if df["average_order_value"].isna().any():
        raise DataValidationError("Customers contains invalid average_order_value numbers.")

    if df["customer_id"].duplicated().any():
        duplicates = df[df["customer_id"].duplicated()]["customer_id"].tolist()
        raise DataValidationError(f"Duplicate customer IDs detected: {duplicates}")

    return df


def load_expenses(data_dir: str = "data") -> pd.DataFrame:
    """Load and validate expenses dataset.

    Returns:
        pd.DataFrame: Cleaned expenses DataFrame with datetime parsed.
    """
    file_path = os.path.join(data_dir, "expenses.csv")
    if not os.path.exists(file_path):
        raise DataLoadError(f"Expenses file not found at: {file_path}")

    try:
        df = pd.read_csv(file_path)
    except Exception as exc:
        raise DataLoadError(f"Failed to read {file_path}: {exc}") from exc

    _validate_columns(df, "expenses.csv")

    if df.empty:
        raise DataValidationError("Expenses dataset cannot be empty.")

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    if df["date"].isna().any():
        raise DataValidationError("Expenses contains invalid date formats.")

    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    if df["amount"].isna().any():
        raise DataValidationError("Expenses contains invalid amounts.")

    if (df["amount"] < 0).any():
        raise DataValidationError("Expense amounts cannot be negative.")

    return df


def load_promotions(data_dir: str = "data") -> pd.DataFrame:
    """Load and validate promotions dataset.

    Returns:
        pd.DataFrame: Cleaned promotions DataFrame with parsed start and end dates.
    """
    file_path = os.path.join(data_dir, "promotions.csv")
    if not os.path.exists(file_path):
        raise DataLoadError(f"Promotions file not found at: {file_path}")

    try:
        df = pd.read_csv(file_path)
    except Exception as exc:
        raise DataLoadError(f"Failed to read {file_path}: {exc}") from exc

    _validate_columns(df, "promotions.csv")

    if df.empty:
        raise DataValidationError("Promotions dataset cannot be empty.")

    df["start_date"] = pd.to_datetime(df["start_date"], errors="coerce")
    df["end_date"] = pd.to_datetime(df["end_date"], errors="coerce")
    if df["start_date"].isna().any() or df["end_date"].isna().any():
        raise DataValidationError("Promotions contains invalid date values.")

    df["discount_percentage"] = pd.to_numeric(df["discount_percentage"], errors="coerce")
    if df["discount_percentage"].isna().any():
        raise DataValidationError("Promotions contains invalid discount percentage.")

    if (df["discount_percentage"] < 0).any() or (df["discount_percentage"] > 100).any():
        raise DataValidationError("Discount percentage must be between 0 and 100.")

    return df


def load_all_data(data_dir: str = "data") -> Dict[str, pd.DataFrame]:
    """Load and validate the full suite of retail datasets.

    Args:
        data_dir: Directory containing CSV files.

    Returns:
        Dict[str, pd.DataFrame]: Dictionary mapping dataset names to DataFrames.
    """
    products = load_products(data_dir)
    sales = load_sales(data_dir, products_df=products)
    customers = load_customers(data_dir)
    expenses = load_expenses(data_dir)
    promotions = load_promotions(data_dir)

    return {
        "products": products,
        "sales": sales,
        "customers": customers,
        "expenses": expenses,
        "promotions": promotions,
    }
