## Finding: SEC-018 — Input-Validation an Tool-Boundaries (Pydantic strict / Zod)

| Feld | Wert |
|---|---|
| **Severity** | high |
| **Check-Status** | partial |
| **Status** | open |
| **Disposition** | offen — geplant, kein Release-Blocker |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `SEC-018` |
| **PDF-Reference** | Sec 3 / Sec 4 (Defense-in-Depth) |
| **Adoption** | enforced |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- strict=True is not set on any input model: page='5' is coerced to 5 (runtime)
- String fields have max_length but no whitelist pattern at the schema boundary; query and identifier accept control characters/NUL (runtime: 'test\x00\r\ninject' accepted by SearchInput); identifier is only regex-checked later in client.get_vertex
- List item strings (types, amenities, facets) have no per-item length/pattern: a 10'000-char types entry is accepted
- No parametrized edge-case tests for too-long strings, unknown fields or control characters (existing tests cover page_size>50, radius without near, missing scope)

### Expected Behavior

- [ ] **Alle** Tool-Argumente haben Schema-Validation (Pydantic / Zod / vergleichbar)
- [ ] Numerische Felder haben `ge`/`le`-Constraints (kein unbegrenzter Range)
- [ ] String-Felder haben `min_length`/`max_length` und idealerweise `pattern`
- [ ] Pattern sind Whitelist-basiert, nicht Blacklist
- [ ] Bei Pydantic: `strict=True` und `extra="forbid"` explizit gesetzt
- [ ] Validation-Errors landen als `isError` im Tool-Result, nicht als Server-Crash (siehe OBS-001)
- [ ] Tests decken Edge-Cases ab: zu lange Strings, Out-of-Range-Numbers, unbekannte Felder

### Evidence

- src/discover_swiss_mcp/tools.py:260-269 — _PagedInput: extra='forbid', page ge=1 le=1000, page_size ge=1 le=MAX_PAGE_SIZE(50), lang Literal
- src/discover_swiss_mcp/tools.py:278-330 — SearchInput: query max_length=200, types max_length=20 items, radius_km gt=0 le=200, locality max_length=100, match Literal; model_validator for radius/near
- src/discover_swiss_mcp/tools.py:333-344 — GetDetailsInput extra='forbid', identifier min_length=1 max_length=128; client.py:226,879-880 — whitelist regex ^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$ applied before the upstream call, client.py:889 quote(safe='')
- src/discover_swiss_mcp/tools.py:250-257 — GeoPoint lat/lon ranges, extra='forbid'; tools.py:2106-2143 ExploreAreaInput facets min_length=1 max_length=12
- runtime (audit, HTTP transport): tools/call get_details with {params:{}} → HTTP 200, result isError=true with validation message (no crash, no upstream call); tests/test_server.py:191-196 asserts invalid input is rejected before any upstream call
- runtime (audit, direct model): extra field → extra_forbidden; query 201 chars → string_too_long; page 1001 → less_than_equal

### Gemessen / Geschlossen / Offen

**Gemessen**
- src/discover_swiss_mcp/tools.py:260-269 — _PagedInput: extra='forbid', page ge=1 le=1000, page_size ge=1 le=MAX_PAGE_SIZE(50), lang Literal
- src/discover_swiss_mcp/tools.py:278-330 — SearchInput: query max_length=200, types max_length=20 items, radius_km gt=0 le=200, locality max_length=100, match Literal; model_validator for radius/near
- src/discover_swiss_mcp/tools.py:333-344 — GetDetailsInput extra='forbid', identifier min_length=1 max_length=128; client.py:226,879-880 — whitelist regex ^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$ applied before the upstream call, client.py:889 quote(safe='')
- src/discover_swiss_mcp/tools.py:250-257 — GeoPoint lat/lon ranges, extra='forbid'; tools.py:2106-2143 ExploreAreaInput facets min_length=1 max_length=12
- runtime (audit, HTTP transport): tools/call get_details with {params:{}} → HTTP 200, result isError=true with validation message (no crash, no upstream call); tests/test_server.py:191-196 asserts invalid input is rejected before any upstream call
- runtime (audit, direct model): extra field → extra_forbidden; query 201 chars → string_too_long; page 1001 → less_than_equal

**Geschlossen**
- All tools take Pydantic models with extra='forbid' and numeric bounds; validation errors surface as isError. Missing strict mode, schema-level patterns and per-item constraints, plus thin edge-case tests, leave 3 of 7 criteria unmet → partial.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: Tool-Argumente kommen vom LLM — einer probabilistischen Quelle, die halluzinieren, formattieren-falsch oder von Prompt-Injection beeinflusst sein kann. Ohne strikte Input-Validation am Tool-Boundary werden invalide oder bösartige Inputs in die Geschäftslogik weitergereicht und können dort:

### Remediation

Set model_config strict=True (keep str_strip_whitespace, extra='forbid') on all input models; add Annotated[str, StringConstraints(max_length=…, pattern=…)] for query/locality/region (reject C0 control chars), move the identifier regex into GetDetailsInput, and constrain list items (e.g. list[Annotated[str, StringConstraints(max_length=64, pattern=r'^[A-Za-z/]+$')]]); add a parametrized test for too-long, extra-field, control-char and coerced-type inputs.

**Disposition:** strict=True on input models and a control-character check on free-text inputs.

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `SEC-018` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)
