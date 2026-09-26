---
id: FID-L01
title: "Lizenz-Whitelist greift — ausgeliefert wird nur Offenes, der Rest wird gezählt"
category: FID
severity: high
applies_when: 'always'
scope: server-specific (discover-swiss-mcp, P4)
narrows: FID-003 (Leermenge unterscheidbar) — ein zurückgehaltener Treffer ist eine Leermenge mit Grund
evidence_required: 3
---

# FID-L01 — Lizenz-Whitelist greift

## Description

Das Open-Produkt von discover.swiss liefert nicht nur offene Lizenzen
(Probe-Report 3, Fundstück 5): Guidle-Events kommen mit
`C-All-Rights-Reserved`, Hotelgruppen ohne Lizenz. Der Server darf nur
`{CC0, CC BY, CC BY-SA, CC BY-ND, ODbL}` ausliefern und muss alles andere
**zählen** (`excluded_by_license`), damit das Modell weiss, dass es etwas
nicht sieht.

## Verification

1. `code_review`: Whitelist-Definition und die Funktion, die die Lizenz
   eines Objekts bestimmt (Search-Treffer ohne root-`license`!).
2. `code_review`: Jeder Tool-Pfad, der Objekte ausliefert, läuft durch das Gate
   (`screen` / `is_servable`) — inklusive Listen-Fallback und `get_details`.
3. `automated`: Tests, die ein nicht offenes Objekt zurückhalten und zählen;
   Gegenprobe: ein offenes Objekt wird ausgeliefert.

## Pass Criteria

- Whitelist ist explizit, nicht als Blacklist formuliert.
- Alle ausliefernden Pfade laufen durchs Gate; keiner verliert den Zähler.
- Test mit All-Rights-Reserved-Objekt vorhanden und grün.
