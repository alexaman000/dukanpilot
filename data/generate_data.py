"""Synthetic data generator for DukaanPilot AI - Sneha Bhandar.

Generates realistic, deterministic retail datasets for a small neighborhood
grocery store located in Shiv Shakti Nagar, Ranchi, Jharkhand (834009).
"""

from datetime import date, timedelta
import os
import random
import pandas as pd

RANDOM_SEED = 42

PRODUCTS = [
    {
        "product_id": "PROD-001",
        "product_name": "Aashirvaad Shudh Chakki Atta 5kg",
        "category": "Grains & Staples",
        "unit_cost": 210.0,
        "selling_price": 240.0,
        "stock_quantity": 12,
        "reorder_level": 5,
        "weight": 0.08,
    },
    {
        "product_id": "PROD-002",
        "product_name": "Tata Sampann Toor Dal 1kg",
        "category": "Grains & Staples",
        "unit_cost": 140.0,
        "selling_price": 165.0,
        "stock_quantity": 8,
        "reorder_level": 6,
        "weight": 0.07,
    },
    {
        "product_id": "PROD-003",
        "product_name": "Madhur Pure & Hygienic Sugar 1kg",
        "category": "Grains & Staples",
        "unit_cost": 40.0,
        "selling_price": 46.0,
        "stock_quantity": 25,
        "reorder_level": 10,
        "weight": 0.10,
    },
    {
        "product_id": "PROD-004",
        "product_name": "Fortune Kachi Ghani Mustard Oil 1L",
        "category": "Edible Oils & Spices",
        "unit_cost": 128.0,
        "selling_price": 145.0,
        "stock_quantity": 15,
        "reorder_level": 6,
        "weight": 0.07,
    },
    {
        "product_id": "PROD-005",
        "product_name": "Tata Salt Vacuum Evaporated 1kg",
        "category": "Edible Oils & Spices",
        "unit_cost": 23.0,
        "selling_price": 28.0,
        "stock_quantity": 30,
        "reorder_level": 10,
        "weight": 0.10,
    },
    {
        "product_id": "PROD-006",
        "product_name": "Everest Turmeric Powder 100g",
        "category": "Edible Oils & Spices",
        "unit_cost": 28.0,
        "selling_price": 34.0,
        "stock_quantity": 18,
        "reorder_level": 8,
        "weight": 0.05,
    },
    {
        "product_id": "PROD-007",
        "product_name": "MDH Deggi Mirch Powder 100g",
        "category": "Edible Oils & Spices",
        "unit_cost": 70.0,
        "selling_price": 82.0,
        "stock_quantity": 4,  # Low stock
        "reorder_level": 5,
        "weight": 0.03,  # Slower moving
    },
    {
        "product_id": "PROD-008",
        "product_name": "Brooke Bond Red Label Tea 250g",
        "category": "Beverages",
        "unit_cost": 98.0,
        "selling_price": 115.0,
        "stock_quantity": 14,
        "reorder_level": 6,
        "weight": 0.06,
    },
    {
        "product_id": "PROD-009",
        "product_name": "Nescafe Classic Coffee 50g",
        "category": "Beverages",
        "unit_cost": 138.0,
        "selling_price": 160.0,
        "stock_quantity": 3,  # Low stock
        "reorder_level": 5,
        "weight": 0.02,  # Slow moving
    },
    {
        "product_id": "PROD-010",
        "product_name": "Maggi 2-Minute Masala Noodles 70g",
        "category": "Snacks & Packaged Foods",
        "unit_cost": 11.5,
        "selling_price": 14.0,
        "stock_quantity": 45,
        "reorder_level": 15,
        "weight": 0.12,  # Fast moving
    },
    {
        "product_id": "PROD-011",
        "product_name": "Parle-G Gold Biscuits 250g",
        "category": "Snacks & Packaged Foods",
        "unit_cost": 20.0,
        "selling_price": 25.0,
        "stock_quantity": 35,
        "reorder_level": 12,
        "weight": 0.11,  # Fast moving
    },
    {
        "product_id": "PROD-012",
        "product_name": "Britannia Good Day Butter Cookies 200g",
        "category": "Snacks & Packaged Foods",
        "unit_cost": 25.0,
        "selling_price": 30.0,
        "stock_quantity": 20,
        "reorder_level": 8,
        "weight": 0.06,
    },
    {
        "product_id": "PROD-013",
        "product_name": "Haldiram Nagpur Aloo Bhujia 200g",
        "category": "Snacks & Packaged Foods",
        "unit_cost": 45.0,
        "selling_price": 55.0,
        "stock_quantity": 16,
        "reorder_level": 6,
        "weight": 0.05,
    },
    {
        "product_id": "PROD-014",
        "product_name": "Lay's India's Magic Masala Chips 50g",
        "category": "Snacks & Packaged Foods",
        "unit_cost": 16.0,
        "selling_price": 20.0,
        "stock_quantity": 22,
        "reorder_level": 10,
        "weight": 0.07,
    },
    {
        "product_id": "PROD-015",
        "product_name": "Amul Taaza Toned Milk 500ml",
        "category": "Dairy & Bakery",
        "unit_cost": 24.5,
        "selling_price": 27.0,
        "stock_quantity": 18,
        "reorder_level": 8,
        "weight": 0.13,  # Daily essential
    },
    {
        "product_id": "PROD-016",
        "product_name": "Britannia Whole Wheat Bread 400g",
        "category": "Dairy & Bakery",
        "unit_cost": 33.0,
        "selling_price": 40.0,
        "stock_quantity": 2,  # Low stock
        "reorder_level": 5,
        "weight": 0.05,
    },
    {
        "product_id": "PROD-017",
        "product_name": "Dettol Original Bathing Soap 75g",
        "category": "Personal Care & Hygiene",
        "unit_cost": 31.0,
        "selling_price": 38.0,
        "stock_quantity": 24,
        "reorder_level": 8,
        "weight": 0.05,
    },
    {
        "product_id": "PROD-018",
        "product_name": "Colgate Strong Teeth Toothpaste 100g",
        "category": "Personal Care & Hygiene",
        "unit_cost": 54.0,
        "selling_price": 65.0,
        "stock_quantity": 11,
        "reorder_level": 5,
        "weight": 0.04,
    },
    {
        "product_id": "PROD-019",
        "product_name": "Surf Excel Easy Wash Detergent Powder 500g",
        "category": "Household & Cleaning",
        "unit_cost": 58.0,
        "selling_price": 70.0,
        "stock_quantity": 9,
        "reorder_level": 6,
        "weight": 0.03,  # Slow moving
    },
    {
        "product_id": "PROD-020",
        "product_name": "Rin Detergent Bar 250g",
        "category": "Household & Cleaning",
        "unit_cost": 16.0,
        "selling_price": 20.0,
        "stock_quantity": 32,
        "reorder_level": 10,
        "weight": 0.08,
    },
]


def generate_all_datasets(output_dir: str = "data") -> None:
    """Generate all synthetic CSV datasets deterministically."""
    random.seed(RANDOM_SEED)
    os.makedirs(output_dir, exist_ok=True)

    # 1. products.csv
    products_clean = [
        {
            "product_id": p["product_id"],
            "product_name": p["product_name"],
            "category": p["category"],
            "unit_cost": p["unit_cost"],
            "selling_price": p["selling_price"],
            "stock_quantity": p["stock_quantity"],
            "reorder_level": p["reorder_level"],
        }
        for p in PRODUCTS
    ]
    df_products = pd.DataFrame(products_clean)
    df_products.to_csv(os.path.join(output_dir, "products.csv"), index=False)

    # 2. sales.csv (91 days: Jan 1, 2024 to Mar 31, 2024)
    start_date = date(2024, 1, 1)
    end_date = date(2024, 3, 31)
    total_days = (end_date - start_date).days + 1

    sales_records = []
    txn_counter = 10001
    prod_weights = [p["weight"] for p in PRODUCTS]
    prod_map = {p["product_id"]: p for p in PRODUCTS}

    payment_choices = ["Cash", "UPI", "Credit"]
    payment_weights = [0.55, 0.35, 0.10]

    for day_idx in range(total_days):
        current_date = start_date + timedelta(days=day_idx)
        is_weekend = current_date.weekday() in (5, 6)

        # Calibrated for small neighborhood shop: ~3-5 txns/day on weekdays, ~4-6 on weekends
        num_txns = random.randint(3, 5) if not is_weekend else random.randint(4, 6)

        for _ in range(num_txns):
            txn_id = f"TXN-{txn_counter}"
            txn_counter += 1
            pay_method = random.choices(payment_choices, weights=payment_weights, k=1)[0]

            # 1 item per basket (82%), 2 items (18%)
            items_in_txn = 1 if random.random() < 0.82 else 2
            chosen_prods = random.choices(PRODUCTS, weights=prod_weights, k=items_in_txn)

            for item in chosen_prods:
                p_id = item["product_id"]
                unit_price = item["selling_price"]

                # High price items bought 1 at a time, smaller items occasionally 2
                if unit_price > 80:
                    qty = 1
                else:
                    qty = 1 if random.random() < 0.82 else 2

                total_amount = round(qty * unit_price, 2)
                sales_records.append({
                    "date": current_date.strftime("%Y-%m-%d"),
                    "transaction_id": txn_id,
                    "product_id": p_id,
                    "quantity": qty,
                    "unit_price": unit_price,
                    "total_amount": total_amount,
                    "payment_method": pay_method,
                })

    df_sales = pd.DataFrame(sales_records)
    df_sales.to_csv(os.path.join(output_dir, "sales.csv"), index=False)

    # 3. customers.csv
    customer_segments = [
        ("Daily Regular", "Daily", 45.0, "Dairy & Bakery"),
        ("Daily Regular", "3-4 times/week", 65.0, "Snacks & Packaged Foods"),
        ("Weekly Family Shopper", "Weekly", 250.0, "Grains & Staples"),
        ("Weekly Family Shopper", "Weekly", 220.0, "Edible Oils & Spices"),
        ("Budget Essentials", "2-3 times/week", 50.0, "Grains & Staples"),
        ("Occasional Footfall", "Monthly", 90.0, "Personal Care & Hygiene"),
    ]

    customers = []
    for i in range(1, 41):
        seg_info = random.choice(customer_segments)
        aov = round(seg_info[2] * random.uniform(0.90, 1.10), 1)
        customers.append({
            "customer_id": f"CUST-{i:03d}",
            "customer_segment": seg_info[0],
            "visit_frequency": seg_info[1],
            "average_order_value": aov,
            "preferred_category": seg_info[3],
        })

    df_customers = pd.DataFrame(customers)
    df_customers.to_csv(os.path.join(output_dir, "customers.csv"), index=False)

    # 4. expenses.csv
    # Realistic small neighborhood shop monthly expenses (~INR 1,200 - 1,400/mo)
    expenses = [
        # January 2024
        {"date": "2024-01-01", "expense_category": "Shop Rent", "amount": 800.0, "description": "Monthly shop lease portion - Shiv Shakti Nagar premises"},
        {"date": "2024-01-10", "expense_category": "Electricity & Utilities", "amount": 280.0, "description": "Electricity bill for lighting and fan"},
        {"date": "2024-01-15", "expense_category": "Packaging & Bags", "amount": 90.0, "description": "Biodegradable carry bags and paper pouches"},
        {"date": "2024-01-22", "expense_category": "Store Maintenance", "amount": 80.0, "description": "Cleaning supplies and shelf upkeep"},
        {"date": "2024-01-28", "expense_category": "Local Transport", "amount": 70.0, "description": "Wholesale market transport allowance"},

        # February 2024
        {"date": "2024-02-01", "expense_category": "Shop Rent", "amount": 800.0, "description": "Monthly shop lease portion - Shiv Shakti Nagar premises"},
        {"date": "2024-02-10", "expense_category": "Electricity & Utilities", "amount": 260.0, "description": "Electricity bill for lighting and fan"},
        {"date": "2024-02-15", "expense_category": "Packaging & Bags", "amount": 85.0, "description": "Carry bags replenishment"},
        {"date": "2024-02-21", "expense_category": "Store Maintenance", "amount": 80.0, "description": "Sanitization and cleaning materials"},
        {"date": "2024-02-27", "expense_category": "Local Transport", "amount": 75.0, "description": "Stock delivery rickshaw cartage"},

        # March 2024
        {"date": "2024-03-01", "expense_category": "Shop Rent", "amount": 800.0, "description": "Monthly shop lease portion - Shiv Shakti Nagar premises"},
        {"date": "2024-03-10", "expense_category": "Electricity & Utilities", "amount": 290.0, "description": "Electricity bill for lighting and refrigeration"},
        {"date": "2024-03-16", "expense_category": "Packaging & Bags", "amount": 95.0, "description": "Packaging bags purchase"},
        {"date": "2024-03-22", "expense_category": "Store Maintenance", "amount": 85.0, "description": "Store fixture cleaning and bulb replacement"},
        {"date": "2024-03-29", "expense_category": "Local Transport", "amount": 80.0, "description": "Wholesale market stock cartage"},
    ]
    df_expenses = pd.DataFrame(expenses)
    df_expenses.to_csv(os.path.join(output_dir, "expenses.csv"), index=False)

    # 5. promotions.csv
    promotions = [
        {
            "promotion_id": "PROM-001",
            "promotion_name": "New Year Morning Staples Combo",
            "start_date": "2024-01-01",
            "end_date": "2024-01-07",
            "discount_percentage": 5.0,
            "applicable_category": "Grains & Staples",
            "status": "Completed",
        },
        {
            "promotion_id": "PROM-002",
            "promotion_name": "Republic Day Tea Time Treats",
            "start_date": "2024-01-20",
            "end_date": "2024-01-26",
            "discount_percentage": 6.0,
            "applicable_category": "Snacks & Packaged Foods",
            "status": "Completed",
        },
        {
            "promotion_id": "PROM-003",
            "promotion_name": "Holi Festival Spices & Sweets Special",
            "start_date": "2024-03-20",
            "end_date": "2024-03-26",
            "discount_percentage": 7.5,
            "applicable_category": "Edible Oils & Spices",
            "status": "Completed",
        },
        {
            "promotion_id": "PROM-004",
            "promotion_name": "Daily Essentials Morning Refresh",
            "start_date": "2024-03-27",
            "end_date": "2024-04-05",
            "discount_percentage": 5.0,
            "applicable_category": "Dairy & Bakery",
            "status": "Active",
        },
        {
            "promotion_id": "PROM-005",
            "promotion_name": "Spring Grocery Basket Growth Booster",
            "start_date": "2024-04-10",
            "end_date": "2024-04-20",
            "discount_percentage": 8.0,
            "applicable_category": "All",
            "status": "Planned",
        },
    ]
    df_promotions = pd.DataFrame(promotions)
    df_promotions.to_csv(os.path.join(output_dir, "promotions.csv"), index=False)

    print(f"Generated synthetic datasets in '{output_dir}':")
    print(f"- products.csv: {len(df_products)} products")
    print(f"- sales.csv: {len(df_sales)} transactions across {total_days} days")
    print(f"- customers.csv: {len(df_customers)} customer profiles")
    print(f"- expenses.csv: {len(df_expenses)} expense entries")
    print(f"- promotions.csv: {len(df_promotions)} promotional campaigns")


if __name__ == "__main__":
    generate_all_datasets("data")
