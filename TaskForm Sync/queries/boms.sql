-- Example query demonstrating 1-level nesting: BOMs → items
-- 
-- This query uses dot notation to create nested arrays:
-- - Regular columns (external_id, bom_code, name) become flat fields on the parent
-- - Columns with dots (items.*) create a nested 'items' array
-- - The 'parent-id' column triggers nesting and groups all rows by BOM ID
--
-- Result structure:
-- {
--   "external_id": "12345",
--   "bom_code": "1642700-1642700-A",
--   "name": "Assembly XYZ",
--   "items": [
--     {
--       "item_number": "001",
--       "component_code": "PART-A",
--       "quantity": 2.5,
--       "unit": "PCS",
--       "length_mm": 100,
--       "width_mm": 50,
--       "thickness_mm": 5
--     }
--   ]
-- }

SELECT 
    -- Parent ID for grouping (required for nesting)
    b.objectid as "parent-id",
    
    -- Flat fields on the parent BOM
    b.objectid as external_id,
    b.alias as bom_code,
    b.description as name,
    
    -- BOM item fields (creates 'items' array)
    bi.itemalias as "items.item_number",
    bi.description as "items.component_code",
    bi.quantity as "items.quantity",
    bi.quantityunit as "items.unit",
    bi.xdimsize as "items.length_mm",
    bi.ydimsize as "items.width_mm",
    bi.zdimsize as "items.thickness_mm"

FROM saleselement b
LEFT JOIN saleselementline bi ON bi.saleselement = b.objectid

-- Optional: filter for specific BOMs
-- WHERE b.alias = '1642700-1642700-A'

ORDER BY b.objectid, bi.itemalias;
