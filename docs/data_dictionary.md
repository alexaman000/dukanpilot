# DukaanPilot AI: Data Dictionary & Analysis Specification

## 1. Business Context

The datasets model the operational records of **Sneha Bhandar**, a small neighborhood grocery store (*kirana*) located in **Shiv Shakti Nagar, Ranchi, Jharkhand, 834009, India**.

* **Store Type:** Neighborhood daily-needs and dry grocery retail.
* **Currency:** Indian Rupee (INR / ₹).
* **Baseline Revenue:** ~₹8,000 / month.
* **Target Revenue Goal:** ₹10,000 / month.
* **Environment:** Purely synthetic simulation with fixed random seeds for reproducible experiments.

---

## 2. Dataset Schemas

### 2.1 Products (`data/products.csv`)
Catalog of 20 retail items across 7 grocery categories.

| Column | Type | Description | Sample Value |
| :--- | :--- | :--- | :--- |
| `product_id` | String | Unique product identifier (`PROD-XXX`) | `PROD-001` |
| `product_name` | String | Commercial product name and packaging size | `Aashirvaad Shudh Chakki Atta 5kg` |
| `category` | String | Grocery category classification | `Grains & Staples` |
| `unit_cost` | Float | Wholesale acquisition cost per unit (INR) | `210.0` |
| `selling_price` | Float | Shelf retail price per unit (INR) | `240.0` |
| `stock_quantity` | Integer | Units on shelf and backroom storage | `12` |
| `reorder_level` | Integer | Threshold triggering replenishment order | `5` |

**Categories Included:**
* `Grains & Staples` (Atta, Dal, Sugar)
* `Edible Oils & Spices` (Mustard Oil, Salt, Turmeric, Deggi Mirch)
* `Beverages` (Red Label Tea, Nescafe Coffee)
* `Snacks & Packaged Foods` (Maggi, Parle-G, Good Day, Bhujia, Lay's)
* `Dairy & Bakery` (Amul Milk, Britannia Bread)
* `Personal Care & Hygiene` (Dettol Soap, Colgate Toothpaste)
* `Household & Cleaning` (Surf Excel, Rin Bar)

---

### 2.2 Sales (`data/sales.csv`)
Individual transaction line items spanning 91 calendar days (January 1, 2024 to March 31, 2024).

| Column | Type | Description | Sample Value |
| :--- | :--- | :--- | :--- |
| `date` | Date (YYYY-MM-DD) | Date of transaction | `2024-01-01` |
| `transaction_id` | String | Unique basket / transaction identifier | `TXN-10001` |
| `product_id` | String | Foreign key to `products.csv` | `PROD-015` |
| `quantity` | Integer | Number of units purchased | `1` |
| `unit_price` | Float | Price per unit at purchase time (INR) | `27.0` |
| `total_amount` | Float | Line total (`quantity * unit_price`) (INR) | `27.0` |
| `payment_method` | String | Transaction tender (`Cash`, `UPI`, `Credit`) | `Cash` |

---

### 2.3 Customers (`data/customers.csv`)
Customer persona profiles representing local shopping patterns in Shiv Shakti Nagar.

| Column | Type | Description | Sample Value |
| :--- | :--- | :--- | :--- |
| `customer_id` | String | Unique profile ID (`CUST-XXX`) | `CUST-001` |
| `customer_segment` | String | Segment (`Daily Regular`, `Weekly Family Shopper`, `Budget Essentials`, `Occasional Footfall`) | `Daily Regular` |
| `visit_frequency` | String | Visit regularity pattern | `Daily` |
| `average_order_value`| Float | Typical basket expenditure (INR) | `45.0` |
| `preferred_category` | String | Most frequently purchased category | `Dairy & Bakery` |

---

### 2.4 Expenses (`data/expenses.csv`)
Monthly operating overheads for maintaining the retail premises.

| Column | Type | Description | Sample Value |
| :--- | :--- | :--- | :--- |
| `date` | Date (YYYY-MM-DD) | Expense settlement date | `2024-01-01` |
| `expense_category` | String | Overhead category (`Shop Rent`, `Electricity & Utilities`, `Packaging & Bags`, `Store Maintenance`, `Local Transport`) | `Shop Rent` |
| `amount` | Float | Monetary cost incurred (INR) | `800.0` |
| `description` | String | Expense narrative | `Monthly shop lease portion - Shiv Shakti Nagar premises` |

---

### 2.5 Promotions (`data/promotions.csv`)
Campaigns and discounts run or planned for the shop.

| Column | Type | Description | Sample Value |
| :--- | :--- | :--- | :--- |
| `promotion_id` | String | Promotion code (`PROM-XXX`) | `PROM-001` |
| `promotion_name` | String | Campaign marketing title | `New Year Morning Staples Combo` |
| `start_date` | Date (YYYY-MM-DD) | Campaign start date | `2024-01-01` |
| `end_date` | Date (YYYY-MM-DD) | Campaign end date | `2024-01-07` |
| `discount_percentage`| Float | Percentage markdown | `5.0` |
| `applicable_category`| String | Target product category or `All` | `Grains & Staples` |
| `status` | String | Lifecycle state (`Completed`, `Active`, `Planned`) | `Completed` |

---

## 3. Data Generation & Integrity Constraints

All datasets are generated programmatically via `data/generate_data.py` using a fixed random seed (`RANDOM_SEED = 42`):

1. **Deterministic Reproducibility:** Re-running the generation script yields the exact same records and numbers.
2. **Strict Foreign Key Consistency:** 100% of product IDs in `sales.csv` exist in `products.csv`.
3. **Line Item Exactness:** Every line item satisfies `total_amount == round(quantity * unit_price, 2)`.
4. **Realistic Footfall Variance:**
   - Weekdays average 3–5 customer transactions per day.
   - Weekends (Saturday and Sunday) reflect a ~30% footfall boost (4–6 transactions per day).
5. **Calibrated Baseline:** The 91-day historical period produces an average monthly revenue of approximately ₹9,150 (with February at ₹8,161), presenting a realistic starting point to optimize toward the ₹10,000/month target.

---

## 4. Financial Calculation Formulas

All analytical metrics are computed deterministically using **Python and Pandas** in `agents/business_analyst.py`:

* **Total Revenue:**
  $$\text{Revenue} = \sum \text{total\_amount}$$

* **Cost of Goods Sold (COGS):**
  $$\text{COGS} = \sum (\text{quantity} \times \text{unit\_cost})$$

* **Gross Profit & Gross Margin:**
  $$\text{Gross Profit} = \text{Revenue} - \text{COGS}$$
  $$\text{Gross Margin \%} = \left( \frac{\text{Gross Profit}}{\text{Revenue}} \right) \times 100$$

* **Estimated Net Profit:**
  $$\text{Net Profit} = \text{Gross Profit} - \sum \text{expense\_amount}$$
  $$\text{Net Margin \%} = \left( \frac{\text{Net Profit}}{\text{Revenue}} \right) \times 100$$

* **Average Transaction Value (ATV / AOV):**
  $$\text{ATV} = \frac{\text{Total Revenue}}{\text{Number of Unique Transaction IDs}}$$

* **Low-Stock Detection:**
  $$\text{Condition: } \text{stock\_quantity} \le \text{reorder\_level}$$
  $$\text{Stock Deficit} = \text{reorder\_level} - \text{stock\_quantity}$$

* **Growth Target Comparison:**
  $$\text{Monthly Average} = \frac{1}{N} \sum_{m=1}^{N} \text{Monthly Revenue}_m$$
  $$\text{Gap to Target} = ₹10,000 - \text{Monthly Average}$$
  $$\text{Target Achievement \%} = \left( \frac{\text{Monthly Average}}{₹10,000} \right) \times 100$$

---

## 5. Execution & Validation

### Regenerate Synthetic Datasets
```bash
python data/generate_data.py
```

### Run Automated Data Validation & Business Analysis Tests
```bash
pytest
```
