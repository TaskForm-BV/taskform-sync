"""
Data transformation utilities for nesting flat query results.
"""
from typing import List, Dict, Any
from decimal import Decimal


def auto_nest_data(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Automatically nest flat data based on dot-notation in column names.
    
    Convention:
    - 'parent-id' column triggers nesting and is used for grouping
    - Columns without dots are flat fields on the parent
    - Columns with dots (e.g., 'lines.sku', 'lines.steps.name') create nested arrays
    
    Examples:
        Flat data (no parent-id):
            [{"external_id": "1", "name": "Customer A"}]
            → [{"external_id": "1", "name": "Customer A"}]
        
        1-level nesting (orders → lines):
            [
                {"parent-id": "O1", "order_number": "001", "lines.sku": "A", "lines.qty": 10},
                {"parent-id": "O1", "order_number": "001", "lines.sku": "B", "lines.qty": 5}
            ]
            → [{"order_number": "001", "lines": [{"sku": "A", "qty": 10}, {"sku": "B", "qty": 5}]}]
        
        3-level nesting (orders → lines → steps):
            [
                {"parent-id": "O1", "lines.line_num": "1", "lines.steps.seq": 1, "lines.steps.op": "Cut"},
                {"parent-id": "O1", "lines.line_num": "1", "lines.steps.seq": 2, "lines.steps.op": "Weld"}
            ]
            → [{"lines": [{"line_num": "1", "steps": [{"seq": 1, "op": "Cut"}, {"seq": 2, "op": "Weld"}]}]}]
    
    Args:
        rows: List of flat dictionaries from database query
    
    Returns:
        List of nested dictionaries ready for API
    """
    if not rows:
        return rows
    
    first_row = rows[0]
    
    # No parent-id column? Return flat data as-is
    if "parent-id" not in first_row:
        return rows
    
    # Group rows by parent-id
    parents = {}
    
    for row in rows:
        parent_id = row["parent-id"]
        
        # Initialize parent if first time seeing this ID
        if parent_id not in parents:
            parents[parent_id] = {
                "_flat_fields": {},
                "_nested_paths": {}
            }
        
        parent = parents[parent_id]
        
        # Process each column in the row
        for col, val in row.items():
            if col == "parent-id" or val is None:
                continue
            
            # Convert Decimal to float for JSON serialization
            if isinstance(val, Decimal):
                val = float(val)
            
            if '.' not in col:
                # Flat field - add to parent
                parent["_flat_fields"][col] = val
            else:
                # Nested field - parse dot notation
                parts = col.split('.')
                _add_nested_value(parent["_nested_paths"], parts, val)
    
    # Convert internal structure to final nested dictionaries
    result = []
    for parent in parents.values():
        final_obj = parent["_flat_fields"].copy()
        
        # Convert nested paths to arrays
        for array_name, items in parent["_nested_paths"].items():
            final_obj[array_name] = _nested_paths_to_arrays(items)
        
        result.append(final_obj)
    
    return result


def _add_nested_value(nested_paths: Dict, parts: List[str], value: Any) -> None:
    """
    Add a value to the nested paths structure.
    
    This builds an intermediate representation that tracks all values
    at each nesting level before converting to arrays.
    """
    if len(parts) == 1:
        # Leaf value - this shouldn't happen at root level
        return
    
    array_name = parts[0]
    remaining_parts = parts[1:]
    
    if array_name not in nested_paths:
        nested_paths[array_name] = []
    
    # Create a signature from remaining parts to identify unique items
    # For nested arrays, we need to track the path
    if len(remaining_parts) == 1:
        # This is a direct field in the array (e.g., lines.sku)
        field_name = remaining_parts[0]
        
        # Find or create an item with this value
        # We'll deduplicate later based on all fields
        nested_paths[array_name].append({field_name: value})
    else:
        # This is a nested array (e.g., lines.steps.name)
        # We need to create a nested structure
        next_array = remaining_parts[0]
        
        # Find or create a container for this nested array
        if not nested_paths[array_name]:
            nested_paths[array_name].append({"_nested": {}})
        
        last_item = nested_paths[array_name][-1]
        if "_nested" not in last_item:
            last_item["_nested"] = {}
        
        _add_nested_value(last_item["_nested"], remaining_parts, value)


def _nested_paths_to_arrays(items: List[Dict]) -> List[Dict]:
    """
    Convert the intermediate nested paths structure to final arrays.
    Handles deduplication and nested array conversion.
    """
    if not items:
        return []
    
    # Merge items with the same values at this level
    merged = {}
    
    for item in items:
        # Separate nested and flat fields
        flat_fields = {k: v for k, v in item.items() if k != "_nested"}
        nested_fields = item.get("_nested", {})
        
        # Create a key from flat fields for deduplication
        key = tuple(sorted(flat_fields.items()))
        
        if key not in merged:
            merged[key] = {
                "flat": flat_fields,
                "nested": {}
            }
        
        # Merge nested fields
        for nested_name, nested_items in nested_fields.items():
            if nested_name not in merged[key]["nested"]:
                merged[key]["nested"][nested_name] = []
            merged[key]["nested"][nested_name].extend(nested_items)
    
    # Convert merged structure to final arrays
    result = []
    for item_data in merged.values():
        final_item = item_data["flat"].copy()
        
        # Recursively convert nested arrays
        for nested_name, nested_items in item_data["nested"].items():
            final_item[nested_name] = _nested_paths_to_arrays(nested_items)
        
        result.append(final_item)
    
    return result
