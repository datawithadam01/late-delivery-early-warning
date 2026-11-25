import sqlite3
import pandas as pd

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
print(df[["order_date", "order_month", "order_weekday", "order_hour"]].head())
print(df[CATEGORICAL + NUMERIC].isna().sum())
print(df[CATEGORICAL].nunique())

print(pd.crosstab(df["ship_mode"], df["scheduled_days"]))

for col in ["payment_type", "customer_segment", "department_name"]:
    print(df.groupby(col)["is_late"].agg(["mean", "size"]))

print(df["items_in_order"].describe())

SPLIT_DATE = pd.Timestamp("2017-04-22")
train = df[df["order_date"] < SPLIT_DATE]
test = df[df["order_date"] >= SPLIT_DATE]

print(len(train), len(test))
print(train["is_late"].mean(), test["is_late"].mean())
print(train["order_date"].min(), train["order_date"].max())
print(test["order_date"].min(), test["order_date"].max())