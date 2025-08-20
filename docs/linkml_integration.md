# LinkML Integration for LinkML Browser

## Executive Summary

This document outlines comprehensive approaches for integrating LinkML schemas into the LinkML Browser, moving from the current custom JSON schema format to native LinkML schema support. Two primary approaches are analyzed: client-side integration using linkml-runtime.js and server-side generation using a custom LinkML generator.

## Current State Analysis

### Current Browser Schema Format

The browser currently uses a custom JSON schema format:

```json
{
  "title": "Browser Title",
  "description": "Browser description",
  "searchPlaceholder": "Search...",
  "searchableFields": ["field1", "field2"],
  "facets": [
    {
      "field": "category",
      "label": "Category",
      "type": "string|array|integer",
      "sortBy": "count|alphabetical"
    }
  ],
  "displayFields": [
    {
      "field": "title",
      "label": "Title", 
      "type": "string|array|integer"
    }
  ]
}
```

### Schema Inference Logic

The current `BrowserGenerator.infer_schema()` method:

1. **Field Analysis**: Examines data types (arrays, strings, numbers)
2. **Facet Generation**: Creates facets for fields with 1-100 unique values
3. **Type Detection**: Automatically determines string/array/integer types
4. **Search Fields**: Prefers string and array fields for searchability
5. **Display Fields**: Includes all fields in results display

## Integration Approaches

### Approach 1: Python Generator (Recommended)

Create a custom LinkML generator that produces browser-compatible JSON schemas.

#### Architecture

```python
from linkml.utils.generator import Generator
from linkml_runtime.utils.schemaview import SchemaView

class BrowserGenerator(Generator):
    """Generate browser schemas from LinkML schemas."""
    
    valid_formats = ['browser-json']
    uses_schemaloader = False
    
    def __init__(self, schema, **kwargs):
        super().__init__(schema, **kwargs)
        self.schema_view = SchemaView(schema)
    
    def serialize(self) -> str:
        """Generate browser JSON schema."""
        browser_schema = {
            "title": self._get_title(),
            "description": self._get_description(),
            "searchPlaceholder": self._get_search_placeholder(),
            "searchableFields": self._get_searchable_fields(),
            "facets": self._generate_facets(),
            "displayFields": self._generate_display_fields()
        }
        return json.dumps(browser_schema, indent=2)
```

#### LinkML-Native Configuration with Slot Groups

Leverage LinkML's built-in metamodel fields and slot groups for browser configuration:

```yaml
# Example LinkML schema using built-in fields
id: https://example.org/books
name: book-catalog
title: Book Catalog Browser
description: Browse and search through books

prefixes:
  browser: https://linkml.io/linkml-browser/

# Define slot groups for UI organization
slot_groups:
  core_metadata:
    title: Core Information
    description: Essential book metadata
    rank: 1
  publication_info:
    title: Publication Details
    description: Publishing and bibliographic information
    rank: 2
  categorization:
    title: Categories and Tags
    description: Genre and subject classification
    rank: 3

classes:
  Book:
    title: Book
    description: A published work in any format
    slot_usage:
      title:
        title: Book Title
        description: The main title of the book
        slot_group: core_metadata
        rank: 1
        required: true
        # Searchable inferred from string type
      
      author:
        title: Author(s)
        description: Person(s) who wrote the book
        slot_group: core_metadata
        rank: 2
        multivalued: true
        required: true
        # Facet inferred from multivalued string
        
      publication_year:
        title: Publication Year
        description: Year the book was first published
        slot_group: publication_info
        rank: 1
        # Integer facet inferred from range
        
      genre:
        title: Genre(s)
        description: Literary or subject categories
        slot_group: categorization
        rank: 1
        multivalued: true
        # Array facet inferred from multivalued enum

slots:
  title:
    range: string
    description: Primary title of the work
    
  author:
    range: string
    multivalued: true
    description: Creator(s) of the work
    
  publication_year:
    range: integer
    minimum_value: 1
    maximum_value: 2030
    description: Year of publication
    
  genre:
    range: Genre
    multivalued: true
    description: Classification by subject or style

enums:
  Genre:
    title: Literary Genre
    description: Categories of literary works
    permissible_values:
      fiction:
        title: Fiction
        description: Imaginative literary work
      non_fiction:
        title: Non-Fiction  
        description: Factual or informational work
      science:
        title: Science
        description: Scientific or technical work
      history:
        title: History
        description: Historical accounts and analysis
```

#### Browser-Specific Annotations (Minimal)

Only use custom annotations for browser-specific features not covered by LinkML built-ins:

```yaml
annotations:
  browser:search_placeholder: Search by title, author, or description...
  browser:theme: light
  browser:results_per_page: 25
  browser:enable_export: true

slots:
  isbn:
    range: string
    annotations:
      browser:format: isbn  # Custom formatting
      browser:searchable: false  # Override default behavior
      
  cover_image:
    range: uri
    annotations:
      browser:render_as: image  # Special UI treatment
      browser:thumbnail_size: 150
```

#### Processing Logic Using LinkML Built-ins

```python
def _get_searchable_fields(self) -> List[str]:
    """Extract searchable fields using LinkML built-in inference."""
    searchable = []
    for class_name in self.schema_view.all_classes():
        for slot_name in self.schema_view.class_slots(class_name):
            slot = self.schema_view.get_slot(slot_name)
            if self._is_searchable(slot):
                searchable.append(slot_name)
    return searchable

def _is_searchable(self, slot) -> bool:
    """Determine searchability using LinkML semantics + optional override."""
    # Check for explicit browser annotation override
    if slot.annotations and 'browser:searchable' in slot.annotations:
        return slot.annotations['browser:searchable']
    
    # Default inference from LinkML semantics:
    # - String fields are searchable
    # - Multivalued string fields are searchable  
    # - Text fields with descriptions are searchable
    return (slot.range == 'string' or 
            (slot.multivalued and slot.range == 'string') or
            (slot.range == 'string' and slot.description))

def _get_slot_title(self, slot) -> str:
    """Get display title using LinkML's built-in title field."""
    # Use LinkML's built-in title field first
    if slot.title:
        return slot.title
    # Fall back to formatted slot name
    return slot.name.replace('_', ' ').title()

def _get_slot_rank(self, slot) -> int:
    """Get display order using LinkML's built-in rank field."""
    return slot.rank if slot.rank is not None else 999
```

#### Facet Generation with Slot Groups

```python
def _generate_facets(self) -> List[Dict[str, Any]]:
    """Generate facet configurations from LinkML schema using built-in fields."""
    facets = []
    for class_name in self.schema_view.all_classes():
        for slot_name in self.schema_view.class_slots(class_name):
            slot = self.schema_view.get_slot(slot_name)
            if self._should_create_facet(slot):
                facet = {
                    "field": slot_name,
                    "label": self._get_slot_title(slot),  # Use built-in title
                    "type": self._get_facet_type(slot),
                    "sortBy": self._get_facet_sort(slot),
                    "group": self._get_slot_group_title(slot)  # Group info
                }
                facets.append(facet)
    return sorted(facets, key=lambda f: (
        self._get_slot_group_rank(f["field"]),  # Group rank first
        self._get_slot_rank(self.schema_view.get_slot(f["field"]))  # Slot rank second
    ))

def _should_create_facet(self, slot) -> bool:
    """Determine if slot should be a facet using LinkML semantics."""
    # Check explicit browser annotation
    if slot.annotations and 'browser:facet' in slot.annotations:
        return slot.annotations['browser:facet']
    
    # Infer from LinkML characteristics:
    # - Enums make good facets
    # - Multivalued fields make good facets  
    # - Required fields are often good facets
    # - Fields with limited ranges make good facets
    return (self.schema_view.get_enum(slot.range) is not None or
            slot.multivalued or
            slot.range in ['integer', 'float'] or
            (slot.required and slot.range == 'string'))

def _get_slot_group_title(self, slot) -> Optional[str]:
    """Get slot group title for facet organization."""
    if slot.slot_group:
        group = self.schema_view.get_slot_group(slot.slot_group)
        return group.title if group and group.title else slot.slot_group
    return None

def _get_slot_group_rank(self, slot_name: str) -> int:
    """Get slot group rank for ordering."""
    slot = self.schema_view.get_slot(slot_name)
    if slot.slot_group:
        group = self.schema_view.get_slot_group(slot.slot_group)
        return group.rank if group and group.rank is not None else 999
    return 999
```

#### Type Mapping

```python
def _get_facet_type(self, slot) -> str:
    """Map LinkML slot to browser facet type."""
    # Check explicit annotation
    if slot.annotations and 'browser:facet_type' in slot.annotations:
        return slot.annotations['browser:facet_type']
    
    # Infer from LinkML schema
    if slot.multivalued:
        return "array"
    elif slot.range in ['integer', 'float']:
        return "integer" 
    else:
        return "string"
```

#### Implementation Plan

1. **Phase 1**: Basic Generator
   - Create `BrowserGenerator` class extending LinkML's `Generator`
   - Implement core schema transformation logic
   - Support basic field mapping (slots → browser fields)

2. **Phase 2**: Annotation System  
   - Define browser-specific annotation vocabulary
   - Implement annotation processing logic
   - Add support for UI customization via annotations

3. **Phase 3**: Advanced Features
   - Support for enums and controlled vocabularies
   - Hierarchical facets for nested data
   - Custom field renderers and formatters

4. **Phase 4**: Integration
   - Update CLI to support LinkML schema input
   - Add schema validation and error handling
   - Documentation and examples

### Approach 2: Client-Side Integration

Use linkml-runtime.js for real-time schema processing in the browser.

#### Architecture

```javascript
// Load LinkML schema and process client-side
import { SchemaView } from 'linkml-runtime-js';

class LinkMLBrowserGenerator {
    constructor(linkmlSchema) {
        this.schemaView = new SchemaView(linkmlSchema);
        this.browserSchema = null;
    }
    
    generateBrowserSchema() {
        this.browserSchema = {
            title: this.getSchemaTitle(),
            description: this.getSchemaDescription(),
            searchableFields: this.extractSearchableFields(),
            facets: this.generateFacets(),
            displayFields: this.generateDisplayFields()
        };
        return this.browserSchema;
    }
}
```

#### Pros and Cons

**Pros:**
- Real-time schema updates without regeneration
- Dynamic schema loading from URLs
- Full client-side operation
- Enables schema editing interfaces

**Cons:**
- linkml-runtime.js is experimental/alpha state
- Limited functionality compared to Python runtime
- Increased client-side bundle size
- Dependency on external JavaScript library

### Approach 3: Hybrid Approach

Combine both approaches for maximum flexibility.

#### Architecture

1. **Default**: Use Python generator for static deployments
2. **Advanced**: Optionally include linkml-runtime.js for dynamic schemas
3. **Configuration**: Allow users to choose their preferred approach

```bash
# Static generation (default)
linkml-browser deploy --schema schema.yaml data.json output/

# Dynamic schema loading
linkml-browser deploy --dynamic-schema data.json output/
```

## Enhanced UI Configuration Strategy

### Leveraging LinkML Built-in Fields

**Primary Strategy**: Use LinkML's native metamodel fields wherever possible:

| Browser Feature | LinkML Built-in | Custom Annotation |
|-----------------|-----------------|-------------------|
| Field Label | `title` | `browser:label` (fallback) |
| Field Order | `rank` | `browser:display_priority` (fallback) |
| Field Description | `description` | `browser:tooltip` (additional) |
| Field Grouping | `slot_group` | `browser:section` (fallback) |
| Deprecation | `deprecated` | N/A |
| Alternative Names | `aliases` | N/A |
| Required Fields | `required` | N/A |
| Multi-valued | `multivalued` | N/A |
| Data Types | `range` | N/A |

### Schema-Level Configuration

```yaml
# Use LinkML built-ins for schema metadata
id: https://example.org/schema
name: my-schema
title: "My Data Browser"  # Browser title
description: "Browse and explore my data"  # Browser subtitle

# Minimal browser-specific annotations
annotations:
  browser:search_placeholder: "Search items..."
  browser:theme: light
  browser:results_per_page: 25
```

### Slot Group Organization

```yaml
slot_groups:
  core:
    title: "Core Information"
    description: "Essential identifying information"
    rank: 1
  metadata:
    title: "Metadata"
    description: "Additional descriptive information"
    rank: 2
  technical:
    title: "Technical Details"
    description: "System and technical attributes"
    rank: 3
```

### Class and Slot Configuration

```yaml
classes:
  MyClass:
    title: "Data Item"
    description: "Primary data entity"
    slot_usage:
      identifier:
        title: "ID"
        description: "Unique identifier"
        rank: 1
        slot_group: core
        required: true
      name:
        title: "Name"
        description: "Human-readable name"
        rank: 2
        slot_group: core
        required: true
      category:
        title: "Category"
        description: "Classification type"
        rank: 1
        slot_group: metadata
        # Facet inferred from enum range
      tags:
        title: "Tags"
        description: "Descriptive keywords"
        rank: 2
        slot_group: metadata
        multivalued: true
        # Array facet inferred from multivalued
```

### Browser-Specific Annotations (Minimal)

Only for features not expressible through LinkML built-ins:

```yaml
slots:
  special_field:
    title: "Special Field"
    range: string
    annotations:
      # Override default inference
      browser:searchable: false
      browser:facet: false
      
      # Custom formatting
      browser:format: "currency"
      browser:decimal_places: 2
      
      # Special rendering
      browser:render_as: "progress_bar"
      browser:color_scale: ["red", "yellow", "green"]
      
      # Advanced features
      browser:export_format: "excel_formula"
      browser:validation_regex: "^[A-Z]{2,3}-\\d{4}$"
```

### Enum Configuration

```yaml
enums:
  Priority:
    title: "Priority Level"
    description: "Task or item priority"
    permissible_values:
      high:
        title: "High Priority"
        description: "Urgent items requiring immediate attention"
        annotations:
          browser:color: "#ff0000"
          browser:icon: "🔥"
      medium:
        title: "Medium Priority"
        description: "Standard priority items"
        annotations:
          browser:color: "#ffaa00"
          browser:icon: "⚡"
      low:
        title: "Low Priority"
        description: "Lower priority items"
        annotations:
          browser:color: "#00aa00"
          browser:icon: "📝"
```

## Implementation Roadmap

### Phase 1: Core Generator (4-6 weeks)

**Week 1-2: Generator Foundation**
- [ ] Create `BrowserGenerator` class extending LinkML `Generator`
- [ ] Implement basic schema parsing and validation
- [ ] Create core transformation logic for classes → display fields
- [ ] Add unit tests for generator functionality

**Week 3-4: Annotation System**  
- [ ] Define browser annotation vocabulary specification
- [ ] Implement annotation extraction and processing
- [ ] Add support for slot-level UI configuration
- [ ] Create annotation validation logic

**Week 5-6: Integration**
- [ ] Update CLI to accept LinkML schemas via `--linkml-schema` flag
- [ ] Add schema format auto-detection (LinkML vs JSON)
- [ ] Implement backward compatibility with existing JSON schemas
- [ ] Add comprehensive error handling and user feedback

### Phase 2: Advanced Features (3-4 weeks)

**Week 1-2: Type System Enhancement**
- [ ] Add support for LinkML built-in types (date, time, uri, etc.)
- [ ] Implement enum facet generation with permissible values
- [ ] Add range validation for numeric facets
- [ ] Support for units and formatting annotations

**Week 3-4: UI Enhancements**
- [ ] Add support for hierarchical facets (tree-like categories)
- [ ] Implement custom field formatters (dates, currencies, links)
- [ ] Add theming support via annotations
- [ ] Create field ordering and grouping features

### Phase 3: Client-Side Integration (2-3 weeks)

**Week 1: Runtime Evaluation**
- [ ] Evaluate linkml-runtime.js stability and feature completeness
- [ ] Create proof-of-concept client-side schema processing
- [ ] Performance testing with large schemas

**Week 2-3: Optional Integration**
- [ ] Implement hybrid mode supporting both approaches
- [ ] Add CLI flags for dynamic vs static schema processing
- [ ] Create documentation for both approaches

### Phase 4: Documentation and Examples (1-2 weeks)

**Week 1: Documentation**
- [ ] Create comprehensive LinkML integration guide
- [ ] Document annotation vocabulary with examples
- [ ] Add migration guide from JSON to LinkML schemas

**Week 2: Examples and Testing**  
- [ ] Convert existing gallery examples to LinkML schemas
- [ ] Create complex schema examples demonstrating advanced features
- [ ] Add integration tests with real-world schemas

## Migration Strategy

### Backward Compatibility

Maintain full backward compatibility with existing JSON schemas:

```python
def load_schema(schema_path: Path) -> Dict[str, Any]:
    """Load schema from LinkML YAML or legacy JSON format."""
    if schema_path.suffix in ['.yaml', '.yml']:
        # LinkML schema - generate browser schema
        from linkml_browser.generators import BrowserGenerator
        generator = BrowserGenerator(schema_path)
        return json.loads(generator.serialize())
    else:
        # Legacy JSON schema
        return json.load(open(schema_path))
```

### Migration Tools

Create migration utilities to help users transition:

```bash
# Convert existing JSON schema to LinkML
linkml-browser migrate-schema schema.json --output schema.yaml

# Analyze data and suggest LinkML schema structure
linkml-browser suggest-schema data.json --output suggested-schema.yaml
```

## Performance Considerations

### Schema Processing Performance

- **Python Generator**: Fast build-time processing, zero runtime overhead
- **Client-Side**: Minimal build overhead, but runtime processing cost
- **Caching**: Implement schema processing cache for development workflows

### Bundle Size Impact

- **Python Generator**: No impact on client bundle size
- **Client-Side**: Adds ~100KB+ for linkml-runtime.js dependency
- **Hybrid**: Optional loading based on schema complexity

## Risk Assessment

### Technical Risks

1. **linkml-runtime.js Maturity**: Current alpha state may have limitations
   - **Mitigation**: Start with Python generator, add client-side later
   
2. **Schema Complexity**: Large, complex schemas may impact performance
   - **Mitigation**: Implement schema validation and optimization warnings
   
3. **Breaking Changes**: LinkML API changes could affect generator
   - **Mitigation**: Pin LinkML version, comprehensive testing

### User Experience Risks

1. **Migration Complexity**: Users need to learn LinkML syntax
   - **Mitigation**: Provide migration tools and comprehensive documentation
   
2. **Feature Parity**: LinkML integration should match current capabilities
   - **Mitigation**: Systematic testing against existing gallery examples

## Success Metrics

### Technical Metrics

- [ ] 100% backward compatibility with existing JSON schemas
- [ ] <500ms schema processing time for typical schemas (<100 classes)
- [ ] Zero breaking changes to CLI interface
- [ ] 95%+ test coverage for generator code

### User Experience Metrics

- [ ] Successful migration of all gallery examples
- [ ] Documentation completeness (all features documented with examples)
- [ ] Community feedback integration (GitHub issues, discussions)

## Conclusion

**Recommended Approach**: Start with **Approach 1 (Python Generator)** leveraging LinkML's built-in metamodel fields:

1. **Standards Alignment**: Uses LinkML's native `title`, `rank`, `slot_group`, and other built-in fields
2. **Minimal Custom Annotations**: Only adds browser-specific annotations where LinkML lacks native support
3. **Semantic Inference**: Automatically infers searchability, facets, and display from LinkML semantics
4. **Maintainability**: Reduces custom vocabulary and leverages LinkML's evolving standards
5. **Ecosystem Integration**: Aligns with LinkML tooling and conventions

**Key Benefits of Built-in Field Strategy**:

- **`title`** → Field labels (instead of custom `browser:label`)
- **`rank`** → Display order (instead of custom `browser:display_priority`) 
- **`slot_group`** → Field organization and facet grouping
- **`description`** → Tooltips and help text
- **`multivalued`** → Automatic array facet inference
- **`required`** → Required field highlighting
- **`deprecated`** → Field deprecation warnings
- **`aliases`** → Alternative search terms

**Minimal Custom Annotations**: Reserved for truly browser-specific features:
- UI theming and styling
- Custom field formatters and renderers
- Export configurations
- Performance optimizations

This approach positions LinkML Browser as a natural extension of the LinkML ecosystem, reducing learning curve and increasing interoperability with other LinkML tools while maintaining the flexibility needed for advanced data exploration interfaces.