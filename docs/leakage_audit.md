| Column      | Decision       | Known at order time? | Reason                        |
| ----------- | -------------- | -------------------- | ----------------------------- |
| ship_mode   | KEEP           | Yes                  | Customer picks it at checkout |
| actual_days | DROP (leakage) | No                   | Only known after delivery     |
| is_late     | TARGET         | No                   | What we predict               |

| Column           | Decision       | Known at order time? | Reason                                                                                          |
| ---------------- | -------------- | -------------------- | ----------------------------------------------------------------------------------------------- |
| order_item_id    | DROP           | Yes                  | Identifier, not a feature                                                                       |
| order_id         | DROP           | Yes                  | Identifier, not a feature                                                                       |
| order_date       | KEEP           | Yes                  | Used for month, weekday, hour and the split                                                     |
| ship_date        | DROP (leakage) | No                   | Behaves like a delivery date (matches actual_days on 97.42%)                                    |
| ship_mode        | KEEP           | Yes                  | Customer picks it at checkout                                                                   |
| scheduled_days   | KEEP           | Yes                  | Promised delivery time, set at order. Fixed per ship_mode (0/1/2/4), so it duplicates ship_mode |
| actual_days      | DROP (leakage) | No                   | Only known after delivery                                                                       |
| delivery_status  | DROP (leakage) | No                   | Only known after delivery                                                                       |
| late_flag_source | DROP (leakage) | No                   | The dataset's own late flag, a copy of the answer                                               |
| sales            | KEEP           | Yes                  | Order value is known at checkout                                                                |
| quantity         | KEEP           | Yes                  | On the order form                                                                               |
| discount_rate    | KEEP           | Yes                  | Applied at checkout                                                                             |
| item_profit      | DROP           | Unclear              | Timing unclear, may include later adjustments. Test in v2                                       |
| customer_segment | KEEP           | Yes                  | Known from the customer                                                                         |
| market           | KEEP           | Yes                  | Delivery destination, known at order                                                            |
| order_region     | KEEP           | Yes                  | Delivery destination, known at order                                                            |
| order_country    | DROP           | Yes                  | About 160 countries, many with few rows. Use market + order_region                              |
| category_name    | KEEP           | Yes                  | Product category on the order                                                                   |
| department_name  | KEEP           | Yes                  | Product department on the order                                                                 |
| payment_type     | KEEP           | Yes                  | Chosen at checkout                                                                              |
| is_cancelled     | DROP (leakage) | No                   | Cancellation happens later. Only used to remove rows                                            |
| is_late          | TARGET         | No                   | What we predict                                                                                 |
| items_in_order   | KEEP (new)     | Yes                  | Count of items in the same order, known at checkout                                             |

item_profit is dropped in v1 because we can't be sure it was known at order time. It might include later adjustments, so we don't risk it.

An interview question: "Why not use profit?" Answer: "I couldn't confirm when it was computed, so I excluded it to avoid possible leakage. I can test it as a separate experiment."

Checked 24 Nov: late rate by payment_type, customer_segment and department_name is 57-61% in every group. No sign of leakage.
