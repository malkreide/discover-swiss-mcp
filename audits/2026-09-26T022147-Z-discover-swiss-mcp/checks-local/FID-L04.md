---
id: FID-L04
title: "HTML gestrippt, Entities aufgelöst"
category: FID
severity: medium
applies_when: 'always'
scope: server-specific (discover-swiss-mcp, P4)
narrows: keiner der Katalog-Checks fragt nach der Kodierung ausgelieferter Texte — eigene Prüfdimension für diesen Server
evidence_required: 2
---

# FID-L04 — HTML gestrippt, Entities aufgelöst

## Description

Beschreibungen kommen als HTML mit Entities (`&uuml;`, `<p>`, Preise als
`<table>`, Fundstück 11). An das Modell geht Klartext: Tags entfernt,
Block-Tags als Zeilenumbruch, Entities aufgelöst — sonst liest es `&uuml;`
vor oder «repariert» die Kodierung stillschweigend falsch.

## Verification

1. `code_review`: `html_to_text` und jede Stelle, an der ein Textfeld
   (description, fees, teaser, openingHours) an eine Response geht.
2. `automated`: Test gegen die aufgezeichnete Landesmuseum-Beschreibung;
   Live-Canary ohne Entity.

## Pass Criteria

- Kein ausgeliefertes Freitextfeld umgeht `html_to_text`.
- Test mit aufgezeichnetem HTML vorhanden und grün.
