import sys
sys.path.append("src")
from ingest import load_config, read_raw, standardize

config = load_config("config/columns.yaml")
df = standardize(read_raw(config), config)

diff_days = (df["ship_date"] - df["order_date"]).dt.days
match = (diff_days == df["actual_days"]).mean() * 100
print(f"ship_date - order_date equals actual_days: {match:.2f}%")

print(df[["order_date", "ship_date", "actual_days", "scheduled_days"]].head())