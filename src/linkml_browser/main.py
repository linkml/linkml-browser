"""CLI interface for LinkML Browser."""

import json
from pathlib import Path
from typing import Optional

import typer
from typing_extensions import Annotated

from .core import BrowserGenerator, load_json_data, load_schema, save_schema

app = typer.Typer(help="LinkML Browser: Generate standalone faceted browsers for tabular JSON datasets")


@app.command()
def deploy(
    data_file: Annotated[Path, typer.Argument(help="Path to JSON data file")],
    output_dir: Annotated[Path, typer.Argument(help="Output directory for the browser")],
    schema_file: Annotated[Optional[Path], typer.Option("--schema", "-s", help="Path to schema JSON file")] = None,
    title: Annotated[str, typer.Option("--title", "-t", help="Browser title")] = "Data Browser",
    description: Annotated[str, typer.Option("--description", "-d", help="Browser description")] = "Browse and filter data",
    force: Annotated[bool, typer.Option("--force", "-f", help="Overwrite existing output directory")] = False
):
    """Deploy a standalone faceted browser for your JSON data."""
    
    # Validate input file
    if not data_file.exists():
        typer.echo(f"Error: Data file '{data_file}' not found", err=True)
        raise typer.Exit(1)
    
    # Load data
    try:
        data = load_json_data(data_file)
    except (json.JSONDecodeError, ValueError) as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)
    
    typer.echo(f"Loaded {len(data)} items from {data_file}")
    
    # Load or infer schema
    if schema_file:
        if not schema_file.exists():
            typer.echo(f"Error: Schema file '{schema_file}' not found", err=True)
            raise typer.Exit(1)
        
        try:
            schema = load_schema(schema_file)
            typer.echo(f"Loaded schema from {schema_file}")
        except json.JSONDecodeError as e:
            typer.echo(f"Error: Invalid JSON in '{schema_file}': {e}", err=True)
            raise typer.Exit(1)
    else:
        typer.echo("No schema provided, inferring from data...")
        # Create a temporary generator to infer schema
        generator = BrowserGenerator(data)
        schema = generator.infer_schema(title, description)
        typer.echo(f"Inferred schema with {len(schema['facets'])} facets")
    
    # Generate browser
    try:
        generator = BrowserGenerator(data, schema)
        generator.generate(output_dir, force)
    except FileExistsError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"Error generating browser: {e}", err=True)
        raise typer.Exit(1)
    
    typer.echo("Copied index.html")
    typer.echo(f"Created data.js with {len(data)} items")
    typer.echo("Created schema.js")
    
    typer.echo(f"\n✅ Browser deployed to: {output_dir}")
    typer.echo(f"To view, open: {output_dir / 'index.html'}")


@app.command()
def init_schema(
    data_file: Annotated[Path, typer.Argument(help="Path to JSON data file")],
    output_file: Annotated[Path, typer.Option("--output", "-o", help="Output schema file")] = Path("schema.json"),
    title: Annotated[str, typer.Option("--title", "-t", help="Browser title")] = "Data Browser",
    description: Annotated[str, typer.Option("--description", "-d", help="Browser description")] = "Browse and filter data"
):
    """Generate a schema file from your data that you can customize."""
    
    # Validate input file
    if not data_file.exists():
        typer.echo(f"Error: Data file '{data_file}' not found", err=True)
        raise typer.Exit(1)
    
    # Load data
    try:
        data = load_json_data(data_file)
    except (json.JSONDecodeError, ValueError) as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)
    
    typer.echo(f"Loaded {len(data)} items from {data_file}")
    
    # Infer schema
    generator = BrowserGenerator(data)
    schema = generator.infer_schema(title, description)
    
    # Write schema
    save_schema(schema, output_file)
    
    typer.echo(f"\n✅ Schema written to: {output_file}")
    typer.echo("Edit this file to customize facets, search fields, and display options.")
    typer.echo(f"Then run: linkml-browser deploy {data_file} output/ --schema {output_file}")


def main():
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()