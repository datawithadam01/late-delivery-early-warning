CREATE VIEW orders_view AS
SELECT
    order_item_id,
    order_id,
    order_date,
    ship_date,
    ship_mode,
    scheduled_days,
    actual_days,
    CASE WHEN delivery_status = 'Shipping canceled' THEN 1 ELSE 0 END AS is_cancelled,
    CASE
        WHEN delivery_status = 'Shipping canceled' THEN NULL
        WHEN actual_days > scheduled_days THEN 1
        ELSE 0
    END AS is_late,    delivery_status,
    late_flag_source,
    sales,
    quantity,
    discount_rate,
    profit,
    customer_segment,
    market,
    order_region,
    order_country,
    category_name,
    department_name,
    payment_type
FROM orders_clean;