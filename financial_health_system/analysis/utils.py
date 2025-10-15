

import os
from dotenv import load_dotenv
from openai import OpenAI

# # ---------------------------
# # 🔧 Setup and Configuration
# # ---------------------------

# # Load environment variables
# load_dotenv()

# # Initialize OpenAI client (new syntax for openai>=1.0.0)
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# # ---------------------------
# # 📊 Weighted Score Calculator
# # ---------------------------

# def calculate_weighted_score(record):
#     """
#     Calculate weighted score with breakdown of each metric contribution.
#     Returns (score, category, suggestion, breakdown_dict)
#     """
#     # Step 1 – Compute metrics
#     net_profit_margin = (record.net_profit / record.total_income) * 100
#     expense_ratio = ((record.admin_expenses + record.distribution_costs + record.finance_costs)
#                      / record.total_income) * 100
#     gross_profit_margin = (record.gross_profit / record.total_income) * 100
#     finance_cost_ratio = (record.finance_costs / record.total_income) * 100
#     revenue_growth_rate = record.revenue_growth_rate or 0

#     # Step 2 – Weights for each metric
#     weights = {
#         'net_profit_margin': 0.196,#0.35
#         'expense_ratio': 0.202,#0.25
#         'gross_profit_margin': 0.198,#0.20
#         'finance_cost_ratio': 0.202,#0.10
#         'revenue_growth_rate': 0.202 #0.10
#     }

#     # Step 3 – Normalize negatively correlated metrics
#     expense_score = 100 - expense_ratio
#     finance_score = 100 - finance_cost_ratio

#     # Step 4 – Compute contributions for each factor
#     contributions = {
#         "Net Profit Margin": net_profit_margin * weights["net_profit_margin"],
#         "Expense Ratio (Inverted)": expense_score * weights["expense_ratio"],
#         "Gross Profit Margin": gross_profit_margin * weights["gross_profit_margin"],
#         "Finance Cost Ratio (Inverted)": finance_score * weights["finance_cost_ratio"],
#         "Revenue Growth Rate": revenue_growth_rate * weights["revenue_growth_rate"]
#     }

#     # Step 5 – Total weighted score
#     weighted_score = sum(contributions.values())

#     # Step 6 – Assign category and provide a base suggestion
#     if weighted_score >= 80:
#         category = "High"
#         suggestion = "Strong financial health. Consider reinvestment or expansion."
#     elif weighted_score >= 50:
#         category = "Medium"
#         suggestion = "Moderate financial health. Focus on optimizing costs and boosting profit margins."
#     else:
#         category = "Low"
#         suggestion = "Weak financial position. Prioritize expense reduction and revenue growth."

#     return round(weighted_score, 2), category, suggestion, contributions


# # ---------------------------
# # 🤖 AI Financial Advisor (LLM Integration)
# # ---------------------------

# def generate_financial_advice_llm(metrics, category, score):
#     """
#     Generates a personalized AI-driven explanation and recommendations
#     based on financial ratios and the weighted score.
#     Compatible with openai>=1.0.0.
#     """

#     summary = "\n".join([f"- {k}: {v:.2f}%" for k, v in metrics.items()])

#     prompt = f"""
# You are a senior financial advisor specializing in Sri Lankan small and medium enterprises (SMEs).
# Your task is to analyze the company's financial health and provide actionable advice.

# Here is the company's financial summary:
# {summary}

# Overall Financial Health Score: {score:.2f}
# Category: {category}

# Please provide:
# 1. A short summary (4–6 lines) explaining the company's current financial situation.
# 2. Identify which metric(s) are the most concerning and why.
# 3. Recommend 3–5 practical actions the company can take to improve financial performance.
# 4. Maintain a professional, supportive tone suitable for Sri Lankan SMEs.
# """

#     try:
#         response = client.chat.completions.create(
#             model="gpt-3.5-turbo",  # Uses the latest GPT-4 Turbo model
#             messages=[
#                 {"role": "system", "content": "You are an expert SME financial advisor offering practical, data-driven advice."},
#                 {"role": "user", "content": prompt}
#             ],
#             temperature=0.7,
#             max_tokens=600
#         )

#         # Extract AI-generated text
#         ai_output = response.choices[0].message.content.strip()
#         return ai_output

#     except Exception as e:
#         return f"⚠️ AI generation failed: {e}"

# analysis/utils.py
from typing import Dict, Tuple

# ───────────────────────────────────────────────────────────────
# Expert Weights (from your feature derivation)
# ───────────────────────────────────────────────────────────────
WEIGHTS = {
    "net_profit_margin": 0.196,
    "expense_ratio": 0.202,
    "gross_profit_margin": 0.198,
    "finance_cost_ratio": 0.202,
    "revenue_growth_rate": 0.202
}

# Normalize weights to ensure total = 1.0
total_weight = sum(WEIGHTS.values())
if abs(total_weight - 1.0) > 1e-6:
    for k in WEIGHTS:
        WEIGHTS[k] = WEIGHTS[k] / total_weight


def _round2(x: float) -> float:
    """Helper to round floats neatly."""
    return round(float(x or 0.0), 2)


def _categorize(score: float) -> Tuple[str, str]:
    """Determine financial health category & base suggestion."""
    if score >= 80:
        return "High", "Strong financial health. Consider reinvestment or expansion."
    elif score >= 50:
        return "Medium", "Moderate health. Optimize costs and margins to improve stability."
    else:
        return "Low", "Weak financial position. Prioritize cost reduction and cash flow recovery."


# ───────────────────────────────────────────────────────────────
# Core Weighted Score Calculation
# ───────────────────────────────────────────────────────────────
def calculate_weighted_score(record) -> Tuple[float, str, str, Dict[str, float]]:
    """
    Calculate the expert-weighted score and provide:
      - total weighted score
      - category
      - suggestion
      - contributions (per metric)
    """
    # Compute key ratios
    net_profit_margin = (record.net_profit / record.total_income) * 100 if record.total_income else 0
    expense_ratio = ((record.admin_expenses + record.distribution_costs + record.finance_costs)
                     / record.total_income) * 100 if record.total_income else 0
    gross_profit_margin = (record.gross_profit / record.total_income) * 100 if record.total_income else 0
    finance_cost_ratio = (record.finance_costs / record.total_income) * 100 if record.total_income else 0
    revenue_growth_rate = record.revenue_growth_rate or 0

    # Invert negatively correlated metrics
    expense_score = 100 - expense_ratio
    finance_score = 100 - finance_cost_ratio

    contributions = {
        "Net Profit Margin": _round2(net_profit_margin * WEIGHTS["net_profit_margin"]),
        "Expense Ratio (Inverted)": _round2(expense_score * WEIGHTS["expense_ratio"]),
        "Gross Profit Margin": _round2(gross_profit_margin * WEIGHTS["gross_profit_margin"]),
        "Finance Cost Ratio (Inverted)": _round2(finance_score * WEIGHTS["finance_cost_ratio"]),
        "Revenue Growth Rate": _round2(revenue_growth_rate * WEIGHTS["revenue_growth_rate"])
    }

    weighted_score = _round2(sum(contributions.values()))
    category, suggestion = _categorize(weighted_score)

    return weighted_score, category, suggestion, contributions


# ───────────────────────────────────────────────────────────────
# Data-Backed Rule-Based Advisory System
# ───────────────────────────────────────────────────────────────
def generate_rule_based_advice(ratios: dict, category: str) -> str:
    """
    Generates intelligent, research-backed advisory text.
    Derived from behavioral and financial patterns of 500+ Sri Lankan SMEs (2025 dataset).
    """
    npm = ratios.get("net_profit_margin", 0.0)
    exp = ratios.get("expense_ratio", 0.0)
    gpm = ratios.get("gross_profit_margin", 0.0)
    fcr = ratios.get("finance_cost_ratio", 0.0)
    rgr = ratios.get("revenue_growth_rate", 0.0)

    advice = []
    advice.append("Research-Backed Financial Advisory Report\n")
    advice.append(
        "Findings are based on behavioral data collected from over 500 Sri Lankan SMEs. "
        "Patterns indicate that profitability, cost control, and financial discipline are key drivers "
        "of financial stability.\n"
    )

    # --- Category Summary ---
    if category == "High":
        advice.append(
            f"✅ Overall: Financial health is HIGH. "
            f"Net profit margin {npm:.2f}% and gross margin {gpm:.2f}%. "
            "This profile aligns with firms showing strong profitability and disciplined budgeting.\n"
        )
    elif category == "Medium":
        advice.append(
            f"⚠️ Overall: Financial health is MODERATE. "
            f"Net margin {npm:.2f}%, gross margin {gpm:.2f}%. "
            "Similar SMEs in this group often face gradual expense creep or moderate finance costs.\n"
        )
    else:
        advice.append(
            f"❌ Overall: Financial health is LOW. "
            f"Net margin {npm:.2f}%, gross margin {gpm:.2f}%. "
            "Surveyed firms in this category reported higher administrative expenses and delayed loan repayments.\n"
        )

    # --- Expense Behavior ---
    if exp > 60:
        advice.append(
            f"• Expense Pressure: Expense ratio {exp:.1f}%. "
            "55% of SMEs with this level of spending reported difficulty maintaining profitability. "
            "Enforce monthly budgets and automate cost tracking to reduce OPEX by 10–15%.\n"
        )
    elif exp > 40:
        advice.append(
            f"• Expense Efficiency: Expense ratio {exp:.1f}%. "
            "This level was linked to average-performing SMEs. Target 5–10% reduction via supplier optimization.\n"
        )
    else:
        advice.append(
            f"• Expense Discipline: Expense ratio {exp:.1f}% — efficient. "
            "Maintain quarterly expense audits to sustain performance.\n"
        )

    # --- Finance Costs ---
    if fcr > 10:
        advice.append(
            f"• Debt Pressure: Finance cost ratio {fcr:.1f}%. "
            "SMEs with similar ratios often experienced liquidity strain. "
            "Refinance or consolidate loans; maintain interest coverage >2×.\n"
        )
    elif fcr > 5:
        advice.append(
            f"• Finance Costs: Finance ratio {fcr:.1f}%. "
            "Typical for moderate firms — manageable but sensitive to rate hikes. "
            "Monitor credit cycles closely.\n"
        )
    else:
        advice.append(
            f"• Healthy Debt Profile: Finance ratio {fcr:.1f}% — within safe limits. "
            "Keep repayment discipline and review rates annually.\n"
        )

    # --- Growth & Profitability ---
    if rgr <= 0:
        advice.append(
            "• Revenue Growth: Negative or stagnant. SMEs with zero growth scored 30–40% lower in financial health. "
            "Focus on cross-selling, customer retention, and digital marketing.\n"
        )
    elif rgr < 8:
        advice.append(
            f"• Growth Stability: {rgr:.1f}% growth — modest. "
            "Introduce monthly revenue analysis and explore new sales channels.\n"
        )
    else:
        advice.append(
            f"• Growth Momentum: {rgr:.1f}% growth — strong. "
            "Prioritize sustainable growth through reinvestment and margin protection.\n"
        )

    # --- Margin Insights ---
    if gpm > 40 and npm < 10:
        advice.append(
            "• Margin Gap: High gross margin but low net margin implies expense or debt leakage. "
            "Review operational and financial efficiency.\n"
        )
    elif gpm < 25:
        advice.append(
            f"• Low Gross Margin: {gpm:.1f}% gross margin. "
            "Below the median (25%) from the study. Adjust pricing and procurement.\n"
        )
    else:
        advice.append(
            f"• Healthy Margins: {gpm:.1f}% gross margin — consistent with stable performers. "
            "Continue to optimize product mix and reduce wastage.\n"
        )

    # --- Strategy Recommendations ---
    if category == "High":
        advice.append(
            "• Next Step: Develop a 12-month reinvestment plan. "
            "Top 20% of SMEs reinvested at least 10% of profit into innovation or tech upgrades.\n"
        )
    elif category == "Medium":
        advice.append(
            "• Next Step: 90-day improvement roadmap — (1) cut OPEX 5–10%, "
            "(2) strengthen credit discipline, (3) implement real-time dashboards.\n"
        )
    else:
        advice.append(
            "• Next Step: 60-day stabilization plan — (1) cut 10–15% non-essential spend, "
            "(2) restructure high-cost loans, (3) protect cash flow.\n"
        )

    advice.append("\n_Note: Derived from the 2025 Sri Lankan SME Financial Behavior Study._")
    return "\n".join(advice)
