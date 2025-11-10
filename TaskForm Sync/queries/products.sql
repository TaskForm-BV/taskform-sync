-- Example SQL query for products
-- This file will sync to: {base_url}/products/bulk

SELECT 
    product_id AS external_id,
    product_name AS name,
    sku,
    price,
    stock_quantity,
    category,
    last_modified
FROM products;