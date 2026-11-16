import sqlite3

import pandas as pd
import yaml
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent


def load_config(path):
    with open(path) as f:
        config = yaml.safe_load(f)
    return config


def read_raw(config):
    df = pd.read_csv(ROOT / config["raw_path"], encoding=config["encoding"])
    return df


def standardize(df, config):
    raw_names = list(config["columns"].values())
    df = df[raw_names]
    reverse = {raw: std for std, raw in config["columns"].items()}
    df = df.rename(columns=reverse)
    df["order_date"] = pd.to_datetime(df["order_date"], format=config["date_format"])
    df["ship_date"] = pd.to_datetime(df["ship_date"], format=config["date_format"])
    return df


def validate(df):
    checks = {}
    checks["rows"] = len(df)
    checks["columns"] = df.shape[1]

    m = df.isna().sum()
    checks["missing"] = m[m > 0].to_dict()

    checks["duplicate_order_item_id"] = int(df.duplicated(subset=["order_item_id"]).sum())
    checks["sales_zero_or_negative"] = int((df["sales"] <= 0).sum())
    checks["ship_before_order"] = int((df["ship_date"] < df["order_date"]).sum())

    checks["order_date_min"] = str(df["order_date"].min())
    checks["order_date_max"] = str(df["order_date"].max())

    is_late = (df["actual_days"] > df["scheduled_days"]).astype(int)
    agree = (df["late_flag_source"] == is_late).mean() * 100
    checks["late_flag_agreement_pct"] = round(float(agree), 2)

    is_cancelled = df["delivery_status"] == "Shipping canceled"
    disagree = df["late_flag_source"] != is_late
    checks["delivery_status_counts"] = df["delivery_status"].value_counts().to_dict()
    checks["cancelled_orders"] = int(is_cancelled.sum())
    checks["late_flag_disagreements"] = int(disagree.sum())
    checks["late_flag_disagreements_that_are_cancelled"] = int((disagree & is_cancelled).sum())
    checks["quantity_zero_or_negative"] = int((df["quantity"] <= 0).sum())
    checks["discount_rate_out_of_range"] = int(((df["discount_rate"] < 0) | (df["discount_rate"] > 1)).sum())
    checks["negative_actual_days"] = int((df["actual_days"] < 0).sum())
    checks["negative_scheduled_days"] = int((df["scheduled_days"] < 0).sum())
    return checks


def write_quality_report(checks, path):
    lines = ["# Data Quality Report", ""]

    for name, value in checks.items():
        lines.append(f"## {name}")
        if value == {}:
            lines.append("None")
        else:
            lines.append(str(value))
        lines.append("")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def load_to_sqlite(df, db_path):
    conn = sqlite3.connect(db_path)
    df.to_sql("orders_clean", conn, if_exists="replace", index=False)
    conn.close()

def create_view(db_path, sql_path):
    with open(sql_path, encoding="utf-8") as f:
        sql = f.read()
    conn = sqlite3.connect(db_path)
    conn.execute("DROP VIEW IF EXISTS orders_view")
    conn.executescript(sql)
    conn.execute("SELECT * FROM orders_view LIMIT 1").fetchall()
    conn.close()


def main():
    config = load_config(ROOT / "config" / "columns.yaml")
    df = read_raw(config)
    df = standardize(df, config)
    checks = validate(df)
    write_quality_report(checks, ROOT / config["report_path"])
    load_to_sqlite(df, ROOT / config["db_path"])
    create_view(ROOT / config["db_path"], ROOT / config["view_sql_path"])
    print(f"Done: {checks['rows']} rows, {checks['columns']} columns loaded to {config['db_path']}")


if __name__ == "__main__":
    main()