import sys
sys.path.append("src")
from ingest import load_config, read_raw, standardize

config = load_config("config/columns.yaml")
df = standardize(read_raw(config), config)

is_late = (df["actual_days"] > df["scheduled_days"]).astype(int)
disagree = df[df["late_flag_source"] != is_late]

print(len(disagree))
print(disagree["delivery_status"].value_counts())
print(df["delivery_status"].value_counts())