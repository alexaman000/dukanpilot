"""Plain-language business insights and bilingual translations for small shopkeepers.

Designed specifically for DukaanPilot AI & Sneha Bhandar (Booty More, Ranchi).
Translates technical data-analysis into actionable, everyday retail language.
Supports both English and Hindi.
"""

from typing import Any, Dict, List, Optional
import pandas as pd
from workflow.config import BASELINE_MONTHLY_REVENUE, TARGET_MONTHLY_REVENUE


# -----------------------------------------------------------------------------
# Bilingual UI & Domain Dictionary
# -----------------------------------------------------------------------------
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "en": {
        "greeting": "Namaste! Here is your shop's business update.",
        "subtitle": "Clear, action-oriented business advice for Sneha Bhandar.",
        "lang_selector": "Language / भाषा",
        "demo_disclaimer": "⚠️ Demonstration Notice: All figures are calculated from synthetic store records for demonstration. Baseline (₹8,000) and Target (₹10,000) are benchmark settings.",
        "simulated_action_notice": "ℹ️ Simulated Demonstration: All actions are executed locally on sample records. No real money or actual store orders are placed.",
        
        # Summary KPI cards
        "current_monthly_sales": "Current Monthly Sales",
        "monthly_goal": "Monthly Goal",
        "remaining_to_goal": "Remaining to Goal",
        "overall_status": "Overall Shop Status",
        "key_issue": "Most Important Issue",
        "recommended_action": "Recommended Next Action",
        
        # Status labels
        "status_doing_well": "Doing well",
        "status_needs_attention": "Needs attention",
        "status_action_required": "Action required",
        
        # Section titles
        "what_to_do_next": "What should I do next?",
        "plain_insights_title": "Shop Insights in Plain Language",
        "detailed_reports_title": "📊 Detailed Reports & Charts (Optional)",
        "worker_activity_title": "🤖 DukaanPilot AI Activity",
        
        # Timeline stage names
        "stage_data": "1. Reviewing business data",
        "stage_plan": "2. Preparing recommendations",
        "stage_approval": "3. Waiting for owner approval",
        "stage_execution": "4. Executing approved actions",
        "stage_learning": "5. Reviewing available results",
        
        # Timeline status badges
        "badge_done": "Completed",
        "badge_waiting": "Waiting for You",
        "badge_running": "In Progress",
        "badge_pending": "Not Started Yet",
        "badge_rejected": "Cancelled by Owner",
        
        # Approval buttons
        "btn_run_planner": "🚀 Ask DukaanPilot for Recommendations",
        "btn_approve_all": "✅ Approve All Recommendations",
        "btn_reject_all": "❌ Reject Recommendations",
        "btn_revise": "✏️ Choose Specific Actions",
        "btn_apply_revision": "Apply Selected Actions & Resume",
        "approval_paused_alert": "The AI has prepared growth recommendations for your shop. Please review and decide below.",
        "approval_granted_alert": "You have approved these actions. DukaanPilot has completed the demonstration simulation.",
        "approval_rejected_alert": "You declined these recommendations. No tools were executed.",
        
        # Action details
        "what_ai_suggests": "What DukaanPilot Suggests",
        "why_it_suggests": "Why this helps your shop",
        "expected_benefit": "Expected Benefit",
        "cost_and_risk": "Estimated Cost & Caution",
        "ai_estimate_tag": "AI Estimate",
        "cost_label": "Cost",
        "risk_label": "Caution",
        "no_active_plan": "No active recommendations yet. Click 'Ask DukaanPilot for Recommendations' above to get fresh advice.",
    },
    "hi": {
        "greeting": "नमस्ते! यह आपकी दुकान का ताज़ा व्यापार अपडेट है।",
        "subtitle": "स्नेहा भंडार के लिए सरल और स्पष्ट व्यापारिक मार्गदर्शन।",
        "lang_selector": "भाषा / Language",
        "demo_disclaimer": "⚠️ प्रदर्शन सूचना: सभी आंकड़े प्रदर्शन के लिए कृत्रिम (सिंथेटिक) रिकॉर्ड्स पर आधारित हैं। आधार बिक्री (₹8,000) और लक्ष्य (₹10,000) डेमो सेटिंग्स हैं।",
        "simulated_action_notice": "ℹ️ सुरक्षित सिमुलेशन: सभी उपकरण केवल परीक्षण के लिए स्थानीय रूप से चलाए जाते हैं। कोई वास्तविक धन खर्च नहीं होता।",
        
        # Summary KPI cards
        "current_monthly_sales": "वर्तमान मासिक बिक्री",
        "monthly_goal": "मासिक लक्ष्य",
        "remaining_to_goal": "लक्ष्य तक पहुँचने के लिए बाकी",
        "overall_status": "दुकान की समग्र स्थिति",
        "key_issue": "सबसे ज़रूरी समस्या",
        "recommended_action": "अगला अनुशंसित कदम",
        
        # Status labels
        "status_doing_well": "सब ठीक है",
        "status_needs_attention": "ध्यान देने की ज़रूरत",
        "status_action_required": "तुरंत कार्रवाई आवश्यक",
        
        # Section titles
        "what_to_do_next": "मुझे आगे क्या करना चाहिए?",
        "plain_insights_title": "आपकी दुकान की सरल बातें",
        "detailed_reports_title": "📊 विस्तृत रिपोर्ट और चार्ट (वैकल्पिक)",
        "worker_activity_title": "🤖 दुकानपायलट AI की कार्यप्रणाली",
        
        # Timeline stage names
        "stage_data": "1. दुकान के डेटा की समीक्षा",
        "stage_plan": "2. विकास सुझाव तैयार करना",
        "stage_approval": "3. दुकानदार की मंजूरी का इंतज़ार",
        "stage_execution": "4. स्वीकृत सुझावों को लागू करना",
        "stage_learning": "5. नतीजों और प्रभाव की समीक्षा",
        
        # Timeline status badges
        "badge_done": "पूरा हुआ",
        "badge_waiting": "आपकी मंजूरी का इंतज़ार",
        "badge_running": "जारी है",
        "badge_pending": "अभी शुरू नहीं हुआ",
        "badge_rejected": "दुकानदार द्वारा अस्वीकृत",
        
        # Approval buttons
        "btn_run_planner": "🚀 दुकानपायलट से नए सुझाव मांगें",
        "btn_approve_all": "✅ सभी सुझाव मंजूर करें",
        "btn_reject_all": "❌ सुझाव अस्वीकार करें",
        "btn_revise": "✏️ अपनी पसंद के सुझाव चुनें",
        "btn_apply_revision": "चुने गए सुझाव लागू करें",
        "approval_paused_alert": "AI ने आपकी दुकान के लिए सुझाव तैयार किए हैं। कृपया नीचे देखकर अपना निर्णय लें।",
        "approval_granted_alert": "आपने ये सुझाव मंजूर कर लिए हैं। दुकानपायलट ने सिमुलेशन पूरा कर लिया है।",
        "approval_rejected_alert": "आपने ये सुझाव अस्वीकार कर दिए। कोई भी उपकरण नहीं चलाया गया।",
        
        # Action details
        "what_ai_suggests": "दुकानपायलट का सुझाव",
        "why_it_suggests": "यह आपकी दुकान के लिए क्यों जरूरी है",
        "expected_benefit": "अनुमानित लाभ",
        "cost_and_risk": "अनुमानित खर्च और सावधानी",
        "ai_estimate_tag": "AI अनुमान",
        "cost_label": "खर्च",
        "risk_label": "सावधानी",
        "no_active_plan": "अभी कोई सक्रिय सुझाव नहीं है। नया मार्गदर्शन पाने के लिए ऊपर 'दुकानपायलट से नए सुझाव मांगें' पर क्लिक करें।",
    },
}


def t(key: str, lang: str = "en") -> str:
    """Retrieve localized string with fallback to English."""
    lang_dict = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
    return lang_dict.get(key, TRANSLATIONS["en"].get(key, key))


# -----------------------------------------------------------------------------
# Shopkeeper Status Determination
# -----------------------------------------------------------------------------
def get_shopkeeper_status(analyst: Any, lang: str = "en") -> Dict[str, str]:
    """Calculate clear text status indicator (Doing well / Needs attention / Action required).
    
    Evaluates:
    - Monthly revenue target gap
    - Low-stock inventory deficit
    - Net profitability
    """
    growth = analyst.compare_to_growth_target(
        baseline_monthly=BASELINE_MONTHLY_REVENUE,
        target_monthly=TARGET_MONTHLY_REVENUE,
    )
    low_stock_df = analyst.get_low_stock_products()
    net_profit_data = analyst.get_net_profit()
    
    gap = growth.get("gap_to_target_inr", 0.0)
    low_stock_count = len(low_stock_df) if isinstance(low_stock_df, pd.DataFrame) else 0
    net_profit = net_profit_data.get("estimated_net_profit", 0.0)
    
    # Critical condition: large gap (> ₹2,500) or severe stockout (>= 3 items) or loss
    if gap > 2500.0 or low_stock_count >= 3 or net_profit < 0:
        code = "action_required"
        label = t("status_action_required", lang)
        if lang == "hi":
            desc = f"तुरंत कार्रवाई आवश्यक: बिक्री लक्ष्य से ₹{gap:,.0f} पीछे है और {low_stock_count} जरूरी सामान का स्टॉक खतरनाक रूप से कम है।"
        else:
            desc = f"Action required: Sales are ₹{gap:,.0f} below target and {low_stock_count} items are running out of stock."
    # Moderate condition: any gap or any low stock
    elif gap > 0.0 or low_stock_count > 0:
        code = "needs_attention"
        label = t("status_needs_attention", lang)
        if lang == "hi":
            desc = f"ध्यान देने की ज़रूरत: मासिक लक्ष्य तक पहुँचने के लिए ₹{gap:,.0f} और चाहिए, तथा {low_stock_count} सामान को दोबारा मंगाने की ज़रूरत है।"
        else:
            desc = f"Needs attention: Shop is ₹{gap:,.0f} away from monthly target, with {low_stock_count} items below safety stock."
    # Healthy condition
    else:
        code = "doing_well"
        label = t("status_doing_well", lang)
        if lang == "hi":
            desc = "सब ठीक है: दुकान अपने लक्ष्य पर सही चल रही है और इन्वेंट्री का स्तर सुरक्षित है।"
        else:
            desc = "Doing well: Shop is on track to meet its revenue goal and inventory levels are healthy."
            
    return {
        "code": code,
        "label": label,
        "description": desc,
    }


# -----------------------------------------------------------------------------
# Simple Business Summary
# -----------------------------------------------------------------------------
def get_shopkeeper_summary(analyst: Any, lang: str = "en") -> Dict[str, Any]:
    """Provide top-level friendly summary with calculated metrics from synthetic data."""
    growth = analyst.compare_to_growth_target(
        baseline_monthly=BASELINE_MONTHLY_REVENUE,
        target_monthly=TARGET_MONTHLY_REVENUE,
    )
    status_info = get_shopkeeper_status(analyst, lang)
    low_stock_df = analyst.get_low_stock_products()
    
    actual_monthly = growth.get("actual_monthly_avg_inr", 8000.0)
    target_monthly = growth.get("target_monthly_inr", 10000.0)
    gap = growth.get("gap_to_target_inr", 0.0)
    
    # Identify top issue
    if isinstance(low_stock_df, pd.DataFrame) and not low_stock_df.empty:
        low_names = ", ".join(low_stock_df["product_name"].head(2).tolist())
        if lang == "hi":
            key_issue = f"कम स्टॉक: {len(low_stock_df)} सामान ({low_names}) जल्द खत्म होने वाले हैं।"
            recommended_action = "दुकानपायलट चलाकर जरूरी सामान मंगवाएं और बिक्री बढ़ाने के लिए वीकेंड ऑफर जोड़ें।"
        else:
            key_issue = f"Low stock in {len(low_stock_df)} items ({low_names})."
            recommended_action = "Restock fast-selling items and activate a weekend snack discount."
    elif gap > 0:
        if lang == "hi":
            key_issue = f"मासिक बिक्री लक्ष्य से ₹{gap:,.0f} कम है।"
            recommended_action = "दुकानपायलट से कॉम्बो ऑफर और ग्राहक संदेश योजना बनवाएं।"
        else:
            key_issue = f"Monthly revenue is ₹{gap:,.0f} behind the ₹{target_monthly:,.0f} milestone."
            recommended_action = "Run DukaanPilot to create combo packs and customer visit reminders."
    else:
        if lang == "hi":
            key_issue = "वर्तमान में कोई गंभीर समस्या नहीं है।"
            recommended_action = "ग्राहकों को बनाए रखने के लिए नए सामान और नियमित ऑफर्स जारी रखें।"
        else:
            key_issue = "No critical issues detected."
            recommended_action = "Maintain regular promotions and customer loyalty follow-ups."
            
    return {
        "greeting": t("greeting", lang),
        "subtitle": t("subtitle", lang),
        "current_monthly_sales": actual_monthly,
        "monthly_goal": target_monthly,
        "remaining_gap": gap,
        "status": status_info,
        "key_issue": key_issue,
        "recommended_action": recommended_action,
        "disclaimer": t("demo_disclaimer", lang),
    }


# -----------------------------------------------------------------------------
# Plain-Language Insights Generator
# -----------------------------------------------------------------------------
def get_plain_language_insights(analyst: Any, lang: str = "en") -> List[Dict[str, str]]:
    """Translate analytical results into simple, understandable everyday retail statements.
    
    Dynamically grounded in dataset calculations:
    1. Sales vs monthly goal
    2. Category concentration
    3. Slow-moving products needing promotion
    4. Low-stock inventory needing reordering
    5. Plain-language profitability
    """
    insights: List[Dict[str, str]] = []
    
    # 1. Sales vs Monthly Goal
    growth = analyst.compare_to_growth_target(
        baseline_monthly=BASELINE_MONTHLY_REVENUE,
        target_monthly=TARGET_MONTHLY_REVENUE,
    )
    actual = growth.get("actual_monthly_avg_inr", 8000.0)
    target = growth.get("target_monthly_inr", 10000.0)
    gap = growth.get("gap_to_target_inr", 0.0)
    
    if gap > 0:
        weekly_need = gap / 4.0
        if lang == "hi":
            text_goal = (
                f"आपकी औसत मासिक बिक्री **₹{actual:,.0f}** है, जो आपके **₹{target:,.0f}** के लक्ष्य से "
                f"**₹{gap:,.0f} कम** है। लक्ष्य पूरा करने के लिए हर हफ्ते लगभग **₹{weekly_need:,.0f}** अधिक बिक्री की ज़रूरत है।"
            )
        else:
            text_goal = (
                f"Your measured monthly sales (**₹{actual:,.0f}**) are **₹{gap:,.0f} below** your monthly goal of **₹{target:,.0f}**. "
                f"You need about **₹{weekly_need:,.0f}** in extra sales each week to reach it."
            )
    else:
        if lang == "hi":
            text_goal = f"बधाई हो! आपकी मासिक बिक्री (**₹{actual:,.0f}**) आपके **₹{target:,.0f}** के लक्ष्य को पार कर चुकी है।"
        else:
            text_goal = f"Great work! Your monthly sales (**₹{actual:,.0f}**) have achieved your target of **₹{target:,.0f}**."
            
    insights.append({
        "topic": "Goal Progress" if lang == "en" else "लक्ष्य की प्रगति",
        "icon": "🎯",
        "text": text_goal,
    })
    
    # 2. Category Concentration
    cat_df = analyst.get_revenue_by_category()
    if isinstance(cat_df, pd.DataFrame) and not cat_df.empty:
        top_cat_row = cat_df.iloc[0]
        top_cat = top_cat_row["category"]
        share = top_cat_row.get("share_pct", 0.0)
        cat_rev = top_cat_row.get("revenue", 0.0)
        
        # Friendly category names in Hindi
        cat_hi = {
            "Grains & Staples": "अनाज और दालें",
            "Snacks & Packaged Foods": "नाश्ता और बिस्कुट",
            "Edible Oils & Spices": "तेल और मसाले",
            "Dairy & Bakery": "दूध और बेकरी",
            "Personal Care & Hygiene": "साबुन और व्यक्तिगत देखभाल",
            "Household & Cleaning": "सफाई का सामान",
            "Beverages": "चाय और कॉफी",
        }.get(top_cat, top_cat)
        
        if lang == "hi":
            text_cat = (
                f"आपकी सबसे ज़्यादा कमाई (**{share:.1f}%**) **'{cat_hi}'** श्रेणी से आती है (लगभग ₹{cat_rev:,.0f})। "
                f"यह आपकी दुकान का मुख्य आधार है।"
            )
        else:
            text_cat = (
                f"Most of your shop's sales (**{share:.1f}%**) come from **'{top_cat}'** (₹{cat_rev:,.0f}). "
                f"This category is your biggest revenue driver."
            )
            
        insights.append({
            "topic": "Top Category" if lang == "en" else "मुख्य बिक्री श्रेणी",
            "icon": "🏆",
            "text": text_cat,
        })
        
    # 3. Slow-Moving Products
    slow_df = analyst.get_slow_moving_products(bottom_n=3)
    if isinstance(slow_df, pd.DataFrame) and not slow_df.empty:
        slow_names = ", ".join(slow_df["product_name"].head(2).tolist())
        if lang == "hi":
            text_slow = (
                f"ये सामान बहुत धीमी गति से बिक रहे हैं: **{slow_names}**। "
                f"इन पर छोटा डिस्काउंट या कॉम्बो ऑफर देकर शेल्फ खाली करने पर विचार करें।"
            )
        else:
            text_slow = (
                f"These products are selling slowly: **{slow_names}**. "
                f"Consider a small 5–10% promotion or bundle deal to clear shelf space."
            )
        insights.append({
            "topic": "Slow Items" if lang == "en" else "धीमी बिक्री वाले सामान",
            "icon": "🐢",
            "text": text_slow,
        })
        
    # 4. Low-Stock Inventory Alerts
    low_df = analyst.get_low_stock_products()
    if isinstance(low_df, pd.DataFrame) and not low_df.empty:
        low_names = ", ".join(low_df["product_name"].head(2).tolist())
        count = len(low_df)
        if lang == "hi":
            text_low = (
                f"ये लोकप्रिय सामान जल्द खत्म हो सकते हैं: **{low_names}** (कुल {count} सामान)। "
                f"नियमित ग्राहकों को खाली हाथ लौटने से बचाने के लिए इन्हें तुरंत मंगवाएं।"
            )
        else:
            text_low = (
                f"These popular products may need restocking soon: **{low_names}** ({count} items low). "
                f"Restock soon so loyal customers don't find empty shelves."
            )
        insights.append({
            "topic": "Stock Alert" if lang == "en" else "स्टॉक चेतावनी",
            "icon": "⚠️",
            "text": text_low,
        })
    else:
        if lang == "hi":
            text_low = "आपकी दुकान की इन्वेंट्री स्वस्थ है। किसी भी जरूरी सामान की कमी नहीं है।"
        else:
            text_low = "Your inventory stock levels are healthy. No items are below safety reorder limits."
        insights.append({
            "topic": "Stock Health" if lang == "en" else "इन्वेंट्री की स्थिति",
            "icon": "📦",
            "text": text_low,
        })
        
    # 5. Everyday Profitability (No jargon)
    np_data = analyst.get_net_profit()
    rev = np_data.get("total_revenue", 1.0)
    net_p = np_data.get("estimated_net_profit", 0.0)
    margin = (net_p / rev * 100.0) if rev > 0 else 0.0
    
    if lang == "hi":
        text_profit = (
            f"थोक खरीद लागत और दुकान के नियमित खर्चों के बाद, हर **₹100 की बिक्री पर आपके पास लगभग ₹{margin:.0f} बचते हैं** "
            f"(यह आपका शुद्ध मुनाफा है)।"
        )
    else:
        text_profit = (
            f"After paying for wholesale stock and daily shop running expenses, your shop keeps about "
            f"**₹{margin:.0f} for every ₹100 of sales** (this is your net profit margin)."
        )
    insights.append({
        "topic": "Profitability" if lang == "en" else "मुनाफे की स्थिति",
        "icon": "💰",
        "text": text_profit,
    })
    
    return insights


# -----------------------------------------------------------------------------
# AI Worker Activity Timeline
# -----------------------------------------------------------------------------
def get_workflow_timeline(
    current_res: Optional[Dict[str, Any]], lang: str = "en"
) -> List[Dict[str, Any]]:
    """Generate accurate 5-stage timeline from actual LangGraph workflow state.
    
    Stages:
    1. Reviewing business data
    2. Preparing recommendations
    3. Waiting for owner approval
    4. Executing approved simulated actions
    5. Reviewing available results
    """
    # Defaults: not started
    timeline = [
        {
            "stage_id": 1,
            "title": t("stage_data", lang),
            "status": "pending",
            "badge": t("badge_pending", lang),
            "note": "Ready to inspect sales records." if lang == "en" else "बिक्री रिकॉर्ड्स जांचने के लिए तैयार।",
        },
        {
            "stage_id": 2,
            "title": t("stage_plan", lang),
            "status": "pending",
            "badge": t("badge_pending", lang),
            "note": "Ready to generate growth plan." if lang == "en" else "योजना तैयार करने के लिए तैयार।",
        },
        {
            "stage_id": 3,
            "title": t("stage_approval", lang),
            "status": "pending",
            "badge": t("badge_pending", lang),
            "note": "Awaiting generated recommendations." if lang == "en" else "सुझावों का इंतज़ार।",
        },
        {
            "stage_id": 4,
            "title": t("stage_execution", lang),
            "status": "pending",
            "badge": t("badge_pending", lang),
            "note": "No actions authorized yet." if lang == "en" else "अभी कोई कार्रवाई अधिकृत नहीं है।",
        },
        {
            "stage_id": 5,
            "title": t("stage_learning", lang),
            "status": "pending",
            "badge": t("badge_pending", lang),
            "note": "Awaiting tool execution outcomes." if lang == "en" else "लागू होने के बाद नतीजों का इंतज़ार।",
        },
    ]
    
    if current_res is None:
        return timeline
        
    interrupts = current_res.get("__interrupt__", [])
    approval_status = current_res.get("approval_status", "pending")
    workflow_status = current_res.get("workflow_status", "pending")
    exec_results = current_res.get("execution_results", [])
    
    # Stage 1: Data analysis completed if business_metrics exists
    if current_res.get("business_metrics"):
        timeline[0]["status"] = "completed"
        timeline[0]["badge"] = t("badge_done", lang)
        timeline[0]["note"] = "Shop sales and inventory records analyzed." if lang == "en" else "बिक्री और इन्वेंट्री का विश्लेषण पूरा हुआ।"
        
    # Stage 2: Recommendations prepared if proposed_actions exists
    has_proposed = bool(current_res.get("proposed_actions") or interrupts)
    if has_proposed:
        timeline[1]["status"] = "completed"
        timeline[1]["badge"] = t("badge_done", lang)
        timeline[1]["note"] = "Grounded growth actions formulated and validated." if lang == "en" else "सुझाव तैयार किए गए और जांचे गए।"
        
    # Stage 3: Approval status
    is_paused = bool(interrupts) or (workflow_status in ("validated", "awaiting_approval") and approval_status == "pending")
    
    if is_paused:
        timeline[2]["status"] = "waiting"
        timeline[2]["badge"] = t("badge_waiting", lang)
        timeline[2]["note"] = "Pausing for shop owner authorization." if lang == "en" else "दुकानदार के निर्णय की प्रतीक्षा में।"
    elif approval_status == "approved":
        timeline[2]["status"] = "completed"
        timeline[2]["badge"] = t("badge_done", lang)
        timeline[2]["note"] = "Owner authorized proposed actions." if lang == "en" else "दुकानदार द्वारा सुझाव स्वीकृत।"
    elif approval_status == "rejected":
        timeline[2]["status"] = "rejected"
        timeline[2]["badge"] = t("badge_rejected", lang)
        timeline[2]["note"] = "Owner declined proposed actions." if lang == "en" else "दुकानदार ने सुझाव अस्वीकार कर दिए।"
        
    # Stage 4: Execution status
    if approval_status == "approved" and exec_results:
        timeline[3]["status"] = "completed"
        timeline[3]["badge"] = t("badge_done", lang)
        timeline[3]["note"] = f"{len(exec_results)} simulated tools executed safely." if lang == "en" else f"{len(exec_results)} उपकरण सुरक्षित रूप से चलाए गए।"
    elif approval_status == "rejected":
        timeline[3]["status"] = "skipped"
        timeline[3]["badge"] = "Skipped" if lang == "en" else "छोड़ दिया गया"
        timeline[3]["note"] = "Zero tools executed (Shopkeeper safety)." if lang == "en" else "शून्य उपकरण चलाए गए (दुकानदार सुरक्षा)।"
        
    # Stage 5: Learning & measured outcomes
    if current_res.get("measured_outcomes") and workflow_status == "completed":
        timeline[4]["status"] = "completed"
        timeline[4]["badge"] = t("badge_done", lang)
        timeline[4]["note"] = "Financial uplift measured and strategy reviewed." if lang == "en" else "बिक्री में सुधार का मूल्यांकन पूरा हुआ।"
    elif approval_status == "rejected":
        timeline[4]["status"] = "skipped"
        timeline[4]["badge"] = "Skipped" if lang == "en" else "छोड़ दिया गया"
        timeline[4]["note"] = "Run ended without tool execution." if lang == "en" else "सत्र बिना किसी कार्रवाई के समाप्त हुआ।"
        
    return timeline


# -----------------------------------------------------------------------------
# Plain-Language Action Adapter
# -----------------------------------------------------------------------------
def get_shopkeeper_action_view(action: Dict[str, Any], lang: str = "en") -> Dict[str, str]:
    """Translate technical action dictionary into shopkeeper-friendly terms."""
    tool_name = action.get("tool_name", "")
    raw_name = action.get("action_name", "")
    rationale = action.get("business_rationale", "")
    expected = action.get("expected_impact", "")
    cost = action.get("estimated_cost", 0.0)
    risk = action.get("risks_or_constraints", "Low risk")
    
    # Friendly action type
    if "promotion" in tool_name:
        friendly_type = "Special Discount Offer" if lang == "en" else "विशेष छूट ऑफर"
    elif "bundle" in tool_name:
        friendly_type = "Combo Savings Pack" if lang == "en" else "कॉम्बो बचत पैक"
    elif "reorder" in tool_name:
        friendly_type = "Restock Fast-Moving Stock" if lang == "en" else "कम स्टॉक वाला सामान मंगाना"
    elif "marketing" in tool_name:
        friendly_type = "Customer Announcement" if lang == "en" else "ग्राहकों को संदेश / सूचना"
    else:
        friendly_type = "Shop Improvement" if lang == "en" else "दुकान सुधार कदम"
        
    return {
        "title": f"{friendly_type}: {raw_name}",
        "what": raw_name,
        "why": rationale,
        "benefit": f"{expected} ({t('ai_estimate_tag', lang)})",
        "cost": f"₹{cost:,.2f}" if cost > 0 else ("₹0 (No upfront cost)" if lang == "en" else "₹0 (कोई अतिरिक्त खर्च नहीं)"),
        "risk": risk,
    }
