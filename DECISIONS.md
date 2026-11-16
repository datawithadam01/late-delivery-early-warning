# Decisions

- 15 Nov 2026: Building the risk model as the core and NL-to-SQL Q&A as a feature, not the other way round. Reason: a model with honest evaluation shows more judgment than another text-to-SQL demo.

## 15 Nov 2026: Data verified (Step 1)

- Raw file: 180,519 rows, 53 columns.
- 65,752 distinct Order Id; 180,519 distinct Order Item Id (unique key).
- Unit of analysis = order item (one row = one product line in an order). Predictions in Step 2 are per order item.
- Date format: "%m/%d/%Y %H:%M" (e.g. 1/31/2018 22:56).

## 16 Nov 2026: Late flag check

- Own rule (actual_days > scheduled_days) agrees with Late_delivery_risk on 97.55% of rows.
- All 4,423 disagreements have Delivery Status = "Shipping canceled".
- Decision: keep cancelled rows in orders_clean (Step 1 does not delete data). Exclude them from model training in Step 2, because "late" is undefined for an order that was never delivered.

## 16 Nov 2026: Late flag check

- Delivery status: Late 98,977 | Advance 41,592 | On time 32,196 | Cancelled 7,754.
- Own rule (actual_days > scheduled_days) agrees with Late_delivery_risk on 97.55% of rows.
- All 4,423 disagreements are "Shipping canceled" (rule says late, dataset says not late).
- Decision: keep all rows in orders_clean. In Step 2, exclude all 7,754 cancelled rows from training (172,765 rows remain), because "late" is undefined for an order that was never delivered.
- Note: the old project's 57.28% late rate included 4,423 cancelled rows counted as late. Excluding cancelled rows, the late rate is 57.29%.

## 16 Nov 2026: Columns dropped

- Privacy: Customer Email, Customer Password, Customer Fname, Customer Lname, Customer Street.
- Empty or mostly empty: Product Description (100% empty), Order Zipcode (86% empty), Customer Zipcode.
- Not needed for this project: Product Image, ids duplicated by other columns, latitude/longitude, city/state columns.
- Kept for Step 1 even though they leak the target: actual_days, delivery_status, late_flag_source. Step 2 decides what the model may see.

## 16 Nov 2026: ship_date is a leakage column

- Check: ship_date - order_date equals actual_days on 97.42% of rows. ship_date is effectively order_date + actual_days, so it gives away the outcome.
- Decision: ship_date is DROP for the model in Step 2. Kept in orders_clean and orders_view for reporting only.
- Step 2 will build features from an explicit allowlist of columns, not "all columns except the leaking ones".
- Leakage list so far: actual_days, delivery_status, late_flag_source, ship_date, is_late (target).
