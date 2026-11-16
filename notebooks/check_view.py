import sqlite3
import pandas as pd

conn = sqlite3.connect("data/orders.db")
print(pd.read_sql("SELECT COUNT(*) AS n, AVG(is_late) AS late_rate, SUM(is_cancelled) AS cancelled FROM orders_view", conn))
conn.close()