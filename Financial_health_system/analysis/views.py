import pandas as pd
from django.shortcuts import render, redirect
from .models import FinancialRecord, FinancialScore
from .utils import calculate_weighted_score

def upload_pnl(request):
    if request.method == "POST":
        file = request.FILES["file"]
        df = pd.read_excel(file)

        total_income = float(df[df.iloc[:,0].str.contains("Total Income", case=False, na=False)].iloc[0, -1])
        gross_profit = float(df[df.iloc[:,0].str.contains("Gross Profit", case=False, na=False)].iloc[0, -1])
        admin_expenses = float(df[df.iloc[:,0].str.contains("Administrative", case=False, na=False)].iloc[0, -1])
        distribution_costs = float(df[df.iloc[:,0].str.contains("Distribution", case=False, na=False)].iloc[0, -1])
        finance_costs = float(df[df.iloc[:,0].str.contains("Finance", case=False, na=False)].iloc[0, -1])

        record = FinancialRecord.objects.create(
            company_name=request.POST["company_name"],
            period=request.POST["period"],
            total_income=total_income,
            gross_profit=gross_profit,
            admin_expenses=admin_expenses,
            distribution_costs=distribution_costs,
            finance_costs=finance_costs,
            net_profit=gross_profit - (admin_expenses + distribution_costs + finance_costs)
        )

        score, category, suggestion = calculate_weighted_score(record)

        FinancialScore.objects.create(
            record=record,
            net_profit_margin=(record.net_profit / record.total_income) * 100,
            expense_ratio=((record.admin_expenses + record.distribution_costs + record.finance_costs) / record.total_income) * 100,
            gross_profit_margin=(record.gross_profit / record.total_income) * 100,
            finance_cost_ratio=(record.finance_costs / record.total_income) * 100,
            weighted_score=score,
            category=category,
            suggestion=suggestion
        )

        return redirect("dashboard")

    return render(request, "analysis/upload.html")

def dashboard(request):
    scores = FinancialScore.objects.select_related("record").all().order_by("-record__uploaded_at")
    return render(request, "analysis/dashboard.html", {"scores": scores})
