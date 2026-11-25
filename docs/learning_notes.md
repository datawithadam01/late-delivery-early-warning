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


Leakage:
Leakage is when a model is trained on information that would not be available at the moment of prediction. This makes test scores look better than real-world performance.
"Known before the prediction moment = KEEP. Known after = DROP."ship_date and scheduled_days are two major examples.
It has two parts:

What: information from after the prediction moment (or the answer itself) gets into the features.
Effect: the score looks great in testing, but the model fails in real use, because that information doesn't exist yet.

Our project version (use this in interviews):

"We predict at the moment the order is placed. actual_days, ship_date and delivery_status only exist after delivery, so they are leakage. scheduled_days and ship_mode are set at checkout, so they are safe."

Time Split
In real use we train on the past and predict the future.
A random split mixes future rows into training, so scores look too good.
We split by order_date. Items of one order share a date, so they stay together.

Likely interview follow-up: "What if the test period looks different from the train period?" Your answer: yes, ours does. From Oct 2017 the data changes (only Europe and Pacific Asia, more departments), so we report results separately for before and after Oct 2017.

the date-split score is lower but honest, because it matches real use. We predict the future from the past.

We train on the past and test on the newest rows, like real use.
A random split lets the model see the future, so scores look too good.
We split by order_date

Base rate:
The base rate is the share of positives, here 57.29% late.
Predicting "late" for everything gives 57% accuracy without any model.
So every metric must be shown next to the base rate, to see if the model really adds something.
"Your model has 65% accuracy. Is that good?" Your answer: not by itself. Compare it with the base rate (57%) and with the ship-mode baseline.

accuracy can look high while the model catches nothing, so we use precision, recall and PR-AUC instead.

Imp terms:
Precision: of the items we flag as late, how many are late.
Recall: of all late items, how many we flag.
PR-AUC: how well the model ranks risky items first

Precision = of the items I flagged, how many were truly late.
Recall = of all late items, how many I flagged.
PR-AUC = how good the ranking is overall. Compare it with the base rate, 0.57.

Callibration:
A score of 0.7 means about 70% of items with that score should truly be late.
A calibration curve checks if the scores match reality.
A model can rank well but still give scores that are too high or too low.

Likely interview follow-up: "Why does calibration matter?" Your answer: if ops teams act on "70% risk", the number must mean what it says.

Calibration means the model's scores match real life. If the model says 0.7 for a group of items, about 70% of them should really be late.

Calibration = the predicted probability matches how often the thing really happens.
Example: of all items scored about 0.7, about 70% should truly be late.
A calibration curve checks this. A model can rank well and still be badly calibrated, for example too confident.

Easy picture: a weather app says "70% rain" on 100 days. If it rains on about 70 of them, it is calibrated. If it rains on only 30, it is not.

Our check: the calibration curve plots the predicted score against the real late rate. The closer it is to a diagonal line, the better. You'll save this plot as docs/calibration.png in Task 6.

Overfitting:

A model does this too. It learns the quirks of the training rows, not the real pattern. So the train score is high and the test score is low.

Our version:

Compare the score on train rows with the score on test rows.
A big gap (high on train, much lower on test) is the warning sign.
This is one reason we never tune on the test set.


Overfitting = the model memorises the training data instead of learning the pattern.
Sign: high train score, much lower test score.
Fix: keep the test set untouched, and keep the model simple.

Likely interview follow-up: "How do you check for overfitting?" Your answer: compare train and test scores, and keep the test set for the final check only.

Precision@k

Precision@k = sort by risk, take the top k, and see what share are really late.
It matches real use: ops can only check k items a day.
Compare it with the base rate (57%). A good model should be well above that at the top.
: precision@k is only meaningful next to the base rate. 90% against 57% means the top of the ranking is much better than random.

ROC-AUC vs PR-AUC
ROC-AUC: the chance a random late item gets a higher score than a random on-time item (0.5 = random).
PR-AUC: how well the flagged items are really late (random = the base rate).
We report PR-AUC, with the base rate next to it.
"Why not ROC-AUC?" Your answer: PR-AUC focuses on the items we flag, which is what ops cares about, and it stays strict when positives are rare.
PR-AUC must be compared with the base rate. 0.58 vs 0.57 means the model is almost random.

Threshold

A model gives each item a score from 0 to 1. To say "late" or "not late", you choose a cutoff, called the threshold.
Threshold = the score cutoff that turns a probability into "late" or "not late".
Lower threshold: higher recall, lower precision. Higher threshold: the opposite.
0.5 is only a default. The right one depends on the cost of mistakes.

Class imbalance 
Our data is not very imbalanced (57% late vs 43% on time). But interviewers often ask "what if late were only 5%?" Your answer has three parts:

Don't use accuracy. Use precision, recall, PR-AUC and precision@k.
Tell the model the small class matters more. In scikit-learn: class_weight="balanced".
Choose the threshold based on the business cost, not 0.5.
Class imbalance = one class is much bigger than the other.
Ours is mild (57/43), so we don't need special fixes.
If late were rare: avoid accuracy, use class weights, and choose the threshold carefully.

the split gave 138,182 train and 34,583 test rows, with equal late rates of about 57.3%, so the base rate is the same on both sides.

flagging everything gives accuracy equal to the base rate (57.30%) and recall 100%, but it tells ops nothing, because it can't tell risky items from safe ones.

the First Class rule has very high precision but low recall, because it flags only one ship mode and misses the late items in the others.

precision 1.0 only means "when I flag, I'm right". It says nothing about how many late items I missed. I need recall too.

: a baseline with only 4 scores has many ties, so its top-k list is arbitrary inside each tie. Real models give many different scores, so they have no such problem.

Baseline	PR-AUC	P@100	P@500	Accuracy	Recall	Precision
Base rate (reference)	0.573					
Majority class	n/a	n/a	n/a	0.573	1.000	0.573
First Class rule	n/a	n/a	n/a	0.580	0.267	1.000
Ship-mode late rate	0.786	1.000	1.000	not yet computed	not yet computed	not yet computed


Ship mode	Late rate
First Class	100.0%
Second Class	79.8%
Same Day	46.7%
Standard Class	39.9%

