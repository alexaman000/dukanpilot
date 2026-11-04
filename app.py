"""DukaanPilot AI - Interactive Streamlit Dashboard for Sneha Bhandar.

Autonomous AI Business Growth Worker for micro-retailers in Ranchi, Jharkhand.
Includes Action-Oriented Shopkeeper Summary, Bilingual (Hindi/English) Support,
Plain-Language Insights, 1-Click Human Approval, and Full Visual Analytics.
"""

from datetime import datetime
import os
import sqlite3
from typing import Any, Dict, List, Optional
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from agents.business_analyst import BusinessAnalyst
from agents.shopkeeper_insights import (
    get_plain_language_insights,
    get_shopkeeper_action_view,
    get_shopkeeper_status,
    get_shopkeeper_summary,
    get_workflow_timeline,
    t,
)
from database.data_loader import load_all_data
from database.run_tracker import list_all_runs, record_run_state
from langgraph.types import Command
from workflow import (
    BASELINE_MONTHLY_REVENUE,
    MONTHLY_REVENUE_GROWTH_TARGET,
    SHOP_ADDRESS,
    SHOP_CURRENCY,
    SHOP_NAME,
    SHOP_TYPE,
    TARGET_MONTHLY_REVENUE,
    build_growth_workflow,
    create_initial_state,
    is_gemini_available,
)
from workflow.config import DEFAULT_DB_PATH

# -----------------------------------------------------------------------------
# Page Configuration & Styling
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title=f"{SHOP_NAME} | DukaanPilot AI",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for crisp retail analytics appearance and accessible shopkeeper UI
st.markdown(
    """
    <style>
    .metric-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .badge-simulated {
        background-color: #e0f2fe;
        color: #0369a1;
        border: 1px solid #bae6fd;
    }
    .badge-approved {
        background-color: #dcfce7;
        color: #15803d;
        border: 1px solid #bbf7d0;
    }
    .badge-paused {
        background-color: #fef3c7;
        color: #b45309;
        border: 1px solid #fde68a;
    }
    .badge-rejected {
        background-color: #fee2e2;
        color: #b91c1c;
        border: 1px solid #fecaca;
    }
    .badge-metric {
        background-color: #f1f5f9;
        color: #334155;
        border: 1px solid #cbd5e1;
    }
    .badge-estimate {
        background-color: #fae8ff;
        color: #86198f;
        border: 1px solid #f0abfc;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# Data Access & Workflow Helpers
# -----------------------------------------------------------------------------
@st.cache_data(ttl=60)
def get_store_data() -> Dict[str, pd.DataFrame]:
    """Load and validate all synthetic store datasets."""
    return load_all_data("data")


def get_analyst(data: Dict[str, pd.DataFrame]) -> BusinessAnalyst:
    """Initialize BusinessAnalyst instance with store datasets."""
    return BusinessAnalyst(
        sales_df=data["sales"],
        products_df=data["products"],
        expenses_df=data["expenses"],
        customers_df=data["customers"],
        promotions_df=data["promotions"],
    )


def get_workflow_snapshot(app: Any, thread_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve full state snapshot from SQLite checkpointer including active interrupts."""
    try:
        config = {"configurable": {"thread_id": thread_id}}
        snapshot = app.get_state(config)
        if not snapshot or not snapshot.values:
            return None
        res = dict(snapshot.values)
        interrupts = []
        for task in getattr(snapshot, "tasks", []):
            if getattr(task, "interrupts", None):
                interrupts.extend(task.interrupts)
        if interrupts:
            res["__interrupt__"] = interrupts
        return res
    except Exception:
        return None


# -----------------------------------------------------------------------------
# Session State Initialization
# -----------------------------------------------------------------------------
if "active_thread_id" not in st.session_state:
    st.session_state["active_thread_id"] = "demo-sneha-session-01"

if "workflow_app" not in st.session_state:
    st.session_state["workflow_app"] = build_growth_workflow()

if "workflow_result" not in st.session_state:
    st.session_state["workflow_result"] = get_workflow_snapshot(
        st.session_state["workflow_app"], st.session_state["active_thread_id"]
    )

if "lang" not in st.session_state:
    st.session_state["lang"] = "en"


# -----------------------------------------------------------------------------
# Sidebar Navigation & Business Identity
# -----------------------------------------------------------------------------
st.sidebar.markdown(f"## 🏪 {SHOP_NAME}")
st.sidebar.caption(f"📍 {SHOP_ADDRESS}")
st.sidebar.markdown(f"**Type:** {SHOP_TYPE}")
st.sidebar.markdown(
    """
    <span class="status-badge badge-simulated">Synthetic Simulation Active</span>
    """,
    unsafe_allow_html=True,
)

st.sidebar.markdown("---")

# Language Selector (English default, with full Hindi option)
lang_choice = st.sidebar.radio(
    "🌐 Language / भाषा",
    ["English", "हिन्दी (Hindi)"],
    index=0 if st.session_state["lang"] == "en" else 1,
)
lang = "en" if "English" in lang_choice else "hi"
st.session_state["lang"] = lang

st.sidebar.markdown("---")

# Navigation options (Preserving all original sections + Adding primary Shopkeeper Home)
if lang == "hi":
    nav_labels = [
        "🏪 दुकान डैशबोर्ड (मुख्य सारांश और सुझाव)",
        "📊 Business Overview (विस्तृत रिपोर्ट)",
        "🎯 Business Goal (व्यापार लक्ष्य)",
        "🤖 AI Growth Plan (AI विकास योजना)",
        "✋ Human Approval (दुकानदार अनुमोदन)",
        "⚡ Execution & Outcomes (परिणाम और प्रभाव)",
        "📜 Run History (रन इतिहास)",
    ]
else:
    nav_labels = [
        "🏪 Shopkeeper Summary & Actions",
        "📊 Business Overview",
        "🎯 Business Goal",
        "🤖 AI Growth Plan",
        "✋ Human Approval",
        "⚡ Execution & Outcomes",
        "📜 Run History",
    ]

selected_nav = st.sidebar.radio("Navigation / नेविगेशन", nav_labels, index=0)
selected_idx = nav_labels.index(selected_nav)

st.sidebar.markdown("---")
gemini_status = (
    "🟢 Configured (Gemini API)" if is_gemini_available() else "⚪ Offline / Deterministic Mode"
)
st.sidebar.caption(f"**Reasoning Engine:**\n{gemini_status}")
st.sidebar.caption(f"**Active Session:** `{st.session_state['active_thread_id']}`")


# -----------------------------------------------------------------------------
# SECTION 0: SHOPKEEPER SUMMARY & ACTIONS (ADDITIONAL ACTION-ORIENTED FEATURE)
# -----------------------------------------------------------------------------
if selected_idx == 0:
    data = get_store_data()
    analyst = get_analyst(data)
    summary = get_shopkeeper_summary(analyst, lang)
    insights = get_plain_language_insights(analyst, lang)
    status_info = summary["status"]

    # 1. Simple Business Summary (Friendly greeting & top-level health)
    st.title(f"🏪 {summary['greeting']}")
    st.markdown(
        f"**{SHOP_NAME}** — {SHOP_ADDRESS} | *{summary['subtitle']}*"
    )
    st.caption(summary["disclaimer"])

    # Friendly Metric Cards
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric(
            label=t("current_monthly_sales", lang),
            value=f"₹{summary['current_monthly_sales']:,.2f}",
            help="Actual measured monthly average calculated from store records",
        )
    with k2:
        st.metric(
            label=t("monthly_goal", lang),
            value=f"₹{summary['monthly_goal']:,.0f}",
            help="Demonstration target setting for Sneha Bhandar",
        )
    with k3:
        gap = summary["remaining_gap"]
        st.metric(
            label=t("remaining_to_goal", lang),
            value=f"₹{gap:,.2f}" if gap > 0 else "Goal Met!",
            delta=f"₹{gap:,.0f} to go" if gap > 0 else "On Target",
            delta_color="inverse" if gap > 0 else "normal",
        )
    with k4:
        code = status_info["code"]
        if code == "doing_well":
            badge_class = "badge-approved"
            icon = "✅"
        elif code == "needs_attention":
            badge_class = "badge-paused"
            icon = "⚠️"
        else:
            badge_class = "badge-rejected"
            icon = "🚨"

        st.markdown(f"**{t('overall_status', lang)}**")
        st.markdown(
            f"""<div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px 14px;">
                <span class="status-badge {badge_class}" style="font-size: 0.95rem;">{icon} {status_info['label']}</span>
            </div>""",
            unsafe_allow_html=True,
        )

    # Status, Most Important Issue, and Next Action (Plain text explanations, no color dependence)
    st.info(
        f"**🔍 {t('key_issue', lang)}:** {summary['key_issue']}\n\n"
        f"**🚀 {t('recommended_action', lang)}:** {summary['recommended_action']}\n\n"
        f"*{status_info['description']}*"
    )

    st.markdown("---")

    # 2. Plain-Language Insights (Everyday business statements grounded in data)
    st.subheader(f"💡 {t('plain_insights_title', lang)}")
    st.caption("Analytical conclusions translated into simple everyday shopkeeper terms without technical jargon.")

    for ins in insights:
        st.markdown(
            f"""
            <div class="metric-card">
                <span style="font-size: 1.25rem;">{ins['icon']}</span> <strong>{ins['topic']}</strong><br/>
                <span style="color: #334155; line-height: 1.5;">{ins['text']}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # 3. Recommended Actions ("What should I do next?")
    st.subheader(f"🎯 {t('what_to_do_next', lang)}")
    st.caption(
        "Actionable growth recommendations created by DukaanPilot. You maintain full control — no action is executed without your explicit decision."
    )

    app = st.session_state["workflow_app"]
    config = {"configurable": {"thread_id": st.session_state["active_thread_id"]}}

    current_res = st.session_state["workflow_result"]
    if current_res is None:
        current_res = get_workflow_snapshot(app, st.session_state["active_thread_id"])
        if current_res:
            st.session_state["workflow_result"] = current_res

    interrupts = current_res.get("__interrupt__", []) if current_res else []
    approval_status = current_res.get("approval_status", "pending") if current_res else "pending"
    workflow_status = current_res.get("workflow_status", "pending") if current_res else "pending"
    is_paused = len(interrupts) > 0 or (
        workflow_status in ("validated", "awaiting_approval") and approval_status == "pending"
    )

    if current_res is None or workflow_status == "pending":
        st.markdown(f"*{t('no_active_plan', lang)}*")
        if st.button(t("btn_run_planner", lang), type="primary", use_container_width=True, key="sh_run_btn"):
            with st.spinner("DukaanPilot is inspecting store records and formulating recommendations..."):
                init_state = create_initial_state()
                res = app.invoke(init_state, config=config)
                st.session_state["workflow_result"] = res
                record_run_state(st.session_state["active_thread_id"], res)
                st.rerun()

    elif is_paused:
        st.warning(f"⏸️ **{t('approval_paused_alert', lang)}**")
        if interrupts:
            actions = interrupts[0].value.get("proposed_actions", [])
        else:
            actions = current_res.get("proposed_actions", [])

        st.markdown(
            f"DukaanPilot has prepared **{len(actions)} specific growth actions** for your review:"
        )

        for idx, act in enumerate(actions, 1):
            view = get_shopkeeper_action_view(act, lang)
            st.markdown(
                f"""
                <div class="metric-card">
                    <h4 style="margin-top:0;">{idx}. {view['title']}</h4>
                    <p><strong>{t('why_it_suggests', lang)}:</strong> {view['why']}</p>
                    <p><strong>{t('expected_benefit', lang)}:</strong> {view['benefit']}</p>
                    <p><strong>{t('cost_and_risk', lang)}:</strong> {t('cost_label', lang)}: {view['cost']} | {t('risk_label', lang)}: {view['risk']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Simple 1-Click Approve / Reject / Revise controls
        btn_c1, btn_c2, btn_c3 = st.columns(3)
        with btn_c1:
            if st.button(
                t("btn_approve_all", lang),
                type="primary",
                use_container_width=True,
                key="sh_approve_btn",
            ):
                with st.spinner("Executing approved actions in simulation..."):
                    res = app.invoke(Command(resume="approve"), config=config)
                    st.session_state["workflow_result"] = res
                    record_run_state(st.session_state["active_thread_id"], res)
                    st.success("Plan Approved! Simulated tools executed.")
                    st.rerun()

        with btn_c2:
            if st.button(
                t("btn_reject_all", lang),
                type="secondary",
                use_container_width=True,
                key="sh_reject_btn",
            ):
                with st.spinner("Rejecting plan..."):
                    res = app.invoke(Command(resume="reject"), config=config)
                    st.session_state["workflow_result"] = res
                    record_run_state(st.session_state["active_thread_id"], res)
                    st.error("Plan Rejected. Zero tools were executed.")
                    st.rerun()

        with btn_c3:
            with st.expander(t("btn_revise", lang)):
                st.markdown("Choose which actions to apply:")
                toggles = {}
                for a in actions:
                    toggles[a["action_id"]] = st.checkbox(
                        a.get("action_name", a["action_id"]), value=True, key=f"sh_chk_{a['action_id']}"
                    )
                if st.button(t("btn_apply_revision", lang), use_container_width=True, key="sh_apply_rev_btn"):
                    selected = [a for a in actions if toggles.get(a["action_id"])]
                    if not selected:
                        st.warning("Please select at least one action.")
                    else:
                        with st.spinner("Applying selected actions..."):
                            res = app.invoke(
                                Command(resume={"decision": "revise", "actions": selected}),
                                config=config,
                            )
                            st.session_state["workflow_result"] = res
                            record_run_state(st.session_state["active_thread_id"], res)
                            st.success("Custom plan applied and executed.")
                            st.rerun()

    elif approval_status == "approved":
        st.success(f"✅ **{t('approval_granted_alert', lang)}**")
        measured = current_res.get("measured_outcomes", {})
        uplift = measured.get("total_simulated_revenue_uplift_inr", 0.0)
        new_rate = measured.get("projected_monthly_run_rate_inr", 0.0)

        st.markdown(
            f"- **Simulated Revenue Uplift:** +₹{uplift:,.2f} *(Simulated projection)*\n"
            f"- **Projected New Monthly Sales:** ₹{new_rate:,.2f} (Target: ₹10,000)\n"
            f"- *{t('simulated_action_notice', lang)}*"
        )
        if st.button("🔄 Start New Recommendation Run / नया सुझाव सत्र", key="sh_new_run_btn"):
            new_id = f"demo-sneha-{datetime.now().strftime('%m%d-%H%M%S')}"
            st.session_state["active_thread_id"] = new_id
            st.session_state["workflow_result"] = None
            st.rerun()

    elif approval_status == "rejected":
        st.error(f"❌ **{t('approval_rejected_alert', lang)}**")
        st.caption(t("simulated_action_notice", lang))
        if st.button("🔄 Ask for Fresh Recommendations / नए सुझाव मांगें", key="sh_retry_btn"):
            new_id = f"demo-sneha-{datetime.now().strftime('%m%d-%H%M%S')}"
            st.session_state["active_thread_id"] = new_id
            st.session_state["workflow_result"] = None
            st.rerun()

    st.markdown("---")

    # 4. AI Worker Activity (Accurate 5-stage timeline from actual LangGraph state)
    st.subheader(f"🤖 {t('worker_activity_title', lang)}")
    st.caption("Live workflow timeline reflecting the actual internal execution state of DukaanPilot AI.")

    timeline = get_workflow_timeline(current_res, lang)
    t_cols = st.columns(len(timeline))
    for col, step in zip(t_cols, timeline):
        with col:
            st_code = step["status"]
            if st_code == "completed":
                badge_style = "badge-approved"
                icon_step = "✅"
            elif st_code == "waiting":
                badge_style = "badge-paused"
                icon_step = "⏸️"
            elif st_code == "rejected":
                badge_style = "badge-rejected"
                icon_step = "❌"
            else:
                badge_style = "badge-metric"
                icon_step = "⚪"

            st.markdown(
                f"""
                <div class="metric-card" style="min-height: 140px;">
                    <strong>{step['title']}</strong><br/>
                    <span class="status-badge {badge_style}" style="margin: 6px 0;">{icon_step} {step['badge']}</span><br/>
                    <small style="color: #64748b;">{step['note']}</small>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("---")

    # 5. Detailed Reports (Optional Section - Clean charts viewable right here!)
    with st.expander(t("detailed_reports_title", lang), expanded=False):
        st.markdown("### 📊 In-Depth Retail Analytics & Trends")
        st.caption("Detailed charts, product movement tables, and inventory metrics.")

        col_left, col_right = st.columns(2)
        with col_left:
            daily_df = analyst.get_revenue_by_day()
            if not daily_df.empty:
                fig_d = px.line(
                    daily_df,
                    x="date",
                    y="revenue",
                    title="Daily Sales Trend (₹)",
                    labels={"revenue": "Revenue (₹)", "date": "Date"},
                    markers=True,
                )
                fig_d.update_layout(margin=dict(l=20, r=20, t=35, b=20), height=300)
                st.plotly_chart(fig_d, use_container_width=True)

        with col_right:
            cat_df = analyst.get_revenue_by_category()
            if not cat_df.empty:
                fig_c = px.bar(
                    cat_df,
                    x="category",
                    y="revenue",
                    color="category",
                    title="Sales by Category (₹)",
                    text_auto=".2s",
                )
                fig_c.update_layout(
                    showlegend=False, margin=dict(l=20, r=20, t=35, b=20), height=300
                )
                st.plotly_chart(fig_c, use_container_width=True)

        # Products breakdown
        p1, p2 = st.columns(2)
        with p1:
            st.markdown("#### 🏆 Top-Selling Products")
            st.dataframe(
                analyst.get_best_selling_products(5)[
                    ["product_name", "category", "revenue", "units_sold"]
                ].rename(
                    columns={
                        "product_name": "Product",
                        "category": "Category",
                        "revenue": "Revenue (₹)",
                        "units_sold": "Units Sold",
                    }
                ),
                use_container_width=True,
                hide_index=True,
            )
        with p2:
            st.markdown("#### 🐢 Slow-Moving Products")
            st.dataframe(
                analyst.get_slow_moving_products(5)[
                    ["product_name", "category", "units_sold", "revenue"]
                ].rename(
                    columns={
                        "product_name": "Product",
                        "category": "Category",
                        "units_sold": "Units Sold",
                        "revenue": "Revenue (₹)",
                    }
                ),
                use_container_width=True,
                hide_index=True,
            )


# -----------------------------------------------------------------------------
# SECTION 1: BUSINESS OVERVIEW (100% PRESERVED ORIGINAL VISUAL ANALYTICS)
# -----------------------------------------------------------------------------
elif selected_idx == 1:
    st.title("📊 Business Overview & Retail Analytics")
    st.markdown(
        f"Operational and financial overview for **{SHOP_NAME}** based on synthetic grocery records."
    )

    data = get_store_data()
    analyst = get_analyst(data)

    # Date Period Filter
    col_filter, col_spacer = st.columns([2, 3])
    with col_filter:
        period_choice = st.selectbox(
            "Select Time Period",
            [
                "All Historical Data (Jan - Mar 2024)",
                "January 2024",
                "February 2024",
                "March 2024",
            ],
            index=0,
        )

    # Date Range Mapping
    date_bounds = {
        "All Historical Data (Jan - Mar 2024)": (None, None),
        "January 2024": ("2024-01-01", "2024-01-31"),
        "February 2024": ("2024-02-01", "2024-02-29"),
        "March 2024": ("2024-03-01", "2024-03-31"),
    }
    start_d, end_d = date_bounds[period_choice]

    # Calculate deterministic metrics
    total_revenue = analyst.get_total_revenue(start_d, end_d)
    gp_data = analyst.get_gross_profit(start_d, end_d)
    np_data = analyst.get_net_profit(start_d, end_d)
    aov = analyst.get_average_transaction_value(start_d, end_d)

    # Top KPI Metrics Cards
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.metric(label="Total Revenue", value=f"₹{total_revenue:,.2f}")
    with m2:
        st.metric(
            label="Gross Profit",
            value=f"₹{gp_data['gross_profit']:,.2f}",
            delta=f"{gp_data['gross_margin_pct']:.1f}% margin",
        )
    with m3:
        st.metric(label="Operating Expenses", value=f"₹{np_data['total_expenses']:,.2f}")
    with m4:
        st.metric(
            label="Estimated Net Profit",
            value=f"₹{np_data['estimated_net_profit']:,.2f}",
            delta=f"{np_data['net_margin_pct']:.1f}% net",
        )
    with m5:
        st.metric(label="Average Basket (ATV)", value=f"₹{aov:,.2f}")

    st.markdown("---")

    # Visualizations: Daily Revenue Trend & Category Breakdown
    c_left, c_right = st.columns(2)

    with c_left:
        st.subheader("Daily Revenue Trajectory")
        daily_df = analyst.get_revenue_by_day(start_d, end_d)
        if not daily_df.empty:
            fig_daily = px.line(
                daily_df,
                x="date",
                y="revenue",
                title=f"Daily Sales Revenue (₹) - {period_choice}",
                labels={"revenue": "Revenue (₹)", "date": "Date"},
                markers=True,
            )
            fig_daily.update_layout(margin=dict(l=20, r=20, t=35, b=20), height=320)
            st.plotly_chart(fig_daily, use_container_width=True)
        else:
            st.info("No daily sales data for this period.")

    with c_right:
        st.subheader("Revenue by Category")
        cat_df = analyst.get_revenue_by_category(start_d, end_d)
        if not cat_df.empty:
            fig_cat = px.bar(
                cat_df,
                x="category",
                y="revenue",
                color="category",
                title=f"Revenue by Category (₹) - {period_choice}",
                labels={"revenue": "Revenue (₹)", "category": "Category"},
                text_auto=".2s",
            )
            fig_cat.update_layout(
                showlegend=False, margin=dict(l=20, r=20, t=35, b=20), height=320
            )
            st.plotly_chart(fig_cat, use_container_width=True)
        else:
            st.info("No category data available for this period.")

    st.markdown("---")

    # Product Performance Breakdown
    t_col1, t_col2, t_col3 = st.columns(3)

    with t_col1:
        st.subheader("🏆 Top-Selling Products")
        best_df = analyst.get_best_selling_products(5, start_d, end_d)
        st.dataframe(
            best_df[["product_name", "category", "revenue", "units_sold"]].rename(
                columns={
                    "product_name": "Product",
                    "category": "Category",
                    "revenue": "Revenue (₹)",
                    "units_sold": "Units Sold",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )

    with t_col2:
        st.subheader("🐢 Slow-Moving Products")
        slow_df = analyst.get_slow_moving_products(5, start_d, end_d)
        st.dataframe(
            slow_df[["product_name", "category", "units_sold", "revenue"]].rename(
                columns={
                    "product_name": "Product",
                    "category": "Category",
                    "units_sold": "Units Sold",
                    "revenue": "Revenue (₹)",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )

    with t_col3:
        st.subheader("⚠️ Low-Stock Alerts")
        low_stock = analyst.get_low_stock_products()
        if not low_stock.empty:
            st.dataframe(
                low_stock[
                    ["product_name", "stock_quantity", "reorder_level", "stock_deficit"]
                ].rename(
                    columns={
                        "product_name": "Product",
                        "stock_quantity": "Current Stock",
                        "reorder_level": "Reorder Level",
                        "stock_deficit": "Units Below Reorder",
                    }
                ),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.success("All inventory stock levels are healthy.")


# -----------------------------------------------------------------------------
# SECTION 2: BUSINESS GOAL (100% PRESERVED ORIGINAL VISUAL ANALYTICS)
# -----------------------------------------------------------------------------
elif selected_idx == 2:
    st.title("🎯 Business Growth Goal")
    st.markdown(
        f"Demonstration objective for **{SHOP_NAME}**: Increase monthly revenue from **₹8,000** to **₹10,000**."
    )

    data = get_store_data()
    analyst = get_analyst(data)
    growth_data = analyst.compare_to_growth_target(
        baseline_monthly=BASELINE_MONTHLY_REVENUE,
        target_monthly=TARGET_MONTHLY_REVENUE,
    )

    actual_avg = growth_data["actual_monthly_avg_inr"]
    target_inr = growth_data["target_monthly_inr"]
    baseline_inr = growth_data["baseline_monthly_inr"]
    gap_inr = growth_data["gap_to_target_inr"]
    achieved_pct = min(100.0, growth_data["target_achievement_pct"])

    g1, g2, g3, g4 = st.columns(4)
    with g1:
        st.metric(
            label="Baseline Monthly Revenue",
            value=f"₹{baseline_inr:,.0f}",
            help="Designated demonstration starting point",
        )
    with g2:
        st.metric(
            label="Measured Monthly Average",
            value=f"₹{actual_avg:,.2f}",
            delta=f"+₹{growth_data['variance_to_baseline_inr']:,.2f} vs baseline",
        )
    with g3:
        st.metric(
            label="Target Monthly Revenue",
            value=f"₹{target_inr:,.0f}",
            delta=f"+₹{target_inr - baseline_inr:,.0f} milestone goal",
        )
    with g4:
        st.metric(
            label="Remaining Monthly Gap",
            value=f"₹{gap_inr:,.2f}",
            delta=f"{100.0 - achieved_pct:.1f}% remaining" if gap_inr > 0 else "Goal Met",
            delta_color="inverse",
        )

    st.markdown("---")

    c_gauge, c_monthly = st.columns([1, 1])

    with c_gauge:
        st.subheader("Target Milestone Progress")
        fig_gauge = go.Figure(
            go.Indicator(
                mode="gauge+number+delta",
                value=actual_avg,
                domain={"x": [0, 1], "y": [0, 1]},
                title={"text": "Monthly Run Rate vs Target (₹)"},
                delta={"reference": target_inr, "increasing": {"color": "green"}},
                gauge={
                    "axis": {"range": [None, 12000]},
                    "bar": {"color": "#0284c7"},
                    "steps": [
                        {"range": [0, baseline_inr], "color": "#f1f5f9"},
                        {"range": [baseline_inr, target_inr], "color": "#e2e8f0"},
                    ],
                    "threshold": {
                        "line": {"color": "#16a34a", "width": 4},
                        "thickness": 0.75,
                        "value": target_inr,
                    },
                },
            )
        )
        fig_gauge.update_layout(height=280, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_gauge, use_container_width=True)

    with c_monthly:
        st.subheader("Monthly Historical Breakdown")
        month_df = analyst.get_revenue_by_month()
        if not month_df.empty:
            fig_months = px.bar(
                month_df,
                x="month",
                y="revenue",
                title="Revenue by Calendar Month (INR)",
                text_auto=".2s",
                labels={"revenue": "Revenue (₹)", "month": "Month"},
            )
            fig_months.add_hline(
                y=baseline_inr,
                line_dash="dash",
                line_color="#64748b",
                annotation_text="Baseline ₹8,000",
            )
            fig_months.add_hline(
                y=target_inr,
                line_dash="dash",
                line_color="#16a34a",
                annotation_text="Target ₹10,000",
            )
            fig_months.update_layout(height=280, margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_months, use_container_width=True)

    st.caption(
        "⚠️ **Demonstration Settings Disclaimer:** Baseline (₹8,000) and target (₹10,000) figures are benchmark demonstration milestones established for Sneha Bhandar. They are demonstration settings and do not represent verified real-world business figures."
    )


# -----------------------------------------------------------------------------
# SECTION 3: AI GROWTH PLAN (100% PRESERVED ORIGINAL WORKFLOW ENGINE)
# -----------------------------------------------------------------------------
elif selected_idx == 3:
    st.title("🤖 AI Growth Strategy Planner")
    st.markdown(
        f"Autonomous LangGraph reasoning engine analyzing data and generating growth actions for **{SHOP_NAME}**."
    )

    ctrl1, ctrl2, ctrl3 = st.columns([3, 1, 2])
    with ctrl1:
        thread_input = st.text_input(
            "Workflow Thread / Run ID:",
            value=st.session_state["active_thread_id"],
            help="Unique ID used by SQLite checkpointer to serialize and resume execution state.",
        )
        if thread_input.strip() != st.session_state["active_thread_id"]:
            st.session_state["active_thread_id"] = thread_input.strip()
            st.session_state["workflow_result"] = get_workflow_snapshot(
                st.session_state["workflow_app"], st.session_state["active_thread_id"]
            )

    with ctrl2:
        st.write("")
        st.write("")
        if st.button("🆕 New Run ID", use_container_width=True):
            new_id = f"demo-sneha-{datetime.now().strftime('%m%d-%H%M%S')}"
            st.session_state["active_thread_id"] = new_id
            st.session_state["workflow_result"] = None
            st.rerun()

    with ctrl3:
        st.write("")
        st.write("")
        start_btn = st.button("🚀 Run Growth Planner", type="primary", use_container_width=True)

    app = st.session_state["workflow_app"]
    config = {"configurable": {"thread_id": st.session_state["active_thread_id"]}}

    if start_btn:
        with st.spinner("Executing Business Analyst & Growth Planner nodes..."):
            init_state = create_initial_state()
            res = app.invoke(init_state, config=config)
            st.session_state["workflow_result"] = res
            record_run_state(st.session_state["active_thread_id"], res)
            st.success("Workflow executed up to Human Approval checkpoint.")

    current_res = st.session_state["workflow_result"]
    if current_res is None:
        current_res = get_workflow_snapshot(app, st.session_state["active_thread_id"])
        if current_res:
            st.session_state["workflow_result"] = current_res

    if current_res is None:
        st.info("Click **'Run Growth Planner'** above to start a stateful LangGraph execution.")
    else:
        metrics = current_res.get("business_metrics", {})
        if metrics:
            st.subheader("📋 Business Analyst Diagnostic Summary")
            st.caption(
                "📊 **Measured Business Metrics (Deterministic Pandas Calculation - Offline Verified)**"
            )
            a_col1, a_col2, a_col3 = st.columns(3)
            with a_col1:
                fin = metrics.get("financials", {})
                st.markdown(
                    f"**Total Historical Revenue:** ₹{fin.get('total_revenue', 0):,.2f}"
                )
                st.markdown(f"**Gross Margin:** {fin.get('gross_margin_pct', 0)}%")
            with a_col2:
                st.markdown(
                    f"**Low-Stock Risk Items:** {metrics.get('low_stock_alert_count', 0)}"
                )
                st.markdown(
                    f"**Average Order Value:** ₹{metrics.get('average_transaction_value', 0):,.2f}"
                )
            with a_col3:
                growth_status = metrics.get("growth_status", {})
                st.markdown(
                    f"**Monthly Revenue Gap:** ₹{growth_status.get('gap_to_target_inr', 0):,.2f}"
                )
                st.markdown(
                    f"**Target Achievement:** {growth_status.get('target_achievement_pct', 0)}%"
                )

        st.markdown("---")

        interrupts = current_res.get("__interrupt__", [])
        if interrupts:
            proposed = interrupts[0].value.get("proposed_actions", [])
        else:
            proposed = current_res.get("proposed_actions", [])

        st.subheader(f"💡 Proposed Growth Interventions ({len(proposed)} Actions)")
        st.caption(
            "🤖 **AI-Generated Action Plan:** Expected impact and revenue estimates are model projections, not guaranteed outcomes. All actions map to safe local simulation tools."
        )

        for idx, act in enumerate(proposed, 1):
            with st.expander(
                f"Action {idx}: {act.get('action_name')} (`{act.get('tool_name')}`)",
                expanded=True,
            ):
                col_a, col_b = st.columns([2, 1])
                with col_a:
                    st.markdown(f"**Business Rationale:** {act.get('business_rationale')}")
                    st.markdown(
                        f"**Expected Impact:** {act.get('expected_impact')} "
                        f'<span class="status-badge badge-estimate">AI Estimate</span>',
                        unsafe_allow_html=True,
                    )
                    st.markdown(f"**Success Metric:** `{act.get('success_metric')}`")
                with col_b:
                    st.markdown(f"**Estimated Cost:** ₹{act.get('estimated_cost', 0):,.2f}")
                    st.markdown(f"**Risks & Constraints:** {act.get('risks_or_constraints')}")
                    st.markdown(f"**Parameters:** `{act.get('parameters')}`")

        val_res = current_res.get("validation_results", {})
        if val_res:
            st.markdown("---")
            st.subheader("🛡️ Action Validation Report")
            v1, v2, v3 = st.columns(3)
            with v1:
                st.metric("Total Proposed", val_res.get("total_proposed", len(proposed)))
            with v2:
                st.metric("Validated Actions", val_res.get("total_valid", len(proposed)))
            with v3:
                st.metric("Rejected Actions", val_res.get("total_rejected", 0))

        if interrupts:
            st.warning(
                "⏸️ **Workflow is paused at the Human Approval gate.** Proceed to the **'✋ Human Approval'** tab to review, approve, reject, or customize."
            )


# -----------------------------------------------------------------------------
# SECTION 4: HUMAN APPROVAL (100% PRESERVED ORIGINAL APPROVAL GATE)
# -----------------------------------------------------------------------------
elif selected_idx == 4:
    st.title("✋ Human-in-the-Loop Approval Gate")
    st.markdown(
        f"Review and authorize proposed business actions for **{SHOP_NAME}** before any tool execution."
    )

    app = st.session_state["workflow_app"]
    config = {"configurable": {"thread_id": st.session_state["active_thread_id"]}}

    current_res = st.session_state["workflow_result"]
    if current_res is None:
        current_res = get_workflow_snapshot(app, st.session_state["active_thread_id"])
        if current_res:
            st.session_state["workflow_result"] = current_res

    if current_res is None:
        st.info(
            f"No workflow run found for thread `{st.session_state['active_thread_id']}`. "
            "Start a run in **'🤖 AI Growth Plan'** first."
        )
    else:
        interrupts = current_res.get("__interrupt__", [])
        approval_status = current_res.get("approval_status", "pending")
        w_status = current_res.get("workflow_status", "pending")

        is_paused = len(interrupts) > 0 or (
            w_status in ("validated", "awaiting_approval") and approval_status == "pending"
        )

        if is_paused:
            if interrupts:
                actions = interrupts[0].value.get("proposed_actions", [])
            else:
                actions = current_res.get("proposed_actions", [])

            st.markdown(
                """
                <span class="status-badge badge-paused">⏸️ Approval Required: Execution Halted</span>
                """,
                unsafe_allow_html=True,
            )
            st.markdown(
                f"The LangGraph workflow has paused and saved state to SQLite (`{st.session_state['active_thread_id']}`). "
                f"Explicit shop owner authorization is required for **{len(actions)} proposed actions**:"
            )

            for idx, act in enumerate(actions, 1):
                st.markdown(
                    f"**{idx}. [{act.get('action_id')}] {act.get('action_name')}** (`{act.get('tool_name')}`)\n"
                    f"   - **Impact:** {act.get('expected_impact')} *(AI Estimate)*\n"
                    f"   - **Est. Cost:** ₹{act.get('estimated_cost', 0):,.2f} | **Metric:** `{act.get('success_metric')}`\n"
                    f"   - **Parameters:** `{act.get('parameters')}`"
                )

            st.markdown("---")
            st.subheader("Authorization Controls")

            btn_col1, btn_col2, btn_col3 = st.columns(3)

            with btn_col1:
                approve_btn = st.button(
                    "✅ Approve Full Strategy",
                    type="primary",
                    use_container_width=True,
                    help="Resumes LangGraph workflow to execute approved demonstration tools.",
                )
            with btn_col2:
                reject_btn = st.button(
                    "❌ Reject Strategy",
                    type="secondary",
                    use_container_width=True,
                    help="Cancels execution immediately with zero tools executed.",
                )
            with btn_col3:
                revise_expander = st.expander("✏️ Revise / Customize Actions")

            if approve_btn:
                with st.spinner("Resuming workflow with Approval..."):
                    res = app.invoke(Command(resume="approve"), config=config)
                    st.session_state["workflow_result"] = res
                    record_run_state(st.session_state["active_thread_id"], res)
                    st.success("Plan Approved! Tool execution complete.")
                    st.rerun()

            if reject_btn:
                with st.spinner("Terminating workflow with Rejection..."):
                    res = app.invoke(Command(resume="reject"), config=config)
                    st.session_state["workflow_result"] = res
                    record_run_state(st.session_state["active_thread_id"], res)
                    st.error("Plan Rejected. Workflow terminated without executing tools.")
                    st.rerun()

            with revise_expander:
                st.markdown("Select specific actions to execute:")
                action_toggles = {}
                for a in actions:
                    action_toggles[a["action_id"]] = st.checkbox(
                        f"{a['action_name']} ({a['tool_name']})",
                        value=True,
                        key=f"rev_{a['action_id']}",
                    )
                apply_revision_btn = st.button(
                    "Apply Selected Actions & Resume", use_container_width=True
                )

                if apply_revision_btn:
                    selected = [a for a in actions if action_toggles.get(a["action_id"])]
                    if not selected:
                        st.warning("Please select at least one action.")
                    else:
                        with st.spinner("Resuming with customized plan..."):
                            res = app.invoke(
                                Command(resume={"decision": "revise", "actions": selected}),
                                config=config,
                            )
                            st.session_state["workflow_result"] = res
                            record_run_state(st.session_state["active_thread_id"], res)
                            st.success("Customized plan applied and executed.")
                            st.rerun()

        elif approval_status == "approved":
            st.markdown(
                """
                <span class="status-badge badge-approved">✅ Plan Authorized & Executed</span>
                """,
                unsafe_allow_html=True,
            )
            st.success(
                f"Workflow session (`{st.session_state['active_thread_id']}`) was approved and completed demonstration tool execution. "
                "View detailed execution records and measured financial outcomes in the **'⚡ Execution & Outcomes'** tab."
            )
        elif approval_status == "rejected":
            st.markdown(
                """
                <span class="status-badge badge-rejected">❌ Plan Rejected</span>
                """,
                unsafe_allow_html=True,
            )
            st.error(
                "This workflow run was rejected by the shop owner. Adhering to Human-in-the-Loop safety boundaries, ZERO tools were executed."
            )
        else:
            st.info(
                f"Current workflow status: `{w_status}`. No actions are currently awaiting decision."
            )


# -----------------------------------------------------------------------------
# SECTION 5: EXECUTION AND OUTCOMES (100% PRESERVED ORIGINAL OUTCOME ANALYSIS)
# -----------------------------------------------------------------------------
elif selected_idx == 5:
    st.title("⚡ Tool Execution & Measured Outcomes")
    st.markdown(
        f"Execution logs and post-intervention outcome analysis for **{SHOP_NAME}**."
    )

    app = st.session_state["workflow_app"]
    current_res = st.session_state["workflow_result"]
    if current_res is None:
        current_res = get_workflow_snapshot(app, st.session_state["active_thread_id"])
        if current_res:
            st.session_state["workflow_result"] = current_res

    if current_res is None or not current_res.get("execution_results"):
        st.info(
            f"No execution logs available yet for session `{st.session_state['active_thread_id']}`. "
            "Run a growth strategy in **'🤖 AI Growth Plan'** and approve it in **'✋ Human Approval'** to view outcomes."
        )
    else:
        exec_logs = current_res.get("execution_results", [])
        measured = current_res.get("measured_outcomes", {})
        learning = current_res.get("learning_summary", {})

        st.caption(
            "⚠️ **Simulated Demonstration Notice:** All tool actions are safe local demonstrations executed using synthetic store data. No real-world money was spent and no external API orders were placed."
        )

        st.subheader(f"🛠️ Demonstration Tool Execution Logs ({len(exec_logs)} Tools)")
        for log in exec_logs:
            is_ok = log.get("status") == "success"
            status_icon = "✅" if is_ok else "⚠️"
            ts_text = (
                f" | Executed At: `{log.get('executed_at', 'Simulated Run')}`"
                if log.get("executed_at")
                else ""
            )
            with st.container():
                st.markdown(
                    f"**{status_icon} {log.get('action_name')}** (`{log.get('tool_name')}`)"
                )
                st.caption(
                    f"Status: **{log.get('status', 'unknown').upper()}** | Action ID: `{log.get('action_id')}`{ts_text}"
                )
                st.markdown(f"> {log.get('message', log.get('error'))}")
                if log.get("details"):
                    with st.expander("View Output Details"):
                        st.json(log.get("details"))
                st.markdown("---")

        st.subheader("📈 Financial Impact & Goal Achievement")
        o1, o2, o3, o4 = st.columns(4)
        with o1:
            st.metric(
                label="Historical Monthly Baseline",
                value=f"₹{measured.get('actual_historical_monthly_avg_inr', 0):,.2f}",
            )
        with o2:
            st.metric(
                label="Simulated Monthly Uplift",
                value=f"+₹{measured.get('total_simulated_revenue_uplift_inr', 0):,.2f}",
                delta="Simulated projection",
            )
        with o3:
            st.metric(
                label="Projected New Monthly Run Rate",
                value=f"₹{measured.get('projected_monthly_run_rate_inr', 0):,.2f}",
                delta=f"Target: ₹{measured.get('target_monthly_revenue_inr', 10000):,.0f}",
            )
        with o4:
            rem_gap = measured.get("remaining_projected_gap_inr", 0)
            st.metric(
                label="Remaining Projected Gap",
                value=f"₹{rem_gap:,.2f}",
                delta="Target Met in Simulation" if rem_gap == 0 else "Gap Remaining",
                delta_color="normal" if rem_gap == 0 else "inverse",
            )

        st.caption(f"ℹ️ {measured.get('disclaimer', '')}")

        if learning:
            st.markdown("---")
            st.subheader("🧠 Learning & Replanning Strategy")
            l_col1, l_col2 = st.columns([1, 2])
            with l_col1:
                st.markdown(
                    f"**Iteration Completed:** {learning.get('iteration_completed', 1)}"
                )
                st.markdown(
                    f"**Replanning Needed:** `{'Yes' if learning.get('should_replan') else 'No'}`"
                )
            with l_col2:
                st.markdown(f"**Strategic Decision:** {learning.get('decision_reason', '')}")

            learnings = learning.get("key_learnings", [])
            if learnings:
                st.markdown("**Key Strategy Learnings:**")
                for item in learnings:
                    st.markdown(f"- {item}")


# -----------------------------------------------------------------------------
# SECTION 6: RUN HISTORY (100% PRESERVED PERSISTED AUDIT TRAIL)
# -----------------------------------------------------------------------------
elif selected_idx == 6:
    st.title("📜 Persisted Workflow Execution History")
    st.markdown(
        f"Audit trail of LangGraph checkpointed runs for **{SHOP_NAME}** stored in `database/dukaanpilot.db`."
    )

    runs = list_all_runs()

    if not runs:
        st.info(
            "No workflow runs recorded yet. Execute a workflow in **'🤖 AI Growth Plan'** to generate history."
        )
    else:
        df_runs = pd.DataFrame(runs)
        st.dataframe(
            df_runs[
                [
                    "thread_id",
                    "updated_at",
                    "workflow_status",
                    "approval_status",
                    "actions_count",
                    "simulated_uplift_inr",
                    "summary_text",
                ]
            ].rename(
                columns={
                    "thread_id": "Thread / Run ID",
                    "updated_at": "Last Updated",
                    "workflow_status": "Status",
                    "approval_status": "Approval",
                    "actions_count": "Actions",
                    "simulated_uplift_inr": "Simulated Uplift (₹)",
                    "summary_text": "Outcome Summary",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )

        st.markdown("---")
        st.subheader("Reopen Saved Workflow Session")

        selected_thread = st.selectbox(
            "Select Run / Thread ID to restore:",
            [r["thread_id"] for r in runs],
            index=0,
        )

        load_run_btn = st.button(
            "🔄 Reopen Selected Session to Active State", type="primary"
        )
        if load_run_btn:
            st.session_state["active_thread_id"] = selected_thread
            app = st.session_state["workflow_app"]
            snapshot = get_workflow_snapshot(app, selected_thread)

            if snapshot:
                st.session_state["workflow_result"] = snapshot
                if snapshot.get("__interrupt__"):
                    st.info(
                        f"Session `{selected_thread}` restored. It is currently paused awaiting Human Approval."
                    )
                else:
                    st.success(
                        f"Session `{selected_thread}` restored. Status: `{snapshot.get('workflow_status')}`."
                    )
            else:
                st.session_state["workflow_result"] = None
                st.warning(f"Thread `{selected_thread}` selected, but no snapshot values found.")
            st.rerun()
