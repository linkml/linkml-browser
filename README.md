# LinkML Browser

Generate standalone, schema-driven faceted browsers for any tabular JSON dataset.

> ⚠️ **LinkML Schema Support**: Currently uses custom JSON schemas. Native LinkML schema support is planned - see our [LinkML Integration Roadmap](docs/linkml_integration.md) for details and timeline.

## Overview

LinkML Browser allows you to quickly create interactive, searchable web interfaces for browsing JSON data. It generates a standalone HTML/JavaScript application that provides:

- **Faceted search and filtering** - Filter data by multiple criteria simultaneously
- **Full-text search** - Search across specified fields with real-time results
- **High performance** - Client-side indexing for instant search results
- **Schema-driven** - Define facets, search fields, and display options via JSON schema
- **Standalone** - No server required, works entirely in the browser
- **Customizable** - Control which fields are searchable, filterable, and how they're displayed

## Installation

```bash
# Using uv (recommended)
uv add linkml-browser

# Or using pip
pip install linkml-browser
```

### Development Installation

```bash
# Clone the repository
git clone https://github.com/linkml/linkml-browser.git
cd linkml-browser

# Install with uv
uv sync

# Run commands with uv
uv run linkml-browser --help
```

## Quick Start

1. **Deploy a browser from your JSON data:**

```bash
linkml-browser deploy data.json output-directory/
```

This will:
- Analyze your data structure
- Generate an appropriate schema
- Create a standalone browser in `output-directory/`
- Open `output-directory/index.html` in your browser to view

2. **Customize with a schema:**

First, generate a schema template:
```bash
linkml-browser init-schema data.json --output schema.json
```

Edit `schema.json` to customize facets, search fields, and display options, then deploy:
```bash
linkml-browser deploy data.json output/ --schema schema.json
```

## Schema Format

The schema controls how your data is displayed and filtered:

```json
{
  "title": "My Data Browser",
  "description": "Browse and filter my data",
  "searchPlaceholder": "Search...",
  "searchableFields": ["title", "description", "tags"],
  "facets": [
    {
      "field": "category",
      "label": "Category",
      "type": "string",
      "sortBy": "count"
    },
    {
      "field": "tags",
      "label": "Tags",
      "type": "array",
      "sortBy": "alphabetical"
    },
    {
      "field": "year",
      "label": "Year",
      "type": "integer",
      "sortBy": "alphabetical"
    }
  ],
  "displayFields": [
    {"field": "title", "label": "Title", "type": "string"},
    {"field": "description", "label": "Description", "type": "string"},
    {"field": "category", "label": "Category", "type": "string"},
    {"field": "tags", "label": "Tags", "type": "array"}
  ]
}
```

### Schema Properties

- **title**: Browser title displayed at the top
- **description**: Subtitle text
- **searchPlaceholder**: Placeholder text for the search box
- **searchableFields**: Array of field names to include in full-text search
- **facets**: Array of facet configurations for filtering
- **displayFields**: Array of fields to show in search results

### Facet Types

- **string**: Single-value text fields (uses OR logic when multiple values selected)
- **array**: Multi-value fields (uses AND logic - items must have ALL selected values)
- **integer**: Numeric fields (displays as range filter with min/max inputs)

## Command Reference

### Show Help

```bash
# Show all available commands
linkml-browser --help

# Show help for a specific command
linkml-browser deploy --help
linkml-browser init-schema --help
```

### `deploy` - Generate a browser

```bash
linkml-browser deploy DATA_FILE OUTPUT_DIR [OPTIONS]
```

**Arguments:**
- `DATA_FILE`: Path to your JSON data file (required)
- `OUTPUT_DIR`: Directory where the browser will be created (required)

**Options:**
- `--schema, -s`: Path to custom schema file
- `--title, -t`: Browser title (default: "Data Browser")
- `--description, -d`: Browser description
- `--force, -f`: Overwrite existing output directory

**Examples:**
```bash
# Basic usage - will infer schema automatically
linkml-browser deploy mydata.json browser/

# With custom title and description
linkml-browser deploy mydata.json browser/ \
  --title "My Dataset" \
  --description "Explore my research data"

# Using a custom schema file
linkml-browser deploy mydata.json browser/ \
  --schema my-schema.json

# Force overwrite existing directory
linkml-browser deploy mydata.json browser/ --force
```

### `init-schema` - Generate a schema template

```bash
linkml-browser init-schema DATA_FILE [OPTIONS]
```

**Arguments:**
- `DATA_FILE`: Path to your JSON data file (required)

**Options:**
- `--output, -o`: Output schema file path (default: "schema.json")
- `--title, -t`: Browser title
- `--description, -d`: Browser description

**Examples:**
```bash
# Generate schema.json in current directory
linkml-browser init-schema mydata.json

# Specify output file and title
linkml-browser init-schema mydata.json \
  --output custom-schema.json \
  --title "Research Data Browser"
```

## Examples

### Example 1: Product Catalog

```bash
# Simple deployment
linkml-browser deploy products.json product-browser/

# With custom schema
linkml-browser init-schema products.json -o product-schema.json
# Edit product-schema.json to customize...
linkml-browser deploy products.json product-browser/ -s product-schema.json
```

### Example 2: Scientific Data

```bash
linkml-browser deploy experiments.json \
  experiment-browser/ \
  --title "Experiment Database" \
  --description "Browse and filter experimental results"
```

## Data Format

Your JSON data should be an array of objects:

```json
[
  {
    "id": "item-1",
    "title": "First Item",
    "category": "TypeA",
    "tags": ["tag1", "tag2"],
    "year": 2024
  },
  {
    "id": "item-2",
    "title": "Second Item",
    "category": "TypeB",
    "tags": ["tag2", "tag3"],
    "year": 2023
  }
]
```

## Features

### Faceted Filtering
- Click facet values to filter results
- Multiple selections within a facet use OR logic (for scalar fields)
- Array fields use AND logic (items must have ALL selected values)
- Numeric fields provide min/max range filtering

### Search
- Real-time search across configured fields
- Partial word matching
- Case-insensitive
- Combines with facet filters

### Performance
- Client-side indexing for instant results
- Handles thousands of items smoothly
- Shows search performance metrics

## Deployment

The generated browser is completely standalone:

1. **Local files**: Open `index.html` directly in a browser
2. **Web server**: Upload the entire output directory to any web server
3. **GitHub Pages**: Commit to a repository and enable GitHub Pages

No backend or database required!

## Future Plans

- Support for LinkML schemas (currently uses custom JSON schema format)
- Additional field types (dates, URLs, etc.)
- Export functionality
- Custom styling options
- Data validation

## Programmatic Usage

LinkML Browser can also be used as a Python library:

```python
from linkml_browser import BrowserGenerator, load_json_data

# Load your data
data = load_json_data("mydata.json")

# Create a browser generator
generator = BrowserGenerator(data)

# Generate browser files
generator.generate(output_dir="browser/", force=True)

# Or with a custom schema
from linkml_browser import load_schema

schema = load_schema("my-schema.json")
generator = BrowserGenerator(data, schema)
generator.generate(output_dir="browser/")
```

## Development

```bash
# Clone the repository
git clone https://github.com/linkml/linkml-browser.git
cd linkml-browser

# Install with uv
uv sync

# Run the CLI
uv run linkml-browser --help

# Run tests (when available)
uv run pytest
```

### Project Structure

```
linkml-browser/
├── src/linkml_browser/
│   ├── __init__.py      # Package exports
│   ├── core.py          # Core logic (BrowserGenerator)
│   ├── main.py          # CLI interface
│   └── index.html       # Browser template
├── pyproject.toml       # Project configuration
├── README.md            # This file
└── CLAUDE.md           # Development context
```

## License

This project is licensed under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.