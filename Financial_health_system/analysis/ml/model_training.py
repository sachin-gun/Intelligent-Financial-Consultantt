import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import joblib

df = pd.read_csv("historical_financial_data.csv")

X = df[['net_profit_margin', 'expense_ratio', 'gross_profit_margin', 'finance_cost_ratio', 'revenue_growth_rate']]
y = df['health_score']

model = LinearRegression()
model.fit(X, y)
joblib.dump(model, "financial_health_model.pkl")
