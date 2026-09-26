## Finding: ARCH-008 — Drei Primitive nutzen: Tools, Resources und Prompts

| Feld | Wert |
|---|---|
| **Severity** | medium |
| **Check-Status** | fail |
| **Status** | open |
| **Disposition** | offen — geplant, kein Release-Blocker |
| **Server** | `discover-swiss-mcp` |
| **Check-Reference** | `ARCH-008` |
| **PDF-Reference** | Anhang A2 |
| **Adoption** | enforced |
| **Audit-Datum** | 2026-09-26 |
| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |
| **Ziel-Revision** | `bd0e371` |

### Observed Behavior

- Only one primitive (tools) and no README rationale for tools-only
- No documented review of read-only tools (get_details by identifier, source_status) as resource candidates
- Capabilities advertise prompts/resources (incl. resources.subscribe) that the server does not provide (SDK default)

### Expected Behavior

- [ ] Server nutzt mindestens zwei der drei Primitive (Tools + Resources oder Tools + Prompts), oder
- [ ] README dokumentiert begründet, warum nur Tools verwendet werden
- [ ] Bei Resources: URI-Schema ist konsistent und dokumentiert
- [ ] Bei Prompts: Template-Liste ist kuratiert, nicht beliebig
- [ ] Tools, die rein read-only sind (idempotent, side-effect-frei, deterministisch), werden auf Resources-Migrations-Potential geprüft

### Evidence

- grep '@mcp.resource|@mcp.prompt|.resource(|.prompt(' src/ → 0 hits (tools only)
- grep -iE 'resources|prompts|primitive' README.md README.de.md → 0 hits (negative control: same pattern hits ARCH-008.md:3)
- runtime: resources/list, prompts/list, resources/templates/list return empty lists, while server/discover advertises capabilities prompts{listChanged:true} and resources{listChanged:true, subscribe:true}

### Gemessen / Geschlossen / Offen

**Gemessen**
- grep '@mcp.resource|@mcp.prompt|.resource(|.prompt(' src/ → 0 hits (tools only)
- grep -iE 'resources|prompts|primitive' README.md README.de.md → 0 hits (negative control: same pattern hits ARCH-008.md:3)
- runtime: resources/list, prompts/list, resources/templates/list return empty lists, while server/discover advertises capabilities prompts{listChanged:true} and resources{listChanged:true, subscribe:true}

**Geschlossen**
- Neither alternative of criterion 1/2 is met: no second primitive and no documented justification.

**Offen**
- keine offenen Punkte

### Risk Description

Katalog-Begründung: MCP definiert drei orthogonale Primitive, von denen die meisten Server nur eines nutzen:

### Remediation

Add a 'MCP primitives' paragraph to README.md and README.de.md explaining tools-only (e.g. identifiers only come from searches; read-only tools are needed for provenance envelopes), or expose get_details as a resource template (discover-swiss://object/{identifier}); consider not advertising unused capabilities.

**Disposition:** Tools-only is deliberate (a tourist question is an action, not a resource); the README will say so in one sentence.

### Effort Estimate

S

### Dependencies / Blockers

keine bekannt

### Verification After Fix

- Re-Audit von `ARCH-008` gegen den Fix-Commit
- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)
