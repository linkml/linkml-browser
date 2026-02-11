"""Unit tests for LinkML Browser generator functionality."""

import tempfile
from pathlib import Path

import pytest

from linkml_browser.core import (
    BrowserGenerator,
    extract_linkml_elements,
    get_linkml_browser_schema,
    load_json_data,
)


class TestBrowserGenerator:
    """Test the BrowserGenerator class functionality."""
    
    @pytest.fixture
    def test_data(self):
        """Load test data fixture."""
        test_file = Path(__file__).parent / "test_data.json"
        return load_json_data(test_file)
    
    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary output directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    def test_browser_generator_creation(self, test_data):
        """Test creating a BrowserGenerator instance."""
        generator = BrowserGenerator(test_data)
        
        assert generator.data == test_data
        assert generator.schema is not None
        assert isinstance(generator.schema, dict)
    
    def test_schema_inference(self, test_data):
        """Test automatic schema inference from data."""
        generator = BrowserGenerator(test_data)
        schema = generator.schema
        
        # Check schema structure
        assert "title" in schema
        assert "description" in schema
        assert "searchableFields" in schema
        assert "facets" in schema
        assert "displayFields" in schema
        
        # Check that some expected fields are searchable
        searchable_fields = schema["searchableFields"]
        assert "title" in searchable_fields
        assert "author" in searchable_fields
        assert "description" in searchable_fields
        
        # Check that facets were created
        facets = schema["facets"]
        facet_fields = [f["field"] for f in facets]
        
        # Should have facets for multi-valued array field
        assert "genre" in facet_fields
        
        # Should have facets for reasonable enum-like string fields
        assert "author" in facet_fields or "language" in facet_fields
        
        # Should have integer facets
        assert any(f["type"] == "integer" for f in facets)
        
        # Check display fields
        display_fields = schema["displayFields"]
        display_field_names = [f["field"] for f in display_fields]
        assert "title" in display_field_names
        assert "author" in display_field_names
    
    def test_deploy_equivalent(self, test_data, temp_output_dir):
        """Test the programmatic equivalent of linkml-browser deploy."""
        # This is the programmatic equivalent of:
        # linkml-browser deploy data.json output-directory/
        
        generator = BrowserGenerator(test_data)
        generator.generate(temp_output_dir, force=True)
        
        # Check that all required files were created
        assert (temp_output_dir / "index.html").exists()
        assert (temp_output_dir / "data.js").exists()
        assert (temp_output_dir / "schema.js").exists()
        
        # Check that index.html is not empty
        index_content = (temp_output_dir / "index.html").read_text()
        assert len(index_content) > 1000  # Should be substantial HTML
        assert "<!DOCTYPE html>" in index_content
        
        # Check that data.js contains the test data
        data_js_content = (temp_output_dir / "data.js").read_text()
        assert "window.searchData" in data_js_content
        assert "The Great Gatsby" in data_js_content
        assert "Harper Lee" in data_js_content
        
        # Check that schema.js contains the schema
        schema_js_content = (temp_output_dir / "schema.js").read_text()
        assert "window.searchSchema" in schema_js_content
        assert "searchableFields" in schema_js_content
        assert "facets" in schema_js_content
    
    def test_custom_schema(self, test_data, temp_output_dir):
        """Test using a custom schema instead of inferred one."""
        custom_schema = {
            "title": "Test Book Browser",
            "description": "A test browser for books",
            "searchPlaceholder": "Search books...",
            "searchableFields": ["title", "author"],
            "facets": [
                {
                    "field": "genre",
                    "label": "Genre",
                    "type": "array",
                    "sortBy": "count"
                },
                {
                    "field": "publication_year",
                    "label": "Publication Year", 
                    "type": "integer",
                    "sortBy": "alphabetical"
                }
            ],
            "displayFields": [
                {"field": "title", "label": "Title", "type": "string"},
                {"field": "author", "label": "Author", "type": "string"},
                {"field": "genre", "label": "Genres", "type": "array"}
            ]
        }
        
        generator = BrowserGenerator(test_data, custom_schema)
        generator.generate(temp_output_dir, force=True)
        
        # Check that custom schema was used
        schema_js_content = (temp_output_dir / "schema.js").read_text()
        assert "Test Book Browser" in schema_js_content
        assert "Search books..." in schema_js_content
    
    def test_force_overwrite(self, test_data, temp_output_dir):
        """Test that force=True overwrites existing directory."""
        # Create initial deployment
        generator = BrowserGenerator(test_data)
        generator.generate(temp_output_dir, force=True)
        
        # Modify a file
        (temp_output_dir / "test_marker.txt").write_text("test")
        
        # Deploy again with force=True
        generator.generate(temp_output_dir, force=True) 
        
        # Marker file should be gone
        assert not (temp_output_dir / "test_marker.txt").exists()
        
        # But required files should still exist
        assert (temp_output_dir / "index.html").exists()
        assert (temp_output_dir / "data.js").exists()
        assert (temp_output_dir / "schema.js").exists()
    
    def test_no_force_fails_on_existing(self, test_data, temp_output_dir):
        """Test that deploy fails on existing directory without force=True."""
        # Create initial deployment
        generator = BrowserGenerator(test_data)
        generator.generate(temp_output_dir, force=True)
        
        # Try to deploy again without force - should fail
        with pytest.raises(FileExistsError):
            generator.generate(temp_output_dir, force=False)
    
    def test_empty_data_fails(self):
        """Test that empty data raises appropriate error."""
        with pytest.raises(ValueError, match="Cannot infer schema from empty data"):
            BrowserGenerator([])
    
    def test_load_json_data(self):
        """Test the load_json_data utility function."""
        test_file = Path(__file__).parent / "test_data.json"
        data = load_json_data(test_file)

        assert isinstance(data, list)
        assert len(data) == 50
        assert data[0]["title"] == "The Great Gatsby"
        assert data[1]["author"] == "Harper Lee"


class TestLinkMLSchemaExtraction:
    """Test LinkML schema extraction functionality."""

    @pytest.fixture
    def minimal_schema_path(self, tmp_path):
        """Create a minimal LinkML schema for testing."""
        schema_content = """
id: https://example.org/test
name: test_schema
prefixes:
  linkml: https://w3id.org/linkml/
  ex: https://example.org/

default_range: string

subsets:
  test_subset:
    description: A test subset

enums:
  StatusEnum:
    description: Status values
    permissible_values:
      active:
        description: Active status
      inactive:
        description: Inactive status

slots:
  id:
    identifier: true
    range: string
  name:
    title: Name
    description: The name of the entity
    required: true
    slot_uri: ex:name
    in_subset:
      - test_subset
  status:
    range: StatusEnum
  tags:
    multivalued: true
    range: string

classes:
  NamedThing:
    abstract: true
    description: A generic named thing
    slots:
      - id
      - name
  Person:
    is_a: NamedThing
    description: A person
    class_uri: ex:Person
    slots:
      - status
      - tags
"""
        schema_file = tmp_path / "test_schema.yaml"
        schema_file.write_text(schema_content)
        return schema_file

    def test_extract_linkml_elements(self, minimal_schema_path):
        """Test extracting elements from a LinkML schema."""
        elements = extract_linkml_elements(minimal_schema_path)

        assert isinstance(elements, list)
        assert len(elements) > 0

        # Check we have all three element types
        types = {el["type"] for el in elements}
        assert "slot_definition" in types
        assert "class_definition" in types
        assert "enum_definition" in types

        # Find specific elements
        slots = [el for el in elements if el["type"] == "slot_definition"]
        classes = [el for el in elements if el["type"] == "class_definition"]
        enums = [el for el in elements if el["type"] == "enum_definition"]

        # Check slot extraction
        name_slot = next((s for s in slots if s["name"] == "name"), None)
        assert name_slot is not None
        assert name_slot["title"] == "Name"
        assert name_slot["description"] == "The name of the entity"
        assert name_slot["required"] is True
        assert name_slot["uri"] == "ex:name"
        assert name_slot["url"] == "https://example.org/name"  # Expanded URI
        assert "test_subset" in name_slot["in_subset"]
        # Check classes field (slots should list which classes use them)
        assert "classes" in name_slot
        assert "NamedThing" in name_slot["classes"]
        assert "Person" in name_slot["classes"]

        # Check class extraction
        person_class = next((c for c in classes if c["name"] == "Person"), None)
        assert person_class is not None
        assert person_class["is_a"] == "NamedThing"
        assert person_class["description"] == "A person"
        assert person_class["uri"] == "ex:Person"
        assert person_class["url"] == "https://example.org/Person"  # Expanded URI
        assert "status" in person_class["slots"]
        assert "tags" in person_class["slots"]

        # Check abstract class
        named_thing = next((c for c in classes if c["name"] == "NamedThing"), None)
        assert named_thing is not None
        assert named_thing["abstract"] is True

        # Check enum extraction
        status_enum = next((e for e in enums if e["name"] == "StatusEnum"), None)
        assert status_enum is not None
        assert status_enum["description"] == "Status values"
        assert "active" in status_enum["permissible_values"]
        assert "inactive" in status_enum["permissible_values"]

    def test_get_linkml_browser_schema(self):
        """Test getting the browser schema for LinkML."""
        schema = get_linkml_browser_schema()

        assert schema["title"] == "Schema Browser"
        assert "searchableFields" in schema
        assert "name" in schema["searchableFields"]
        assert "facets" in schema
        assert "displayFields" in schema

        # Check custom title override
        custom_schema = get_linkml_browser_schema(title="Custom Title", description="Custom desc")
        assert custom_schema["title"] == "Custom Title"
        assert custom_schema["description"] == "Custom desc"

    def test_deploy_schema_integration(self, minimal_schema_path, temp_output_dir):
        """Test the full deploy-schema workflow."""
        elements = extract_linkml_elements(minimal_schema_path)
        browser_schema = get_linkml_browser_schema(title="Test Schema Browser")

        generator = BrowserGenerator(elements, browser_schema)
        generator.generate(temp_output_dir, force=True)

        # Check output files
        assert (temp_output_dir / "index.html").exists()
        assert (temp_output_dir / "data.js").exists()
        assert (temp_output_dir / "schema.js").exists()

        # Check data.js content
        data_js = (temp_output_dir / "data.js").read_text()
        assert "slot_definition" in data_js
        assert "class_definition" in data_js
        assert "enum_definition" in data_js

        # Check schema.js content
        schema_js = (temp_output_dir / "schema.js").read_text()
        assert "Test Schema Browser" in schema_js
        assert "Element Type" in schema_js

    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary output directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
