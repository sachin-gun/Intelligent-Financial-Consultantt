def calculate_weighted_score(record):
    net_profit_margin = (record.net_profit / record.total_income) * 100
    expense_ratio = ((record.admin_expenses + record.distribution_costs + record.finance_costs) / record.total_income) * 100
    gross_profit_margin = (record.gross_profit / record.total_income) * 100
    finance_cost_ratio = (record.finance_costs / record.total_income) * 100
    revenue_growth_rate = record.revenue_growth_rate or 0

    weights = {
        'net_profit_margin': 0.35,
        'expense_ratio': 0.25,
        'gross_profit_margin': 0.20,
        'finance_cost_ratio': 0.10,
        'revenue_growth_rate': 0.10
    }

    expense_score = 100 - expense_ratio
    finance_score = 100 - finance_cost_ratio

    weighted_score = (
        net_profit_margin * weights['net_profit_margin'] +
        expense_score * weights['expense_ratio'] +
        gross_profit_margin * weights['gross_profit_margin'] +
        finance_score * weights['finance_cost_ratio'] +
        revenue_growth_rate * weights['revenue_growth_rate']
    )

    if weighted_score >= 80:
        category = "High"
        suggestion = "Strong financial health. Consider reinvestment or expansion."
    elif weighted_score >= 50:
        category = "Medium"
        suggestion = "Moderate health. Optimize costs and improve profit margins."
    else:
        category = "Low"
        suggestion = "Weak financial position. Focus on expense reduction and revenue growth."

    return round(weighted_score, 2), category, suggestion
