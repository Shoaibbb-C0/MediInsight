# Mumbai region OSM snapshot (mumbai-v1)

Data © OpenStreetMap contributors, made available under the Open Database License
1.0 (ODbL): https://opendatacommons.org/licenses/odbl/1-0/
Attribution and source rights: https://www.openstreetmap.org/copyright
Geofabrik regional extract: https://download.geofabrik.de/asia/india/western-zone.html

This directory redistributes an ODbL derivative database of OSM tags and derived
location centers. The database is licensed under ODbL 1.0, including its applicable
attribution, share-alike and offer-of-database obligations. Individual OSM contents
are subject to the Database Contents License where applicable. Application code
licensing is separate; this notice does not relicense unrelated application code.
The complete redistributed JSON database is provided here with the application.
Keep this notice, attribution and source metadata with redistributed copies.

- File: `mumbai-v1.json`; immutable version in Git.
- Retrieved: 18 October 2026 21:10:56 UTC (19 October 2026 in India).
- Source last modified: 17 October 2026 22:31:07 UTC.
- Source PBF SHA-256: `1539d9f9d33cfb2788797ef15e4d3978961b809bef97a5f753a72c362a5f297c`.
- Bounds [west, south, east, north]: [72.75, 18.85, 73.35, 19.50].
- 2,710 healthcare OSM elements; 2,663 have names, 47 unnamed elements are retained
  for audit but omitted from cards. These are elements, not proven unique venues:
  the same real facility may have multiple OSM elements.
- 1,390 tagged place records; 205 raw PIN entries derived from address tags.
  Runtime PIN lookup uses 164 entries with a regional 400/401/410/421 prefix and
  at least two source addresses. This is not official India Post validation.
- 237 elements have an explicit specialty tag; 117 have phone tags, 185 website
  tags, 2,366 any address tags (including partial addresses). These counts describe
  source tags, before URL/phone validation, filtering or unnamed omission.

No names, phone numbers, professional qualifications, ratings, available slots or
specialties have been invented. Partial/mistaken/stale OSM tags, duplicates and
missing facilities remain possible. No claim of complete facility coverage is made.
Nodes retain source coordinates; ways use bounding-box centers and relations use
available member centers. PIN centers average tagged source locations; locality
centers and East/West combined centers are approximate, not postal/ward polygons.
Regional aliases use actual source locality anchors and never invent providers.

For coverage samples, build instructions, operation and deployment see
`docs/HYBRID_DOCTOR_DEMO.md`. Snapshot search does not require osmium at runtime.
