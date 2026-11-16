Fix types first. pandas guesses each column’s type on load. Dates come in as text (str), so convert them with to_datetime and an explicit format, or you can’t compare or subtract them.
Check before you trust the data. duplicated(subset=[key]).sum() should be 0 for a key, and isna().sum() shows which columns are empty. Here, Product Description is 100% empty and Order Zipcode is 86% empty.
Know the grain. One row is one order item, not one order (180,519 rows vs 65,752 orders). Every count or prediction must say which one it means.

SQLite

SQLite is a database stored in one file (orders.db), and Python talks to it with sqlite3.
df.to_sql(...) writes a DataFrame as a table, and pd.read_sql(...) reads a query result back as a DataFrame.
A view is a saved SELECT with a name. It stores no data, it runs the query each time, and I drop and recreate it so the script can run again.

YAML

YAML is a settings file with key: value pairs, and indentation shows what belongs inside what (spaces only, never Tab).
yaml.safe_load turns it into a Python dictionary, and safe_load is safer than load.
I use it so column names live in the config, not in the code, so a client’s data needs only a new YAML.

FastAPI

An API is a web address that returns data, and FastAPI builds one from Python functions.
@app.get("/health") means “when someone visits /health, run the function below”.
uvicorn runs the server, and /docs is a page FastAPI builds automatically to test endpoints.