import sqlite3
import pandas as pd

conn = sqlite3.connect("data/orders.db")
df = pd.read_sql(
    "SELECT order_date, ship_mode, market, department_name, category_name, sales, is_late "
    "FROM orders_view WHERE is_cancelled = 0",
    conn,
    parse_dates=["order_date"],
)
conn.close()

df["period"] = (df["order_date"] >= "2017-10-01").map(
    {False: "before Oct 2017", True: "Oct 2017 onwards"}
)

print(df.groupby("period").agg(
    rows=("is_late", "size"),
    late_rate=("is_late", "mean"),
    avg_sales=("sales", "mean"),
    departments=("department_name", "nunique"),
    categories=("category_name", "nunique"),
))
print(pd.crosstab(df["period"], df["ship_mode"], normalize="index").round(3))
print(pd.crosstab(df["period"], df["market"], normalize="index").round(3))