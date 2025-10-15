# import pandas as pd
# from django.shortcuts import render
# from .models import FinancialRecord, FinancialScore
# from .utils import calculate_weighted_score, generate_financial_advice_llm  # <-- new import

# def get_value(df, keywords):
#     """
#     Search entire DataFrame for a keyword, then return the rightmost numeric value in that row.
#     Works even if label is in column D and value in column H (or elsewhere).
#     """
#     for keyword in keywords:
#         mask = df.apply(lambda col: col.astype(str).str.contains(keyword, case=False, na=False))
#         row_index = mask.any(axis=1)
#         match = df[row_index]

#         if not match.empty:
#             row = match.iloc[0]
#             numeric_values = pd.to_numeric(row, errors="coerce")
#             valid_nums = numeric_values[numeric_values.notna()]
#             if not valid_nums.empty:
#                 return float(valid_nums.iloc[-1])
#     return 0.0


# def upload_pnl(request):
#     """
#     View for uploading the Profit & Loss Excel file,
#     calculating the weighted financial score,
#     and generating AI-based advice using an LLM.
#     """
#     if request.method == "POST":
#         try:
#             file = request.FILES["file"]
#             df = pd.read_excel(file)

#             # --- Extract key metrics dynamically ---
#             total_income = get_value(df, ["Total Income", "Total Revenue", "Income"])
#             gross_profit = get_value(df, ["Gross Profit"])
#             admin_expenses = get_value(df, ["Total ADMINISTRATIVE EXPENSES", "Administrative"])
#             distribution_costs = get_value(df, ["Total DISTRIBUTION COSTS", "Distribution"])
#             finance_costs = get_value(df, ["Total FINANCE AND OTHER", "Finance"])

#             # --- Validate data presence ---
#             if total_income == 0 or gross_profit == 0:
#                 return render(request, "analysis/upload.html", {
#                     "error": "Could not locate essential fields in your Excel file. "
#                              "Please check column names (e.g., 'Total Income', 'Gross Profit')."
#                 })

#             # --- Compute derived metrics ---
#             net_profit = gross_profit - (admin_expenses + distribution_costs + finance_costs)

#             record = FinancialRecord.objects.create(
#                 company_name=request.POST["company_name"],
#                 period=request.POST["period"],
#                 total_income=total_income,
#                 gross_profit=gross_profit,
#                 admin_expenses=admin_expenses,
#                 distribution_costs=distribution_costs,
#                 finance_costs=finance_costs,
#                 net_profit=net_profit
#             )

#             # --- Weighted score computation ---
#             score, category, suggestion, contributions = calculate_weighted_score(record)

#             # --- Store ratios and score ---
#             fs = FinancialScore.objects.create(
#                 record=record,
#                 net_profit_margin=(record.net_profit / record.total_income) * 100,
#                 expense_ratio=((record.admin_expenses + record.distribution_costs + record.finance_costs)
#                                / record.total_income) * 100,
#                 gross_profit_margin=(record.gross_profit / record.total_income) * 100,
#                 finance_cost_ratio=(record.finance_costs / record.total_income) * 100,
#                 weighted_score=score,
#                 category=category,
#                 suggestion=suggestion
#             )

#             # --- Prepare metrics dictionary for AI ---
#             metrics = {
#                 "Net Profit Margin": fs.net_profit_margin,
#                 "Expense Ratio": fs.expense_ratio,
#                 "Gross Profit Margin": fs.gross_profit_margin,
#                 "Finance Cost Ratio": fs.finance_cost_ratio
#             }

#             # --- Generate LLM Explanation & Advice ---
#             llm_advice = generate_financial_advice_llm(metrics, category, score)

#             # --- Display results ---
#             context = {
#                 "company": record.company_name,
#                 "period": record.period,
#                 "income": total_income,
#                 "gross_profit": gross_profit,
#                 "admin_exp": admin_expenses,
#                 "dist_exp": distribution_costs,
#                 "finance_exp": finance_costs,
#                 "net_profit": net_profit,
#                 "score": score,
#                 "category": category,
#                 "suggestion": suggestion,
#                 "contributions": contributions,
#                 "metrics": metrics,
#                 "llm_advice": llm_advice,  # <-- NEW
#             }

#             return render(request, "analysis/result_card.html", context)

#         except Exception as e:
#             return render(request, "analysis/upload.html", {
#                 "error": f"An error occurred while processing the file: {e}"
#             })

#     return render(request, "analysis/upload.html")


# def dashboard(request):
#     """
#     View to show all historical records and their scores.
#     """
#     scores = FinancialScore.objects.select_related("record").all().order_by("-record__uploaded_at")
#     return render(request, "analysis/dashboard.html", {"scores": scores})



# analysis/views.py
import pandas as pd
from django.shortcuts import render
from .models import FinancialRecord, FinancialScore
from .utils import calculate_weighted_score, generate_rule_based_advice


def dashboard(request):
    from .models import FinancialScore
    scores = FinancialScore.objects.select_related("record").order_by("-id")[:10]
    return render(request, "analysis/dashboard.html", {"scores": scores})


def get_value_anywhere(df, keywords):
    
    """
    Improved version:
    - Handles merged cells
    - Ignores spaces, case, and special characters
    - Returns the rightmost numeric value in the matched row
    """
    import re

    # Clean DataFrame text
    df_clean = df.copy().astype(str).applymap(lambda x: x.strip().replace("\u00A0", " ").lower() if pd.notna(x) else "")

    for keyword in keywords:
        # Flexible regex for partial matches (handles missing or extra spaces)
        pattern = re.compile(keyword.lower().replace(" ", ".*"))

        # Find any row containing the keyword in any column
        mask = df_clean.apply(lambda col: col.apply(lambda cell: bool(pattern.search(cell))))
        matched_rows = df[mask.any(axis=1)]

        if not matched_rows.empty:
            # Take the first match
            row = matched_rows.iloc[0]

            # Extract all numeric values from the row
            numeric_values = pd.to_numeric(row, errors="coerce")
            valid_nums = numeric_values[numeric_values.notna()]

            if not valid_nums.empty:
                # Return the last (rightmost) numeric value
                return float(valid_nums.iloc[-1])

    # Nothing found
    return 0.0



def upload_pnl(request):
    if request.method == "POST":
        try:
            file = request.FILES["file"]
            df = pd.read_excel(file, header=None)
            company = request.POST.get("company_name", "Unknown")
            period = request.POST.get("period", "N/A")

            # --- Extract key metrics dynamically ---
            total_income = get_value_anywhere(df, ["Total Income", "Total Revenue", "Income"])
            gross_profit = get_value_anywhere(df, ["Gross Profit"])
            admin_expenses = get_value_anywhere(df, ["Total ADMINISTRATIVE EXPENSES", "Administrative Expenses", "Administration"])
            distribution_costs = get_value_anywhere(df, ["Total DISTRIBUTION COSTS", "Distribution Costs", "Selling & Distribution"])
            finance_costs = get_value_anywhere(df, ["Total FINANCE AND OTHER", "Finance Costs", "Financial Expenses", "Interest"])
            growth_rate = get_value_anywhere(df, ["Revenue Growth", "Growth Rate"])

            # --- Validate essential fields ---
            if total_income == 0 or gross_profit == 0:
                return render(request, "analysis/upload.html", {
                    "error": "Missing key fields like 'Total Income' or 'Gross Profit'."
                })

            # --- Compute derived metric ---
            net_profit = gross_profit - (admin_expenses + distribution_costs + finance_costs)

            # --- Save financial record ---
            record = FinancialRecord.objects.create(
                company_name=company,
                period=period,
                total_income=total_income,
                gross_profit=gross_profit,
                admin_expenses=admin_expenses,
                distribution_costs=distribution_costs,
                finance_costs=finance_costs,
                net_profit=net_profit,
                revenue_growth_rate=growth_rate or 0
            )

            # --- Weighted score calculation ---
            score, category, suggestion, contributions = calculate_weighted_score(record)

            # --- Ratios dictionary ---
            ratios = {
                "net_profit_margin": (record.net_profit / record.total_income) * 100,
                "expense_ratio": ((record.admin_expenses + record.distribution_costs + record.finance_costs) / record.total_income) * 100,
                "gross_profit_margin": (record.gross_profit / record.total_income) * 100,
                "finance_cost_ratio": (record.finance_costs / record.total_income) * 100,
                "revenue_growth_rate": record.revenue_growth_rate or 0
            }

            # --- Generate rule-based advice ---
            advisory = generate_rule_based_advice(ratios, category)

            # --- Save financial score ---
            FinancialScore.objects.create(
                record=record,
                net_profit_margin=ratios["net_profit_margin"],
                expense_ratio=ratios["expense_ratio"],
                gross_profit_margin=ratios["gross_profit_margin"],
                finance_cost_ratio=ratios["finance_cost_ratio"],
                weighted_score=score,
                category=category,
                suggestion=advisory
            )

            # --- Prepare context for result page ---
            context = {
                "company": company,
                "period": period,
                "income": total_income,
                "gross_profit": gross_profit,
                "admin_exp": admin_expenses,
                "dist_exp": distribution_costs,
                "finance_exp": finance_costs,
                "net_profit": net_profit,
                "score": score,
                "category": category,
                "contributions": contributions,
                "ratios": ratios,
                "advisory": advisory
            }

            return render(request, "analysis/result_card.html", context)

        except Exception as e:
            return render(request, "analysis/upload.html", {"error": f"Error: {e}"})

    return render(request, "analysis/upload.html")

