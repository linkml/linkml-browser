"""Core functionality for LinkML Browser."""

import json
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


class BrowserGenerator:
    """Generates standalone faceted browsers for JSON data."""
    
    def __init__(self, data: List[Dict[str, Any]], schema: Optional[Dict[str, Any]] = None):
        """Initialize the browser generator.
        
        Args:
            data: List of JSON objects to browse
            schema: Optional schema definition. If not provided, will be inferred.
        """
        self.data = data
        self.schema = schema or self.infer_schema()
    
    def infer_schema(self, 
                     title: str = "Data Browser",
                     description: str = "Browse and filter data") -> Dict[str, Any]:
        """Infer a basic schema from the data structure.
        
        Args:
            title: Browser title
            description: Browser description
            
        Returns:
            Inferred schema dictionary
        """
        if not self.data:
            raise ValueError("Cannot infer schema from empty data")
        
        # Get all unique keys from all items
        all_keys: Set[str] = set()
        for item in self.data:
            all_keys.update(item.keys())
        
        # Analyze field types from first few items
        field_info: Dict[str, Dict[str, Any]] = {}
        sample_size = min(100, len(self.data))
        
        for key in all_keys:
            field_info[key] = {
                'has_array': False,
                'has_string': False,
                'has_number': False,
                'unique_values': set(),
                'all_numbers': True
            }
            
            for item in self.data[:sample_size]:
                if key in item:
                    value = item[key]
                    if isinstance(value, list):
                        field_info[key]['has_array'] = True
                        # Add array values to unique values
                        for v in value:
                            if isinstance(v, (str, int, float)):
                                field_info[key]['unique_values'].add(str(v))
                    elif isinstance(value, (int, float)):
                        field_info[key]['has_number'] = True
                        field_info[key]['unique_values'].add(str(value))
                    elif isinstance(value, str):
                        field_info[key]['has_string'] = True
                        field_info[key]['all_numbers'] = False
                        field_info[key]['unique_values'].add(value)
        
        # Build schema
        schema: Dict[str, Any] = {
            "title": title,
            "description": description,
            "searchPlaceholder": "Search...",
            "searchableFields": [],
            "facets": [],
            "displayFields": []
        }
        
        # Determine searchable fields (prefer string fields)
        for key, info in field_info.items():
            if info['has_string'] or info['has_array']:
                schema["searchableFields"].append(key)
        
        # If no string fields, use all fields
        if not schema["searchableFields"]:
            schema["searchableFields"] = list(all_keys)
        
        # Create facets for fields with reasonable number of unique values
        for key, info in field_info.items():
            unique_count = len(info['unique_values'])
            
            # Skip fields with too many unique values (likely IDs)
            if unique_count > 1 and unique_count < 100:
                facet_type = "array" if info['has_array'] else "string"
                
                # Check if all values are integers
                if info['all_numbers'] and not info['has_array']:
                    try:
                        # Try to parse all values as integers
                        int_values = [int(v) for v in info['unique_values'] if v]
                        if len(int_values) == len(info['unique_values']):
                            facet_type = "integer"
                    except ValueError:
                        pass
                
                schema["facets"].append({
                    "field": key,
                    "label": key.replace('_', ' ').title(),
                    "type": facet_type,
                    "sortBy": "count"
                })
        
        # Display all fields
        for key in sorted(all_keys):
            field_type = "array" if field_info[key]['has_array'] else "string"
            schema["displayFields"].append({
                "field": key,
                "label": key.replace('_', ' ').title(),
                "type": field_type
            })
        
        return schema
    
    def generate(self, output_dir: Path, force: bool = False) -> None:
        """Generate the browser files in the specified directory.
        
        Args:
            output_dir: Directory to generate files in
            force: Whether to overwrite existing directory
        """
        # Create output directory
        if output_dir.exists():
            if not force:
                raise FileExistsError(f"Output directory '{output_dir}' already exists. Use force=True to overwrite.")
            else:
                shutil.rmtree(output_dir)
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy index.html
        template_path = Path(__file__).parent / "index.html"
        if not template_path.exists():
            raise FileNotFoundError(f"Template file not found at {template_path}")
        
        shutil.copy(template_path, output_dir / "index.html")
        
        # Create data.js
        self._create_data_js(output_dir / "data.js")
        
        # Create schema.js
        self._create_schema_js(output_dir / "schema.js")
    
    def _create_data_js(self, output_path: Path) -> None:
        """Create data.js file from JSON data."""
        js_content = f"window.searchData = {json.dumps(self.data, indent=2)};\n"
        js_content += "window.dispatchEvent(new Event('searchDataReady'));\n"
        
        with open(output_path, 'w') as f:
            f.write(js_content)
    
    def _create_schema_js(self, output_path: Path) -> None:
        """Create schema.js file from schema definition."""
        js_content = f"window.searchSchema = {json.dumps(self.schema, indent=2)};\n"
        js_content += "window.dispatchEvent(new Event('searchDataReady'));\n"
        
        with open(output_path, 'w') as f:
            f.write(js_content)


def load_json_data(file_path: Path) -> List[Dict[str, Any]]:
    """Load and validate JSON data from a file.
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        List of JSON objects
        
    Raises:
        ValueError: If data is not a list of objects
    """
    with open(file_path) as f:
        data = json.load(f)
    
    if not isinstance(data, list):
        raise ValueError("Data must be a JSON array of objects")
    
    return data


def load_schema(file_path: Path) -> Dict[str, Any]:
    """Load schema from a JSON file.
    
    Args:
        file_path: Path to schema JSON file
        
    Returns:
        Schema dictionary
    """
    with open(file_path) as f:
        return json.load(f)


def save_schema(schema: Dict[str, Any], file_path: Path) -> None:
    """Save schema to a JSON file.
    
    Args:
        schema: Schema dictionary
        file_path: Path to save the schema
    """
    with open(file_path, 'w') as f:
        json.dump(schema, f, indent=2)