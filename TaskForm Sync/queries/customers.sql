-- Example SQL query
-- The filename (without .sql) determines the table name for the API endpoint
-- This file will sync to: {base_url}/customers/bulk

SELECT 
    id AS external_id,
    name,
    email,
    phone,
    created_at,
    updated_at
FROM customers
WHERE active = 1;