import sqlite3
import pandas as pd
from sklearn.metrics import accuracy_score, recall_score, precision_score
from sklearn.metrics import average_precision_score

CATEGORICAL = ["ship_mode", "customer_segment", "market", "order_region",
               "category_name", "department_name", "payment_type"]
NUMERIC = ["scheduled_days", "sales", "quantity", "discount_rate",
           "order_month", "order_weekday", "order_hour","items_in_order"]
TARGET = "is_late"

con = sqlite3.connect("data/orders.db")
df = pd.read_sql(
    "SELECT * FROM orders_view WHERE is_cancelled = 0",
    con,
    parse_dates=["order_date"],
)
df["order_month"] = df["order_date"].dt.month
df["order_weekday"] = df["order_date"].dt.day_of_week
df["order_hour"] = df["order_date"].dt.hour
df["items_in_order"] = df.groupby("order_id")["order_id"].transform("size")


SPLIT_DATE = pd.Timestamp("2017-04-22")
train = df[df["order_date"] < SPLIT_DATE]
test = df[df["order_date"] >= SPLIT_DATE]

print(len(train), len(test))
print(train["is_late"].mean(), test["is_late"].mean())
print(train["order_date"].min(), train["order_date"].max())
print(test["order_date"].min(), test["order_date"].max())

y_test = test["is_late"]
majority_pred = pd.Series(1, index=test.index)
print("majority accuracy:", accuracy_score(y_test, majority_pred))
print("majority recall:", recall_score(y_test, majority_pred))

rule_pred = (test["ship_mode"] == "First Class").astype(int)
print("first class accuracy:", accuracy_score(y_test, rule_pred))
print("first class recall:", recall_score(y_test, rule_pred))

print("first class precision:", precision_score(y_test, rule_pred))

rates = train.groupby("ship_mode")["is_late"].mean()
print(rates)

shipmode_score = test["ship_mode"].map(rates)
print(shipmode_score.head())

def precision_at_k(y_true, scores, k):
    order = scores.sort_values(ascending=False).index
    top_k = order[:k]
    return y_true.loc[top_k].mean()

print("shipmode P@100:", precision_at_k(y_test, shipmode_score, 100))
print("shipmode P@500:", precision_at_k(y_test, shipmode_score, 500))

print("shipmode PR-AUC:", average_precision_score(y_test, shipmode_score))
print("base rate:", y_test.mean())
