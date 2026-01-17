#!/usr/bin/env python3
"""Extract Cell Ontology terms for linkml-browser gallery."""

import json
import subprocess
import sys


def extract_cl_terms() -> list[dict]:
    """Extract CL terms using oaklib and flatten for browser."""
    # Run oaklib to get CL terms
    result = subprocess.run(
        ["uv", "run", "runoak", "-i", "sqlite:obo:cl", "info", "i^CL:", "-O", "json", "-D", "all"],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"Error running oaklib: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    # Parse the JSON output
    raw_terms = json.loads(result.stdout)

    terms = []
    for node in raw_terms:
        # Only include CLASS type entities
        if node.get("type") != "CLASS":
            continue

        term = {
            "id": node.get("id", ""),
            "label": node.get("lbl", ""),
        }

        meta = node.get("meta", {})

        # Extract definition
        definition = meta.get("definition", {})
        if definition:
            term["definition"] = definition.get("val", "")

        # Extract subsets/slims
        subsets = meta.get("subsets", [])
        if subsets:
            # Clean up subset names
            term["subsets"] = [s.split("#")[-1] if "#" in s else s.split("/")[-1] for s in subsets]

        # Extract synonyms
        synonyms = meta.get("synonyms", [])
        if synonyms:
            term["synonyms"] = [s.get("val", "") for s in synonyms if s.get("val")]

        # Check if obsolete
        term["obsolete"] = "obsolete" in term["label"].lower()

        # Extract xrefs
        xrefs = meta.get("xrefs", [])
        if xrefs:
            term["xrefs"] = [x.get("val", "") for x in xrefs if x.get("val")]

        terms.append(term)

    return terms


def main():
    """Main entry point."""
    terms = extract_cl_terms()
    print(json.dumps(terms, indent=2))


if __name__ == "__main__":
    main()
