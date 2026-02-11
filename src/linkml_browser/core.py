"""Core functionality for LinkML Browser."""

import json
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

from linkml_runtime.utils.schemaview import SchemaView


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


# Browser schema for LinkML schemas
LINKML_BROWSER_SCHEMA: Dict[str, Any] = {
    "title": "Schema Browser",
    "description": "Browse LinkML schema elements",
    "searchPlaceholder": "Search elements...",
    "searchableFields": ["name", "title", "description", "aliases", "comments", "keywords", "permissible_values"],
    "facets": [
        {"field": "type", "label": "Element Type", "type": "string", "sortBy": "count"},
        {"field": "in_subset", "label": "Subset", "type": "array", "sortBy": "count"},
        {"field": "classes", "label": "Used By Class", "type": "array", "sortBy": "count"},
        {"field": "slots", "label": "Used By Slot", "type": "array", "sortBy": "count"},
        {"field": "range", "label": "Range", "type": "string", "sortBy": "count"},
        {"field": "is_a", "label": "Parent", "type": "string", "sortBy": "count"},
        {"field": "required", "label": "Required", "type": "string", "sortBy": "count"},
        {"field": "multivalued", "label": "Multivalued", "type": "string", "sortBy": "count"},
        {"field": "abstract", "label": "Abstract", "type": "string", "sortBy": "count"},
        {"field": "mixin", "label": "Mixin", "type": "string", "sortBy": "count"},
        {"field": "deprecated", "label": "Deprecated", "type": "string", "sortBy": "count"},
    ],
    "displayFields": [
        {"field": "name", "label": "Name", "type": "string"},
        {"field": "title", "label": "Title", "type": "string"},
        {"field": "description", "label": "Description", "type": "string"},
        {"field": "type", "label": "Type", "type": "string"},
        {"field": "range", "label": "Range", "type": "string"},
        {"field": "is_a", "label": "Parent", "type": "string"},
        {"field": "url", "label": "URI", "type": "url"},
        {"field": "classes", "label": "Used By", "type": "array"},
        {"field": "slots", "label": "Slots", "type": "array"},
        {"field": "mixins", "label": "Mixins", "type": "array"},
        {"field": "permissible_values", "label": "Values", "type": "array"},
        {"field": "in_subset", "label": "Subsets", "type": "array"},
        {"field": "aliases", "label": "Aliases", "type": "array"},
        {"field": "keywords", "label": "Keywords", "type": "array"},
        {"field": "mappings", "label": "Mappings", "type": "array"},
    ],
}


def _collect_mappings(element: Any) -> List[str]:
    """Collect all mappings from a LinkML element into a single list."""
    mappings = []
    for attr in ['exact_mappings', 'close_mappings', 'related_mappings', 'broad_mappings', 'narrow_mappings']:
        values = getattr(element, attr, None)
        if values:
            mappings.extend(values)
    return mappings


def _add_if_present(d: Dict[str, Any], key: str, value: Any) -> None:
    """Add a key-value pair to dict only if value is truthy."""
    if value:
        d[key] = value


def _expand_uri(sv: SchemaView, uri: Optional[str]) -> Optional[str]:
    """Expand a CURIE to a full URI if possible."""
    if not uri:
        return None
    expanded = sv.expand_curie(uri)
    return expanded if expanded else uri


def _build_slot_to_classes_map(sv: SchemaView) -> Dict[str, List[str]]:
    """Build a mapping from slot names to the classes that use them."""
    slot_to_classes: Dict[str, List[str]] = {}
    for cls_name in sv.all_classes():
        for slot_name in sv.class_slots(cls_name):
            if slot_name not in slot_to_classes:
                slot_to_classes[slot_name] = []
            slot_to_classes[slot_name].append(cls_name)
    return slot_to_classes


def _build_enum_to_slots_map(sv: SchemaView) -> Dict[str, List[str]]:
    """Build a mapping from enum names to slots that use them as range."""
    enum_to_slots: Dict[str, List[str]] = {}
    for slot in sv.all_slots().values():
        if slot.range and slot.range in sv.all_enums():
            if slot.range not in enum_to_slots:
                enum_to_slots[slot.range] = []
            enum_to_slots[slot.range].append(slot.name)
    return enum_to_slots


def extract_linkml_elements(schema_paths: Union[Path, List[Path]]) -> List[Dict[str, Any]]:
    """Extract all elements from LinkML schema(s) as a flat list.

    Args:
        schema_paths: Path or list of paths to LinkML schema YAML file(s)

    Returns:
        List of element dictionaries with type field
    """
    # Handle single path or list of paths
    if isinstance(schema_paths, Path):
        schema_paths = [schema_paths]

    # Load and merge schemas
    sv = SchemaView(str(schema_paths[0]))
    for schema_path in schema_paths[1:]:
        sv.merge_schema(SchemaView(str(schema_path)).schema)

    elements = []

    # Build reverse mappings
    slot_to_classes = _build_slot_to_classes_map(sv)
    enum_to_slots = _build_enum_to_slots_map(sv)

    # Extract slots
    for slot in sv.all_slots().values():
        element: Dict[str, Any] = {
            "name": slot.name,
            "type": "slot_definition",
        }
        _add_if_present(element, "title", slot.title)
        _add_if_present(element, "description", slot.description)
        _add_if_present(element, "range", slot.range)
        _add_if_present(element, "required", slot.required)
        _add_if_present(element, "multivalued", slot.multivalued)
        _add_if_present(element, "in_subset", list(slot.in_subset) if slot.in_subset else None)
        # Use get_uri to get default URI if slot_uri not set
        slot_uri = slot.slot_uri or sv.get_uri(slot.name, expand=False)
        slot_url = sv.get_uri(slot.name, expand=True) if slot_uri else None
        _add_if_present(element, "uri", slot_uri)
        _add_if_present(element, "url", slot_url)
        _add_if_present(element, "classes", slot_to_classes.get(slot.name))
        _add_if_present(element, "domain", slot.domain)
        _add_if_present(element, "pattern", slot.pattern)
        _add_if_present(element, "minimum_value", slot.minimum_value)
        _add_if_present(element, "maximum_value", slot.maximum_value)
        _add_if_present(element, "keywords", list(slot.keywords) if slot.keywords else None)
        _add_if_present(element, "deprecated", slot.deprecated)
        _add_if_present(element, "comments", list(slot.comments) if slot.comments else None)
        _add_if_present(element, "aliases", list(slot.aliases) if slot.aliases else None)
        _add_if_present(element, "see_also", list(slot.see_also) if slot.see_also else None)
        mappings = _collect_mappings(slot)
        _add_if_present(element, "mappings", mappings)
        elements.append(element)

    # Extract classes
    for cls in sv.all_classes().values():
        element = {
            "name": cls.name,
            "type": "class_definition",
        }
        _add_if_present(element, "title", cls.title)
        _add_if_present(element, "description", cls.description)
        _add_if_present(element, "is_a", cls.is_a)
        _add_if_present(element, "mixins", list(cls.mixins) if cls.mixins else None)
        _add_if_present(element, "slots", list(sv.class_slots(cls.name)))
        # Use get_uri to get default URI if class_uri not set
        class_uri = cls.class_uri or sv.get_uri(cls.name, expand=False)
        class_url = sv.get_uri(cls.name, expand=True) if class_uri else None
        _add_if_present(element, "uri", class_uri)
        _add_if_present(element, "url", class_url)
        _add_if_present(element, "abstract", cls.abstract)
        _add_if_present(element, "mixin", cls.mixin)
        _add_if_present(element, "deprecated", cls.deprecated)
        _add_if_present(element, "comments", list(cls.comments) if cls.comments else None)
        _add_if_present(element, "aliases", list(cls.aliases) if cls.aliases else None)
        _add_if_present(element, "see_also", list(cls.see_also) if cls.see_also else None)
        mappings = _collect_mappings(cls)
        _add_if_present(element, "mappings", mappings)
        elements.append(element)

    # Extract enums
    for enum in sv.all_enums().values():
        element = {
            "name": enum.name,
            "type": "enum_definition",
        }
        _add_if_present(element, "title", enum.title)
        _add_if_present(element, "description", enum.description)
        # Use get_uri to get default URI if enum_uri not set
        enum_uri = enum.enum_uri or sv.get_uri(enum.name, expand=False)
        enum_url = sv.get_uri(enum.name, expand=True) if enum_uri else None
        _add_if_present(element, "uri", enum_uri)
        _add_if_present(element, "url", enum_url)
        # Add slots that use this enum as range
        enum_slots = enum_to_slots.get(enum.name, [])
        _add_if_present(element, "slots", enum_slots)
        # Add classes that use those slots (transitive)
        enum_classes = set()
        for slot_name in enum_slots:
            enum_classes.update(slot_to_classes.get(slot_name, []))
        _add_if_present(element, "classes", sorted(enum_classes) if enum_classes else None)
        if enum.permissible_values:
            element["permissible_values"] = list(enum.permissible_values.keys())
        _add_if_present(element, "deprecated", enum.deprecated)
        _add_if_present(element, "comments", list(enum.comments) if enum.comments else None)
        _add_if_present(element, "aliases", list(enum.aliases) if enum.aliases else None)
        _add_if_present(element, "see_also", list(enum.see_also) if enum.see_also else None)
        mappings = _collect_mappings(enum)
        _add_if_present(element, "mappings", mappings)
        elements.append(element)

    return elements


def get_linkml_browser_schema(title: Optional[str] = None, description: Optional[str] = None) -> Dict[str, Any]:
    """Get the browser schema for LinkML schemas with optional title override.

    Args:
        title: Optional custom title
        description: Optional custom description

    Returns:
        Browser schema dictionary
    """
    schema = LINKML_BROWSER_SCHEMA.copy()
    if title:
        schema["title"] = title
    if description:
        schema["description"] = description
    return schema