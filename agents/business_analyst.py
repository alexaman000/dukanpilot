"""Business analysis module for DukaanPilot AI.

Performs deterministic business and financial calculations for Sneha Bhandar
using Python and Pandas. No arithmetic or metric extrapolation is delegated to LLMs.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import pandas as pd


class BusinessAnalyst:
    """Analytics engine for retail operations and financial KPIs."""

    def __init__(
        self,
        sales_df: pd.DataFrame,
        products_df: pd.DataFrame,
        expenses_df: Optional[pd.DataFrame] = None,
        customers_df: Optional[pd.DataFrame] = None,
        promotions_df: Optional[pd.DataFrame] = None,
    ):
        """Initialize analyst with verified retail dataframes."""
        self.sales = sales_df.copy()
        self.products = products_df.copy()
        self.expenses = expenses_df.copy() if expenses_df is not None else pd.DataFrame()
        self.customers = customers_df.copy() if customers_df is not None else pd.DataFrame()
        self.promotions = promotions_df.copy() if promotions_df is not None else pd.DataFrame()

        # Ensure datetime on sales and expenses
        if not self.sales.empty and not pd.api.types.is_datetime64_any_dtype(self.sales["date"]):
            self.sales["date"] = pd.to_datetime(self.sales["date"])
        if not self.expenses.empty and not pd.api.types.is_datetime64_any_dtype(self.expenses["date"]):
            self.expenses["date"] = pd.to_datetime(self.expenses["date"])

    def _filter_sales(
        self, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """Filter sales by date range if provided."""
        df = self.sales
        if start_date is not None:
            df = df[df["date"] >= pd.to_datetime(start_date)]
        if end_date is not None:
            df = df[df["date"] <= pd.to_datetime(end_date)]
        return df

    def get_total_revenue(
        self, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> float:
        """Calculate total revenue for a given date range."""
        df = self._filter_sales(start_date, end_date)
        if df.empty:
            return 0.0
        return round(float(df["total_amount"].sum()), 2)

    def get_revenue_by_day(
        self, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """Calculate daily revenue and transaction count."""
        df = self._filter_sales(start_date, end_date)
        if df.empty:
            return pd.DataFrame(columns=["date", "revenue", "transactions", "units_sold"])

        grouped = df.groupby(df["date"].dt.strftime("%Y-%m-%d")).agg(
            revenue=("total_amount", "sum"),
            transactions=("transaction_id", "nunique"),
            units_sold=("quantity", "sum"),
        ).reset_index()

        grouped["revenue"] = grouped["revenue"].round(2)
        return grouped.sort_values("date")

    def get_revenue_by_month(self) -> pd.DataFrame:
        """Calculate monthly revenue and transaction metrics."""
        if self.sales.empty:
            return pd.DataFrame(columns=["month", "revenue", "transactions", "units_sold", "avg_daily_revenue"])

        df = self.sales.copy()
        df["month"] = df["date"].dt.strftime("%Y-%m")

        grouped = df.groupby("month").agg(
            revenue=("total_amount", "sum"),
            transactions=("transaction_id", "nunique"),
            units_sold=("quantity", "sum"),
            days_active=("date", lambda s: s.dt.date.nunique()),
        ).reset_index()

        grouped["revenue"] = grouped["revenue"].round(2)
        grouped["avg_daily_revenue"] = (grouped["revenue"] / grouped["days_active"]).round(2)
        return grouped.sort_values("month")

    def get_revenue_by_product(
        self, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """Calculate revenue and units sold per product."""
        df = self._filter_sales(start_date, end_date)
        if df.empty:
            return pd.DataFrame(columns=["product_id", "product_name", "category", "revenue", "units_sold"])

        agg = df.groupby("product_id").agg(
            revenue=("total_amount", "sum"),
            units_sold=("quantity", "sum"),
        ).reset_index()

        merged = pd.merge(self.products, agg, on="product_id", how="left")
        merged["revenue"] = merged["revenue"].fillna(0.0).round(2)
        merged["units_sold"] = merged["units_sold"].fillna(0).astype(int)

        return merged[["product_id", "product_name", "category", "revenue", "units_sold"]].sort_values(
            "revenue", ascending=False
        )

    def get_revenue_by_category(
        self, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """Calculate aggregate revenue and volume by product category."""
        prod_rev = self.get_revenue_by_product(start_date, end_date)
        if prod_rev.empty:
            return pd.DataFrame(columns=["category", "revenue", "units_sold", "share_pct"])

        cat_summary = prod_rev.groupby("category").agg(
            revenue=("revenue", "sum"),
            units_sold=("units_sold", "sum"),
        ).reset_index()

        total_rev = cat_summary["revenue"].sum()
        cat_summary["share_pct"] = (
            (cat_summary["revenue"] / total_rev * 100).round(2) if total_rev > 0 else 0.0
        )
        cat_summary["revenue"] = cat_summary["revenue"].round(2)
        return cat_summary.sort_values("revenue", ascending=False)

    def get_units_sold_by_product(
        self, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """Retrieve unit sales breakdown per product."""
        prod_rev = self.get_revenue_by_product(start_date, end_date)
        return prod_rev[["product_id", "product_name", "category", "units_sold"]].sort_values(
            "units_sold", ascending=False
        )

    def get_average_transaction_value(
        self, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> float:
        """Calculate average order / basket value across unique transactions."""
        df = self._filter_sales(start_date, end_date)
        if df.empty:
            return 0.0

        txn_totals = df.groupby("transaction_id")["total_amount"].sum()
        return round(float(txn_totals.mean()), 2)

    def get_gross_profit(
        self, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> Dict[str, float]:
        """Calculate gross profit and gross margin using product cost records."""
        df = self._filter_sales(start_date, end_date)
        if df.empty:
            return {
                "total_revenue": 0.0,
                "total_cogs": 0.0,
                "gross_profit": 0.0,
                "gross_margin_pct": 0.0,
            }

        merged = pd.merge(df, self.products[["product_id", "unit_cost"]], on="product_id", how="left")
        merged["cogs"] = merged["quantity"] * merged["unit_cost"]

        total_rev = round(float(merged["total_amount"].sum()), 2)
        total_cogs = round(float(merged["cogs"].sum()), 2)
        gross_profit = round(total_rev - total_cogs, 2)
        gross_margin_pct = round((gross_profit / total_rev * 100), 2) if total_rev > 0 else 0.0

        return {
            "total_revenue": total_rev,
            "total_cogs": total_cogs,
            "gross_profit": gross_profit,
            "gross_margin_pct": gross_margin_pct,
        }

    def get_net_profit(
        self, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> Dict[str, float]:
        """Calculate operating expenses and estimated net profit."""
        gp_metrics = self.get_gross_profit(start_date, end_date)

        exp_df = self.expenses
        if not exp_df.empty:
            if start_date is not None:
                exp_df = exp_df[exp_df["date"] >= pd.to_datetime(start_date)]
            if end_date is not None:
                exp_df = exp_df[exp_df["date"] <= pd.to_datetime(end_date)]
            total_expenses = round(float(exp_df["amount"].sum()), 2)
        else:
            total_expenses = 0.0

        estimated_net_profit = round(gp_metrics["gross_profit"] - total_expenses, 2)
        net_margin_pct = (
            round((estimated_net_profit / gp_metrics["total_revenue"] * 100), 2)
            if gp_metrics["total_revenue"] > 0
            else 0.0
        )

        return {
            "total_revenue": gp_metrics["total_revenue"],
            "total_cogs": gp_metrics["total_cogs"],
            "gross_profit": gp_metrics["gross_profit"],
            "gross_margin_pct": gp_metrics["gross_margin_pct"],
            "total_expenses": total_expenses,
            "estimated_net_profit": estimated_net_profit,
            "net_margin_pct": net_margin_pct,
        }

    def get_best_selling_products(
        self, top_n: int = 5, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """Identify top-performing products by total revenue."""
        prod_rev = self.get_revenue_by_product(start_date, end_date)
        return prod_rev.head(top_n)

    def get_slow_moving_products(
        self, bottom_n: int = 5, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """Identify slow-moving items by unit sales volume."""
        prod_rev = self.get_revenue_by_product(start_date, end_date)
        return prod_rev.sort_values(["units_sold", "revenue"], ascending=[True, True]).head(bottom_n)

    def get_low_stock_products(self) -> pd.DataFrame:
        """Detect inventory items with stock levels at or below reorder threshold."""
        if self.products.empty:
            return pd.DataFrame()

        low_stock = self.products[self.products["stock_quantity"] <= self.products["reorder_level"]].copy()
        low_stock["stock_deficit"] = low_stock["reorder_level"] - low_stock["stock_quantity"]
        return low_stock.sort_values("stock_deficit", ascending=False)

    def compare_to_growth_target(
        self, baseline_monthly: float = 8000.0, target_monthly: float = 10000.0
    ) -> Dict[str, Any]:
        """Compare actual monthly average revenue against baseline and target milestones."""
        monthly_df = self.get_revenue_by_month()
        if monthly_df.empty:
            actual_monthly_avg = 0.0
            num_months = 0
        else:
            actual_monthly_avg = round(float(monthly_df["revenue"].mean()), 2)
            num_months = len(monthly_df)

        gap_to_target = round(target_monthly - actual_monthly_avg, 2)
        variance_to_baseline = round(actual_monthly_avg - baseline_monthly, 2)
        target_achievement_pct = round((actual_monthly_avg / target_monthly * 100), 2) if target_monthly > 0 else 0.0

        return {
            "baseline_monthly_inr": baseline_monthly,
            "target_monthly_inr": target_monthly,
            "actual_monthly_avg_inr": actual_monthly_avg,
            "months_analyzed": num_months,
            "variance_to_baseline_inr": variance_to_baseline,
            "gap_to_target_inr": gap_to_target,
            "target_achievement_pct": target_achievement_pct,
            "monthly_breakdown": monthly_df.to_dict(orient="records"),
        }

    def generate_executive_summary(self) -> Dict[str, Any]:
        """Compile a comprehensive executive summary for Sneha Bhandar."""
        net_metrics = self.get_net_profit()
        growth_comparison = self.compare_to_growth_target()
        low_stock_df = self.get_low_stock_products()
        best_sellers = self.get_best_selling_products(3)
        slow_movers = self.get_slow_moving_products(3)

        return {
            "financials": net_metrics,
            "growth_status": growth_comparison,
            "average_transaction_value": self.get_average_transaction_value(),
            "low_stock_alert_count": len(low_stock_df),
            "low_stock_items": low_stock_df["product_name"].tolist() if not low_stock_df.empty else [],
            "top_products": best_sellers[["product_name", "revenue", "units_sold"]].to_dict(orient="records"),
            "slow_products": slow_movers[["product_name", "units_sold"]].to_dict(orient="records"),
        }
