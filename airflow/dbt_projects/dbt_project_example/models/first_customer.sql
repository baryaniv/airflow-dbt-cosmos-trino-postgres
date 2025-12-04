-- View with the name of the first customer
SELECT 
    customer_name as first_customer_name
FROM {{ ref('customers') }}
ORDER BY customer_id
LIMIT 1
