import sys
sys.path.append("src")
from ingest import load_config, read_raw, standardize, ROOT

config = load_config(ROOT / "config" / "columns.yaml")
df = standardize(read_raw(config), config)

n_items = df.groupby("order_id")["order_item_id"].transform("count")
multi = df[n_items > 1]

distinct_profits = multi.groupby("order_id")["profit"].nunique()
print("orders with more than 1 item:", len(distinct_profits))
print("of these, orders where profit differs between items:", int((distinct_profits > 1).sum()))

example_id = multi["order_id"].iloc[0]
print(df[df["order_id"] == example_id][["order_id", "order_item_id", "sales", "profit"]])