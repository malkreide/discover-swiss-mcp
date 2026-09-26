"""Render findings/<ID>-<slug>.md for this run from raw results and dispositions.

Inputs, all in this run directory:
  verification-results.json        catalogue checks (step 4)
  verification-results-local.json  server-specific checks FID-L01..04
  dispositions.json                one disposition per finding
  checks-local/                    definitions of the server-specific checks
and the catalogue directory given as the first argument.

Written as a script, not by hand, because 58 documents from the same data drift
the moment one is edited separately (mcp-audit, step 5.0).
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

RUN = Path(__file__).resolve().parent
CATALOG = Path(sys.argv[1])

STATUS_BY_KIND = {
    "fix-before-release": "open",
    "fix-later": "open",
    "accepted": "accepted-risk",
    "fixed": "closed",
}
KIND_LABEL = {
    "fix-before-release": "offen — vor dem Release zu beheben",
    "fix-later": "offen — geplant, kein Release-Blocker",
    "accepted": "akzeptiert (accepted-risk)",
    "fixed": "nach dem Audit behoben",
}


def frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    fields: dict[str, str] = {}
    if match:
        for line in match.group(1).splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                fields[key.strip()] = value.strip().strip("'\"")
    return fields


def section(path: Path, heading: str) -> str:
    text = path.read_text(encoding="utf-8")
    match = re.search(rf"^## {re.escape(heading)}\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    return match.group(1).strip() if match else ""


def first_paragraph(text: str) -> str:
    for block in text.split("\n\n"):
        block = block.strip()
        if block and not block.startswith(("`", "|", "```", "#")):
            return block
    return ""


def slug(title: str) -> str:
    ascii_title = (
        title.lower().replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    )
    return re.sub(r"[^a-z0-9]+", "-", ascii_title).strip("-")[:60] or "finding"


def render(cid: str, result: dict, check_path: Path, disposition: list[str], date: str) -> str:
    meta = frontmatter(check_path)
    title = meta.get("title", cid)
    kind, reason = disposition
    evidence = result.get("evidence") or []
    gaps = result.get("gaps") or []
    criteria = section(check_path, "Pass Criteria") or "_(siehe Check-Definition)_"
    description = first_paragraph(section(check_path, "Description"))
    notes = (result.get("evaluator_notes") or "").strip()
    remediation = (result.get("remediation") or "").strip()
    effort = (result.get("effort") or "").strip() or "—"
    narrows = meta.get("narrows")

    lines = [
        f"## Finding: {cid} — {title}",
        "",
        "| Feld | Wert |",
        "|---|---|",
        f"| **Severity** | {result['severity']} |",
        f"| **Check-Status** | {result['status']} |",
        f"| **Status** | {STATUS_BY_KIND[kind]} |",
        f"| **Disposition** | {KIND_LABEL[kind]} |",
        "| **Server** | `discover-swiss-mcp` |",
        f"| **Check-Reference** | `{cid}` |",
        f"| **PDF-Reference** | {meta.get('pdf_ref', '—')} |",
        f"| **Adoption** | {meta.get('adoption', 'enforced')} |",
        f"| **Audit-Datum** | {date} |",
        "| **Auditor** | Claude (mcp-audit 2.3.0, Prüf-Agenten je Kategorie; Stichproben vom Report-Autor nachgemessen) |",
        "| **Ziel-Revision** | `bd0e371` |",
        "",
    ]
    if narrows:
        lines += [f"> Serverspezifischer Check. Verengt: {narrows}", ""]
    lines += ["### Observed Behavior", ""]
    lines += [f"- {gap}" for gap in gaps] or ["- _(keine Lücke einzeln benannt; siehe Evidence)_"]
    lines += ["", "### Expected Behavior", "", criteria, "", "### Evidence", ""]
    lines += [f"- {item}" for item in evidence] or ["- _(keine)_"]
    lines += [
        "",
        "### Gemessen / Geschlossen / Offen",
        "",
        "**Gemessen**",
    ]
    lines += [f"- {item}" for item in evidence] or ["- _(nichts gemessen)_"]
    lines += [
        "",
        "**Geschlossen**",
        f"- {notes}" if notes else "- _(keine Schlussfolgerung notiert)_",
    ]
    lines += ["", "**Offen**"]
    if result["status"] == "not_verified":
        lines.append("- Nicht verifizierbar zum Audit-Zeitpunkt; siehe Disposition.")
    else:
        lines.append("- keine offenen Punkte")
    lines += [
        "",
        "### Risk Description",
        "",
        f"Katalog-Begründung: {description}" if description else "_(siehe Check-Definition)_",
        "",
        "### Remediation",
        "",
        remediation or "_(siehe Disposition)_",
        "",
        f"**Disposition:** {reason}",
        "",
        "### Effort Estimate",
        "",
        effort,
        "",
        "### Dependencies / Blockers",
        "",
        dependency(cid),
        "",
        "### Verification After Fix",
        "",
        f"- Re-Audit von `{cid}` gegen den Fix-Commit",
        "- Test, der die beobachtete Lücke abprüft, mit Gegenprobe (Mutation schlägt an)",
        "",
    ]
    return "\n".join(lines)


DEPENDENCIES = {
    "SEC-002": "Hängt an SEC-016 (Remote-Bind nur mit ausdrücklichem Opt-in).",
    "SEC-003": "Hängt an SEC-016 (Remote-Bind nur mit ausdrücklichem Opt-in).",
    "SEC-024": "Zusammen mit SEC-016 umsetzen (derselbe Startpfad).",
    "ARCH-012": "Zusammen mit ARCH-015 und ARCH-016 (Protokoll-Identität).",
    "FID-006": "Neuer degraded-Wert braucht Envelope-Doku (models.py) und Tool-Hash-Update.",
    "FID-005": "Ändert Tool-Descriptions → Tool-Hash-Snapshot im selben PR.",
    "DRIFT-004": "Live-Lauf braucht einen Key; läuft lokal wie OPS-001.",
}


def dependency(cid: str) -> str:
    return DEPENDENCIES.get(cid, "keine bekannt")


def main() -> int:
    meta = json.loads((RUN / "audit-meta.json").read_text(encoding="utf-8"))["audit_meta"]
    date = meta["started_at"][:10]
    dispositions = json.loads((RUN / "dispositions.json").read_text(encoding="utf-8"))
    summary = json.loads((RUN / "summary.json").read_text(encoding="utf-8"))
    catalogue = json.loads((RUN / "verification-results.json").read_text(encoding="utf-8"))
    local = json.loads((RUN / "verification-results-local.json").read_text(encoding="utf-8"))

    out = RUN / "findings"
    out.mkdir(exist_ok=True)
    out_local = RUN / "findings-local"
    out_local.mkdir(exist_ok=True)

    written = 0
    for cid in summary["findings"]["expected_ids"]:
        path = CATALOG / f"{cid}.md"
        text = render(cid, catalogue["results"][cid], path, dispositions[cid], date)
        (out / f"{cid}-{slug(frontmatter(path).get('title', cid))}.md").write_text(
            text, encoding="utf-8"
        )
        written += 1
    for cid, result in local["results"].items():
        if result["status"] not in ("fail", "partial"):
            continue
        path = RUN / "checks-local" / f"{cid}.md"
        text = render(cid, result, path, dispositions[cid], date)
        (out_local / f"{cid}-{slug(frontmatter(path).get('title', cid))}.md").write_text(
            text, encoding="utf-8"
        )
        written += 1
    print(f"finding documents written: {written}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
