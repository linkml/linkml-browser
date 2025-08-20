# CLAUDE.md - Project Context for LinkML Browser

## Project Overview

LinkML Browser is a Python tool that generates standalone, schema-driven faceted browsers for any tabular JSON dataset. The generated browsers are self-contained HTML/JavaScript applications that work entirely in the browser without requiring a server.

## Key Features

- **Faceted search and filtering** - Filter data by multiple criteria
- **Full-text search** - Real-time search across specified fields
- **High performance** - Client-side indexing for instant results
- **Schema-driven** - Define facets, search fields, and display via JSON
- **Standalone** - No server required, works entirely in the browser
- **Auto-inference** - Can automatically generate schemas from data

## Architecture

### Core Components

1. **`src/linkml_browser/core.py`** - Core logic
   - `BrowserGenerator` class - Main browser generation logic
   - Schema inference from data
   - File generation (data.js, schema.js)

2. **`src/linkml_browser/main.py`** - CLI interface
   - `deploy` command - Generate browser from data
   - `init-schema` command - Create schema template

3. **`src/linkml_browser/index.html`** - Browser template
   - Self-contained HTML with embedded JavaScript
   - Faceted search implementation
   - Performance optimizations (inverted index)

### Schema Format

The schema controls how data is displayed and filtered:

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
      "type": "string|array"
    }
  ]
}
```

### Field Types

- **string**: Single-value text fields (OR logic for multiple selections)
- **array**: Multi-value fields (AND logic - items must have ALL selected values)
- **integer**: Numeric fields (range filter with min/max)

## Development Guidelines

### Code Style
- Use type hints for all function parameters and returns
- Follow PEP 8 conventions
- Keep logic separated from CLI interface
- Document all public methods

### Testing Commands
```bash
# Install dependencies
uv sync

# Test deploy command
uv run linkml-browser deploy sample_data.json output/

# Test schema generation
uv run linkml-browser init-schema sample_data.json
```

### Common Tasks

1. **Adding a new field type**:
   - Update schema inference in `core.py`
   - Add rendering logic in `index.html`
   - Update facet generation logic

2. **Improving search performance**:
   - The search uses an inverted index built in `buildSearchIndex()`
   - Consider adding n-gram support for fuzzy matching

3. **Adding export functionality**:
   - Add export buttons to the UI
   - Implement CSV/JSON export of filtered results

## Dependencies

- **typer**: CLI framework
- **linkml**: Future schema support (not yet implemented)
- **linkml-store**: Future data storage support

## Future Enhancements

1. **LinkML Schema Support**: Currently uses custom JSON schema format. Plan to support LinkML schemas for better interoperability.

2. **Additional Field Types**:
   - Date/datetime with date range pickers
   - URL fields with automatic linking
   - Hierarchical/nested categories

3. **UI Improvements**:
   - Custom themes/styling
   - Responsive mobile design
   - Export filtered results

4. **Performance**:
   - Web worker for indexing large datasets
   - Virtual scrolling for result lists
   - Progressive loading

## Known Issues

- Very large datasets (>10k items) may have initial loading delays
- Integer facets don't preserve selection after search
- No validation of schema against data structure

## Useful Links

- [Typer Documentation](https://typer.tiangolo.com/)
- [LinkML Documentation](https://linkml.io/)
- [UV Package Manager](https://github.com/astral-sh/uv)