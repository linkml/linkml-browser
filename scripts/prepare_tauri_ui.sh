#!/usr/bin/env bash
set -euo pipefail

root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ui_dir="${root_dir}/ui"

mkdir -p "${ui_dir}"
cp "${root_dir}/src/linkml_browser/index.html" "${ui_dir}/index.html"

cat > "${ui_dir}/data.js" <<'EOF'
window.searchData = [
  {
    "id": "welcome-1",
    "message": "No project loaded. Use File > Open Project… or Open Project from GitHub…",
    "status": "ready"
  }
];
window.dispatchEvent(new Event('searchDataReady'));
EOF

cat > "${ui_dir}/schema.js" <<'EOF'
window.searchSchema = {
  "title": "MANTRA",
  "description": "Open a project to begin reviewing evaluations.",
  "searchPlaceholder": "Search...",
  "recordIdField": "id",
  "searchableFields": ["message", "status"],
  "facets": [
    { "field": "status", "label": "Status", "type": "string", "sortBy": "alphabetical" }
  ],
  "displayFields": [
    { "field": "message", "label": "Welcome", "type": "string", "primary": true },
    { "field": "status", "label": "Status", "type": "string" }
  ]
};
window.dispatchEvent(new Event('searchSchemaReady'));
EOF
