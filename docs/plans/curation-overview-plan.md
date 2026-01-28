# Curation Forms: Overview Plan

## Goals
- Add Argilla-like curation controls to each card (thumbs/rating/notes/etc.).
- Keep existing read-only, static deployment fully supported by default.
- Make curation schema-driven and optional.
- Support local-only storage first; allow optional API sync later.
- Preserve current faceted search and card rendering behavior.

## Non-Goals (initial phases)
- Real-time multi-user collaboration.
- Server-side search or server-managed datasets.
- Complex workflow engines (e.g., arbitration, consensus).

## High-Level Architecture
- **Schema extensions** for curation fields + inline decorators.
- **UI renderer** for curation panel + inline decorators.
- **Annotation store abstraction** (local storage now; API later).
- **Import/export** for annotations (JSON + CSV).
- **Feature gating** to keep read-only static builds unchanged unless curation is enabled.

## Phases

### Phase 0: Schema + UX Design (spec only)
- Finalize schema extension structure and field types.
- Decide on default UI placement (inline decorators vs curation panel).
- Decide on record ID strategy and required schema fields.

### Phase 1: Local-Only MVP
- Implement schema parsing of curation fields and decorators.
- Render curation UI per card.
- Implement local annotation store (localStorage for small datasets, IndexedDB for larger).
- Add import/export actions.
- Add minimal UI states (saved, dirty, invalid).

### Phase 2: Polishing
- Validation errors per field.
- Keyboard shortcuts for common actions (thumbs up/down, save).
- Batch export (all or filtered results).
- Basic analytics (count of annotated vs unannotated).

### Phase 3: Optional Sync / API
- Add API-backed store (token auth + simple CRUD endpoints).
- Optional sync button and conflict resolution.
- Store metadata for curator identity.

### Phase 4: Desktop Wrapper (Optional)
- Tauri wrapper points at the same generated UI output.
- Local file or SQLite-backed storage via Tauri.
- Native file dialogs for import/export.

## Deliverables
- Updated schema docs in `docs/`.
- UI changes in `src/linkml_browser/index.html`.
- Annotation store module added to frontend (embedded in HTML).
- Import/export helpers.
- Optional Tauri wrapper scaffold in `apps/tauri/` (if pursued).

## Risks / Open Questions
- Stable record IDs required for annotation persistence.
- Large datasets may need IndexedDB to avoid localStorage limits.
- UI complexity: ensure curation doesn’t degrade existing search performance.

## Testing Strategy
- Unit-ish JS tests are not present; plan manual test checklist:
  - Load dataset, set annotations, reload page, verify persistence.
  - Export JSON/CSV, import into fresh browser profile, verify merge behavior.
  - Validate field types and range limits.
  - Verify faceted browsing remains unchanged when curation is disabled.

