## Add your own just recipes here. This is imported by the main justfile.

# ============== Gallery generation recipes ==============

gallery_dir := "docs/gallery"

# Regenerate all galleries
[group('gallery')]
gallery: gallery-books gallery-cell-ontology
    @echo "All galleries regenerated"

# Regenerate the books gallery from test data
[group('gallery')]
gallery-books:
    uv run linkml-browser deploy tests/test_data.json {{gallery_dir}}/books/ \
        --title "Books Browser" \
        --description "Browse and filter classic literature" \
        --force

# Regenerate cell-ontology gallery from semantic-sql
[group('gallery')]
gallery-cell-ontology:
    #!/usr/bin/env bash
    set -euo pipefail
    tmpfile=$(mktemp).json
    echo "Fetching Cell Ontology from semantic-sql..."
    uv run python scripts/extract_cl.py > "$tmpfile"
    echo "Deploying browser..."
    uv run linkml-browser deploy "$tmpfile" {{gallery_dir}}/cell-ontology/ \
        --title "Cell Ontology Browser" \
        --description "Browse cell types from the Cell Ontology (CL)" \
        --force
    rm "$tmpfile"
    echo "Cell Ontology gallery regenerated"

# Verify galleries exist and have expected files
[group('gallery')]
gallery-check:
    #!/usr/bin/env bash
    set -euo pipefail
    check_gallery() {
        local name=$1
        local dir="{{gallery_dir}}/$name"
        if [[ ! -d "$dir" ]]; then
            echo "FAIL $name: directory missing"
            return 1
        fi
        for file in index.html data.js schema.js; do
            if [[ ! -f "$dir/$file" ]]; then
                echo "FAIL $name: $file missing"
                return 1
            fi
        done
        echo "OK $name"
    }
    check_gallery "books"
    check_gallery "cell-ontology"

# Serve the docs directory locally for testing galleries
[group('gallery')]
gallery-serve:
    uv run python -m http.server 8000 --directory docs

# ============== Tauri demo recipes ==============

# Copy a gallery into ui/ for Tauri testing: just tauri-demo dismech
[group('tauri')]
tauri-demo name:
    #!/usr/bin/env bash
    set -euo pipefail
    dir="{{gallery_dir}}/{{name}}"
    if [[ ! -d "$dir" ]]; then
        echo "Unknown gallery: {{name}}"
        echo "Available:"
        ls -1 "{{gallery_dir}}"
        exit 1
    fi
    rm -rf ui
    cp -R "$dir" ui
    echo "Loaded {{name}} into ui/"

# Faster alternative using a symlink: just tauri-demo-link dismech
[group('tauri')]
tauri-demo-link name:
    #!/usr/bin/env bash
    set -euo pipefail
    dir="{{gallery_dir}}/{{name}}"
    if [[ ! -d "$dir" ]]; then
        echo "Unknown gallery: {{name}}"
        echo "Available:"
        ls -1 "{{gallery_dir}}"
        exit 1
    fi
    ln -sfn "$dir" ui
    echo "Linked {{name}} to ui/"
