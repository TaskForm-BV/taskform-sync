-- Example query demonstrating 3-level nesting: orders → lines → steps
-- 
-- This query uses dot notation to create nested arrays:
-- - Regular columns (external_id, order_number) become flat fields on the parent
-- - Columns with dots (lines.*, lines.steps.*) create nested arrays
-- - The 'parent-id' column triggers nesting and groups all rows by this ID
--
-- Result structure:
-- {
--   "external_id": "PO001",
--   "order_number": "2024-001",
--   "customer": "ACME Corp",
--   "lines": [
--     {
--       "line_number": 1,
--       "product": "Widget A",
--       "quantity": 100,
--       "steps": [
--         {"sequence": 1, "operation": "Cut", "duration_minutes": 30},
--         {"sequence": 2, "operation": "Weld", "duration_minutes": 45}
--       ]
--     }
--   ]
-- }

SELECT 
    -- Parent ID for grouping (required for nesting)
    po.objectid as "parent-id",
    
    -- Flat fields on the parent production order
    po.objectid as external_id,
    po.ordernumber as order_number,
    po.customername as customer,
    po.orderdate as order_date,
    po.status as status,
    
    -- Production line fields (creates 'lines' array)
    pl.linenumber as "lines.line_number",
    pl.productcode as "lines.product",
    pl.quantity as "lines.quantity",
    pl.unitprice as "lines.unit_price",
    
    -- Production step fields (creates 'steps' array nested in 'lines')
    ps.sequence as "lines.steps.sequence",
    ps.operation as "lines.steps.operation",
    ps.duration as "lines.steps.duration_minutes",
    ps.workcenter as "lines.steps.workcenter",
    ps.status as "lines.steps.status"

FROM production_orders po
LEFT JOIN production_lines pl ON pl.order_id = po.objectid
LEFT JOIN production_steps ps ON ps.line_id = pl.objectid

-- Optional: filter for specific orders
-- WHERE po.status = 'ACTIVE'
-- AND po.orderdate >= CURRENT_DATE - 30

ORDER BY po.objectid, pl.linenumber, ps.sequence;
