import sqlite3
import pandas as pd

conn = sqlite3.connect("data/orders.db")
df = pd.read_sql(
    "SELECT order_date FROM orders_view WHERE is_cancelled = 0",
    conn,
    parse_dates=["order_date"],
)
conn.close()

monthly = df.groupby(df["order_date"].dt.to_period("M")).size()
print(monthly.to_string())
print("80th percentile date:", df["order_date"].quantile(0.8))