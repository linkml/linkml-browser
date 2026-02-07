# External Database Strategy for LinkML Browser

## Executive Summary

This document evaluates strategies for extending LinkML Browser from its current static/in-memory architecture to support external database backends (Solr, Elasticsearch, or a linkml-store API). The core tension is between the simplicity of the current self-contained HTML approach and the requirements of querying a remote data source from the browser. **The static browser model can work with an external database, but only behind a same-origin proxy**—direct browser-to-database calls are impractical for production. For maximum flexibility, a lightweight API layer (ideally reusing linkml-store's existing FastAPI endpoints) is the recommended path, with the frontend remaining vanilla JS unless requirements grow significantly.

---

## 1. Current Architecture

The current LinkML Browser is a **fully static, zero-server application**:

```
Python CLI (core.py)
  ├── Reads JSON data file
  ├── Infers or loads schema
  └── Generates output/
        ├── index.html  (self-contained ~3200-line HTML+JS+CSS)
        ├── data.js     (window.searchData = [...]; dispatches event)
        └── schema.js   (window.searchSchema = {...}; dispatches event)
```

All data lives in `data.js` as a JavaScript array assigned to `window.searchData`. The `OptimizedFacetedSearch` class builds inverted indexes in memory and performs all search, faceting, and filtering client-side. This works well for datasets up to ~10K items but fundamentally cannot scale to large external databases.

Key characteristics:
- **No network requests** after initial page load
- **No CORS concerns** (everything is same-origin file:// or static hosting)
- **No pagination against a backend** (all data loaded upfront, UI pagination only)
- **Facet counts computed client-side** via pre-built indexes

---

## 2. The CORS Problem

### Why This Matters

If the browser JavaScript tries to call a Solr or Elasticsearch endpoint directly:

```javascript
// This WILL fail from a static HTML page
fetch('http://solr-server:8983/solr/mycore/select?q=*:*')
```

The browser enforces the **Same-Origin Policy**. Unless the search engine is configured with permissive CORS headers, the request is blocked before it even reaches the server.

### Can You Just Enable CORS on Solr/ES?

Technically yes, but it's problematic:

| Concern | Impact |
|---------|--------|
| **Security exposure** | `Access-Control-Allow-Origin: *` exposes the full query API to any website. Anyone can craft arbitrary queries, extract all data, or abuse the cluster. |
| **No query sanitization** | The browser sends raw queries directly to the search engine. There's no middleware to validate, restrict, or transform queries. |
| **Credential leakage** | If the search engine requires auth, credentials must be embedded in client-side JavaScript—visible to anyone who opens DevTools. |
| **Configuration fragility** | Solr's Jetty CORS filter requires editing `web.xml`, which gets overwritten on upgrades. Elasticsearch CORS settings have had version-specific bugs. |
| **`file://` protocol** | If the browser is opened as a local file (the current use case), CORS is even more restrictive—most browsers block all cross-origin requests from `file://` origins. |

**Verdict: Direct browser-to-database with CORS is a development convenience, not a production strategy.**

### The Proxy Solution

The standard production pattern is a **same-origin reverse proxy**:

```
Browser (index.html)
   │
   │  fetch('/api/search?q=...')     ← Same origin, no CORS
   │
   ▼
Proxy / API Server (Nginx, FastAPI, Express)
   │
   │  HTTP request to search engine   ← Server-to-server, no CORS
   │
   ▼
Solr / Elasticsearch / linkml-store backend
```

This eliminates CORS entirely, provides a place to sanitize queries, add auth, cache results, and restrict which operations are exposed.

---

## 3. Proposed Architecture Options

### Option A: Static Browser + linkml-store API (Recommended)

Reuse the existing linkml-store FastAPI server as the backend. Modify the LinkML Browser frontend to fetch data from the API instead of `data.js`.

```
┌─────────────────────────────────┐
│         linkml-store            │
│         FastAPI Server          │
│                                 │
│  GET /db/col/objects?where=...  │ ← Query with filters
│  GET /db/col/search/{term}      │ ← Full-text search
│  GET /db/col/facets?where=...   │ ← Facet counts
│                                 │
│  Backends: DuckDB, Solr,        │
│    MongoDB, Ibis (PostgreSQL,   │
│    BigQuery, etc.)              │
├─────────────────────────────────┤
│    Static Files (same server)   │
│    index.html, schema.js        │
└─────────────────────────────────┘
         ▲
         │  Same-origin requests
         │
    Browser (vanilla JS)
```

**Why this is the best option:**

1. **linkml-store already has the exact API shape needed**:
   - `/databases/{db}/collections/{col}/objects?where=&limit=&offset=` — paginated query with filters
   - `/databases/{db}/collections/{col}/search/{term}` — full-text search
   - `/databases/{db}/collections/{col}/facets?where=` — facet counts
   - `/databases/{db}/collections/{col}/attributes/{attr}` — single-field distribution

2. **Backend-agnostic**: The same browser works whether linkml-store is backed by DuckDB (for moderate datasets), Solr (for large-scale search), MongoDB, or PostgreSQL via Ibis.

3. **No CORS**: Serve the static HTML from the same FastAPI server (or put both behind Nginx).

4. **The frontend stays vanilla JS**: No need to adopt React or a build system. The existing `OptimizedFacetedSearch` class can be refactored to call the API instead of querying in-memory data.

5. **Incremental migration**: The `data.js` approach can remain as a fallback for small datasets.

#### API Contract

Based on linkml-store's existing REST API, the browser would need these endpoints:

```
# Search with filters and pagination
GET /api/objects?q={searchTerm}&where={jsonFilters}&limit=50&offset=0

# Facet counts (with current filters applied)
GET /api/facets?where={jsonFilters}

# Schema/configuration
GET /api/schema
```

The `where` parameter uses linkml-store's filter syntax:

```json
{
  "category": "Electronics",
  "price": {"$gte": 50, "$lte": 200},
  "tags": {"$contains": "wireless"}
}
```

The facets endpoint returns:

```json
{
  "category": [["Electronics", 42], ["Clothing", 28], ["Books", 15]],
  "brand": [["Apple", 30], ["Samsung", 25], ["Sony", 18]]
}
```

#### Frontend Changes Required

The `OptimizedFacetedSearch` class currently does everything synchronously in memory. The refactor introduces async data fetching:

```javascript
class OptimizedFacetedSearch {
    constructor(schema, options = {}) {
        this.schema = schema;
        this.apiBase = options.apiBase || '/api';  // API endpoint
        this.mode = options.mode || 'auto';        // 'static' | 'api' | 'auto'

        // If data is provided inline (legacy), use static mode
        // If apiBase is configured, use api mode
        // 'auto' detects based on presence of window.searchData
    }

    async search() {
        if (this.mode === 'static') {
            return this._searchLocal();   // Current in-memory logic
        }

        // Build query from current filters
        const where = this._buildWhereClause();
        const params = new URLSearchParams({
            q: this.currentQuery,
            where: JSON.stringify(where),
            limit: this.itemsPerPage,
            offset: this.currentOffset
        });

        // Fetch results and facet counts in parallel
        const [results, facets] = await Promise.all([
            fetch(`${this.apiBase}/objects?${params}`).then(r => r.json()),
            fetch(`${this.apiBase}/facets?${params}`).then(r => r.json())
        ]);

        this.currentFilteredData = results.items;
        this.totalCount = results.meta.item_count;
        this.currentFacetCounts = facets;

        this.renderResults();
        this.renderFacets(this.currentFacetCounts);
    }
}
```

Key behavioral changes in API mode:
- **Search is async** (returns a Promise, needs debouncing)
- **Pagination is real** (offset/limit against the server, not slicing a local array)
- **Facet counts come from the server** (no client-side index building)
- **No upfront data load** (the page renders immediately, first search populates results)

#### Dual-Mode Support

The browser can support both modes transparently:

```javascript
// In initialization:
if (window.searchData) {
    // Static mode: data.js was loaded, use in-memory search
    this.mode = 'static';
    this.originalData = window.searchData;
    this.buildSearchIndex();
    this.buildFacetIndex();
} else if (this.apiBase) {
    // API mode: fetch from server
    this.mode = 'api';
}
```

This means the same `index.html` template works for both static deployment (small datasets) and server-backed deployment (large datasets).

---

### Option B: Nginx Reverse Proxy to Raw Solr/ES

Skip linkml-store and proxy directly to Solr or Elasticsearch.

```
Browser → Nginx → Solr/ES
```

The frontend would need to construct Solr/ES queries directly in JavaScript:

```javascript
// Solr query construction in the browser
const solrQuery = new URLSearchParams({
    q: searchTerm || '*:*',
    defType: 'edismax',
    qf: 'title^3 description',
    fq: filters.map(f => `${f.field}:${f.value}`).join('&fq='),
    'facet': 'true',
    'facet.field': schema.facets.map(f => f.field),
    rows: 50,
    start: offset,
    wt: 'json'
});

const results = await fetch(`/solr/mycore/select?${solrQuery}`);
```

**Pros:**
- No application server needed (just Nginx + Solr/ES)
- Full Solr/ES query power available

**Cons:**
- **Backend lock-in**: The browser must know it's talking to Solr vs ES (different APIs)
- **Query injection risk**: Client-side query construction means users can manipulate parameters via DevTools
- **No abstraction**: Changing the backend requires rewriting the frontend
- **Nginx still required**: You need a proxy regardless

**Verdict: This works but couples the frontend to a specific search engine. Option A is strictly better if linkml-store is available.**

---

### Option C: React/SPA with Build System

Replace the vanilla JS browser with a React (or Vue/Svelte) application with a proper build pipeline.

```
React App (Vite/Next.js)
  ├── Components: SearchBar, FacetPanel, ResultList, Pagination
  ├── State management: React Query / Zustand
  ├── API client layer
  └── Build output: static files served from any CDN/server
```

**When this makes sense:**
- You need complex interactive features (drag-and-drop, inline editing, real-time collaboration)
- Multiple developers will work on the frontend
- You want a component library ecosystem (Material UI, Ant Design, etc.)
- The curation/annotation system grows in complexity
- You need SSR for SEO

**When this is overkill:**
- The primary use case remains "generate a browser for a dataset"
- The current vanilla JS works fine and has zero build dependencies
- The frontend is maintained by 1-2 people
- The main value proposition is simplicity (single HTML file)

**My assessment: Option C is not needed yet.** The current architecture's main strength is that `linkml-browser deploy` produces a self-contained output with no build step, no node_modules, no bundler config. Moving to React would fundamentally change the tool's character from "generate a browser" to "deploy a web application." That said, if the curation features continue to grow in complexity, or if you want to support features like real-time collaborative annotation, React may eventually be warranted.

**Hybrid approach**: If React is eventually adopted, it can still produce a static build that works with either `data.js` (static mode) or an API (dynamic mode). Frameworks like Vite produce optimized static bundles. The generated output would be `index.html` + `assets/` instead of a single HTML file, but the deployment model could remain similar.

---

## 4. Recommended Implementation Plan

### Phase 1: API Adapter Layer in the Frontend

Introduce an abstraction layer that separates data access from rendering:

```javascript
// DataSource interface (implicit, via duck typing)
class StaticDataSource {
    constructor(data) { this.data = data; /* build indexes */ }
    async search(query, filters, offset, limit) { /* local search */ }
    async getFacetCounts(filters) { /* local facet computation */ }
}

class APIDataSource {
    constructor(apiBase) { this.apiBase = apiBase; }
    async search(query, filters, offset, limit) {
        const resp = await fetch(`${this.apiBase}/objects?...`);
        return resp.json();
    }
    async getFacetCounts(filters) {
        const resp = await fetch(`${this.apiBase}/facets?...`);
        return resp.json();
    }
}
```

This is a minimal refactor—extract the data access methods from `OptimizedFacetedSearch` into a separate object, then swap implementations based on configuration.

### Phase 2: linkml-store Integration

Ensure linkml-store's FastAPI endpoints support the exact query patterns the browser needs:

1. **Combined search + filter**: The `/objects` endpoint needs to support both `q` (text search) and `where` (structured filters) simultaneously.
2. **Facet isolation**: When computing facet counts for field X, the filters on field X should be excluded (so the user sees all possible values, not just the currently selected one). This is the `{!ex=tag}` pattern in Solr / `post_filter` in ES. linkml-store's DuckDB backend already implements this.
3. **Total count**: The response must include the total number of matching documents (not just the current page), for pagination UI.
4. **Multivalued field faceting**: Array fields need `UNNEST` (DuckDB) / `$unwind` (MongoDB) / native multivalued field support (Solr). linkml-store handles this.

### Phase 3: Deployment Tooling

Update the CLI to support both modes:

```bash
# Static mode (current behavior, unchanged)
linkml-browser deploy data.json output/

# API mode: generate browser configured for a linkml-store endpoint
linkml-browser deploy --api-url http://localhost:8395/databases/mydb/collections/mycol output/

# Full stack: start linkml-store server + serve browser
linkml-browser serve data.json --port 8080
```

The `serve` command would:
1. Start a linkml-store instance with the data loaded
2. Serve `index.html` and `schema.js` from the same server
3. Configure the browser to use the API endpoints

### Phase 4 (If Needed): React Migration

If the frontend complexity warrants it, migrate to React with:
- Vite for building
- React Query for data fetching + caching
- A component library for the facet panel, result cards, etc.
- Static build output that can be served from the same linkml-store server

---

## 5. Query Mapping: Browser Filters → API → Backend

Here's how the current in-memory filter logic maps to the API layer and ultimately to backend-specific queries:

### String Facet (OR logic)

```
User selects: category = ["Electronics", "Books"]

Browser → API:
  GET /api/objects?where={"category": {"$in": ["Electronics", "Books"]}}

API → DuckDB:
  SELECT * FROM items WHERE category IN ('Electronics', 'Books')

API → Solr:
  fq=category:(Electronics OR Books)

API → Elasticsearch:
  {"terms": {"category.keyword": ["Electronics", "Books"]}}
```

### Array Facet (AND logic)

```
User selects: tags = ["wireless", "bluetooth"]

Browser → API:
  GET /api/objects?where={"tags": {"$all": ["wireless", "bluetooth"]}}

API → DuckDB:
  SELECT * FROM items
  WHERE list_contains(tags, 'wireless') AND list_contains(tags, 'bluetooth')

API → Solr:
  fq=tags:wireless AND tags:bluetooth

API → Elasticsearch:
  {"bool": {"filter": [
    {"term": {"tags": "wireless"}},
    {"term": {"tags": "bluetooth"}}
  ]}}
```

### Integer Facet (Range)

```
User selects: price range [50, 200]

Browser → API:
  GET /api/objects?where={"price": {"$gte": 50, "$lte": 200}}

API → DuckDB:
  SELECT * FROM items WHERE price >= 50 AND price <= 200

API → Solr:
  fq=price:[50 TO 200]

API → Elasticsearch:
  {"range": {"price": {"gte": 50, "lte": 200}}}
```

### Full-Text Search + Filters Combined

```
User types: "wireless headphones", with category=Electronics selected

Browser → API:
  GET /api/objects?q=wireless+headphones&where={"category":"Electronics"}

API → Solr:
  q=wireless headphones&defType=edismax&qf=title^3 description
  &fq=category:Electronics

API → Elasticsearch:
  {"bool": {
    "must": [{"multi_match": {"query": "wireless headphones", "fields": ["title^3","description"]}}],
    "filter": [{"term": {"category.keyword": "Electronics"}}]
  }}
```

---

## 6. Decision Matrix

| Criterion | Static (Current) | Static + API (Option A) | Raw Solr/ES Proxy (B) | React SPA (C) |
|-----------|:-:|:-:|:-:|:-:|
| **CORS-free** | ✅ No network | ✅ Same-origin proxy | ✅ Same-origin proxy | ✅ Same-origin proxy |
| **No build step** | ✅ | ✅ | ✅ | ❌ Node/Vite required |
| **Self-contained output** | ✅ 3 files | ⚠️ Needs running server | ⚠️ Needs running server | ⚠️ Needs running server |
| **Large dataset support** | ❌ <10K items | ✅ Server-side query | ✅ Server-side query | ✅ Server-side query |
| **Backend-agnostic** | N/A | ✅ linkml-store abstracts | ❌ Solr or ES specific | ✅ Via API layer |
| **Query safety** | N/A | ✅ Server validates | ⚠️ Client constructs | ✅ Server validates |
| **Development complexity** | Low | Low-Medium | Medium | High |
| **Offline capability** | ✅ | ❌ | ❌ | ❌ |
| **Reuses existing code** | ✅ | ✅ Most of index.html | ⚠️ Major JS rewrite | ❌ Full rewrite |

---

## 7. Recommendation

**Go with Option A (Static Browser + linkml-store API)** for these reasons:

1. **linkml-store already exists and has the right API shape.** The FastAPI endpoints for objects, search, and facets map directly to what the browser needs. No new backend code required.

2. **The frontend refactor is modest.** Extract data access into a `DataSource` abstraction, make `search()` async, add a fetch-based implementation. The rendering code, CSS, facet UI, and curation system remain unchanged.

3. **Dual-mode preserves the tool's identity.** The `linkml-browser deploy` command continues to work for small datasets with zero infrastructure. The `--api-url` flag or a new `serve` command enables the external database path.

4. **CORS is a non-issue** because the static files are served from the same origin as the API (either the same FastAPI server, or both behind Nginx).

5. **No React needed yet.** The current vanilla JS is well-structured (~3200 lines, single class with clear methods). Moving to React would add significant build complexity without proportional benefit for the current feature set. Revisit this if the curation system grows into a full annotation platform.

6. **Backend flexibility for free.** linkml-store supports DuckDB (easy local dev), Solr (production search), MongoDB (document store), and PostgreSQL via Ibis. The browser doesn't need to know or care which one is behind the API.

### When to Reconsider React

Adopt a React/SPA architecture if any of these become true:
- The curation system needs real-time collaboration (WebSocket state sync)
- You need server-side rendering for SEO
- The UI grows beyond what's manageable in a single HTML file (~5000+ lines)
- Multiple frontend developers need to work concurrently with component isolation
- You want to integrate a design system (Material UI, Ant Design, Radix)

---

## 8. Appendix: linkml-store API Reference (Relevant Endpoints)

These are the existing linkml-store FastAPI endpoints that map to browser needs:

```
GET  /databases/{db}/collections/{col}/objects
     ?where={json_filter}&limit=50&offset=0
     → Returns: {meta: {item_count, page, page_size}, items: [...]}

GET  /databases/{db}/collections/{col}/search/{term}
     ?limit=50&offset=0
     → Returns: {items: [...], ranked_rows: [(score, item), ...]}

GET  /databases/{db}/collections/{col}/facets
     ?where={json_filter}
     → Returns: {field_name: [[value, count], ...], ...}

GET  /databases/{db}/collections/{col}/attributes/{attr}
     → Returns: value distribution for a single field

GET  /databases/{db}/collections/{col}/attributes/{attr}/equals/{val}
     ?limit=50&offset=0
     → Returns: items where attr == val
```

The `where` parameter supports:
```json
{
  "field": "exact_value",
  "field": {"$gt": 10, "$lt": 100},
  "field": {"$in": ["val1", "val2"]},
  "field": {"$contains": "substring"}
}
```
