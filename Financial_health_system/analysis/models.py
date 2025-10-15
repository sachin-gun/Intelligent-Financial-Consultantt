from django.db import models

class FinancialRecord(models.Model):
    company_name = models.CharField(max_length=100)
    period = models.CharField(max_length=50)
    total_income = models.FloatField()
    gross_profit = models.FloatField()
    admin_expenses = models.FloatField()
    distribution_costs = models.FloatField()
    finance_costs = models.FloatField()
    net_profit = models.FloatField()
    revenue_growth_rate = models.FloatField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.company_name} - {self.period}"

class FinancialScore(models.Model):
    record = models.OneToOneField(FinancialRecord, on_delete=models.CASCADE)
    net_profit_margin = models.FloatField()
    expense_ratio = models.FloatField()
    gross_profit_margin = models.FloatField()
    finance_cost_ratio = models.FloatField()
    weighted_score = models.FloatField()
    category = models.CharField(max_length=10, choices=[
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low')
    ])
    suggestion = models.TextField(blank=True, null=True)
