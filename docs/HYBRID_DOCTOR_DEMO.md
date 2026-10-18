# Hybrid doctor discovery — external demonstration runbook

## What is reliable without live OSM search

The committed `backend/app/data/osm/mumbai-v1.json` is genuine OSM data derived
locally from Geofabrik's Western India PBF. Mumbai-region facility search, manual
indexed locality/PIN resolution, GPS distance/radius filtering and specialty
matching never require Overpass or Nominatim. The existing MapLibre/OpenFreeMap
map remains interactive; its online style/tiles need internet. If WebGL/tiles fail,
use the synchronized facility cards and OSM source/directions links. Directions,
websites and phone applications are external services, not offline guarantees.

`OSM_DISCOVERY_ENABLED` controls only the **live nationwide adapter**. Setting it
false does not disable the snapshot. Outside coverage, enabled live requests keep
the previous timeout, cache, identification and aggregate quota protections. A
network failure returns an explicit error, never demo or out-of-area substitution.

## Geographic coverage and actual data limits

Rectangle: west 72.75, south 18.85, east 73.35, north 19.50. This covers the full
Greater Mumbai geographic extent from Colaba through Dahisar and Mulund, plus
Navi Mumbai, Thane, Panvel and Kalyan-Dombivli, and some surrounding places. It is
an extraction rectangle, **not an official municipal boundary**. It does not mean
all real facilities in those places have been mapped. Snapshot-boundary crossings
are disclosed; no automatic live expansion occurs. Source data last modified
17 October 2026; retrieved 18 October 21:10 UTC / 19 October in India.

2,710 OSM healthcare elements were retained, 2,663 named. 47 unnamed elements are
not displayed. Multiple elements may represent one physical venue. 1,390 place
records and 205 raw PIN entries are retained. 164 PIN entries are used in the
runtime index after regional-prefix and minimum-two-source-address checks.
Distant PIN mistakes (for example, Pune tags on a Mumbai object) are not silently
turned into Mumbai PIN lookups. Unsupported regional PINs/localities return a
helpful request for another indexed locality/PIN or GPS, rather than invented
coordinates. Some unknown inputs need live nationwide geocoding.

Only 237 elements have specialty tags; 117 have phone tags and 185 website tags.
Only source-supported, usable contact links are displayed. Addresses can be
partial. Specialty matching is exact/conservative: absence of tags does not prove
absence of a clinician. The general-facility action makes no specialist claim.
There are no ratings, verified physician credentials, fees, hours or appointments.

Example **10 km general-facility searches** against this version (overlapping
search circles; counts are source elements after runtime filtering):

| Search anchor | Matching elements |
|---|---:|
| Colaba / South Mumbai anchor | 175 |
| Dadar / Central Mumbai anchor | 723 |
| Andheri / Western Suburbs anchor | 954 |
| Borivali | 532 |
| Dahisar | 464 |
| Mulund | 496 |
| Ghatkopar / Eastern Suburbs anchor | 784 |
| Chembur | 777 |
| Navi Mumbai | 190 |
| Thane | 411 |
| Panvel | 160 |
| Kalyan | 241 |
| Dombivli | 247 |

At most 100 nearest matching snapshot cards are returned; total match count and
cap state are displayed. Reduce the radius or choose a more specific locality.
The live adapter retains its existing 50-card/250-source-element bounds. East/
West combined locality centers and broader regional aliases are labelled as
approximate. PIN centers are derived from OSM address tags, not India Post boundaries.

## Exact Railway deployment steps (existing project)

1. Open Railway → the existing MediInsight/Simplifier backend service. Keep its
   repository integration, root Dockerfile build, start command and PORT handling.
   The Dockerfile already copies all `backend/`, including this versioned dataset.
   Its build-time runtime check now refuses a missing/invalid snapshot.
2. Wait for the GitHub `main` push to trigger deployment, or open Deployments →
   deploy the latest commit if automatic deployment is disabled. Select the commit
   reported in the final delivery. Do not create another backend or paid resource.
3. Keep existing `ENVIRONMENT=production`, `AUTH_MODE=supabase`, `SUPABASE_URL`,
   `SUPABASE_PUBLISHABLE_KEY` and exact `CORS_ORIGINS`. Never use a service-role key
   for patient requests. No database migration is required for this addition.
4. For the most dependable Mumbai-only presentation, set
   `OSM_DISCOVERY_ENABLED=false` in Railway Variables and deploy that variable
   change. Covered searches still work. Outside-region searches show live-disabled
   errors honestly. To demonstrate the nationwide hybrid path, use true instead;
   outside coverage still depends on public service availability.
5. If enabling public live services, retain the identified `OSM_USER_AGENT`, one
   replica and private persistent shared `APP_DATA_DIR` for live quotas/cache as
   described in `docs/OSM_DISCOVERY.md`. The **snapshot itself needs no writable
   volume, refresh job, new API key or external database**.
6. Check deployment logs for successful model/font/OCR and snapshot validation,
   then open `https://simplifier-2-backend-production.up.railway.app/health`.
   HTTP 200 alone proves health, not this feature or deployment version.
7. Sign in through the frontend with a test account, open its report, search
   Mumbai and inspect the network response: `data_source= osm_snapshot`,
   `snapshot_version=mumbai-v1`, real retrieval date, and source-linked providers.
   With live disabled this is the direct acceptance check for the deployed snapshot.
8. Repeat with another account: the second account must not read the first
   account's report or consultation PDF. No snapshot query sends patient data out.

## Exact Vercel deployment steps (existing project)

1. Open the existing Vercel project connected to this repository and `main`.
   Keep Root Directory `frontend`, Install `npm ci`, Build `npm run build`,
   Output `dist`. Keep the committed Railway `/api/:path*` rewrite unchanged.
2. Let GitHub trigger the production deployment, or redeploy the latest `main`
   commit if the integration is disabled. No Google/OSM browser API key is required.
   Optional map style remains `VITE_OSM_MAP_STYLE_URL` (OpenFreeMap Liberty default).
3. The connected project currently lists `https://medi-insight-iota.vercel.app` as its verified domain; the repository's old `simplifier2-0.vercel.app` homepage returns 404. Verify the backend first, then sign in on the actual HTTPS frontend. Confirm
   `/api/v1/auth/configuration` reaches the backend through the existing rewrite.
4. Open a report → Doctors → Mumbai → search → inspect the dated snapshot label.
   Use “Browse general healthcare facilities” if the report-selected specialty has
   no source-tagged matches. Open Map and a marker; verify the matching profile
   and selected card. Test phone/website/directions only where supplied.
5. Repeat with `400001`, `Panvel`, `Dahisar`, `Mulund` and Kalyan-Dombivli. Test GPS
   while physically inside coverage; outside GPS intentionally uses live search.
   Test mobile layout, keyboard focus, Hindi and Marathi. Camera/report/OCR,
   nutrition, PDF/history and consultation consent must continue to work.

## Presentation checklist

- Use a controlled test account and clearly labelled example report or consented,
  de-identified real report. Do not show private patient documents to examiners.
- Keep internet for the hosted app, authentication and map tiles. The backend's
  **facility and covered-location searches** are independent of public search APIs.
- Rehearse Mumbai, Colaba, Dahisar, Mulund, Panvel and PIN 400001. Choose a smaller
  radius for fewer cards. Some specialists have zero tagged matches: show the
  honest explanation and explicit general-facility action.
- Keep the dated snapshot label/attribution visible. An OSM listing is not medical
  registration, current availability or a confirmed appointment.
- For a poor map connection, switch to Provider list; cards and local search remain
  usable. PDF sharing remains opt-in; no report is sent to OSM or providers.

## Rebuild/provenance

The raw 221 MB PBF is intentionally ignored in `artifacts/`, not shipped to Git or
Railway. Source: https://download.geofabrik.de/asia/india/western-zone-latest.osm.pbf
SHA-256: `1539d9f9d33cfb2788797ef15e4d3978961b809bef97a5f753a72c362a5f297c`.
No bulk Overpass or Nominatim requests were used to assemble this dataset.

For a future intentional snapshot revision, download an official PBF once, record
its HTTP Last-Modified/retrieval time and SHA-256, and use a separate tool environment:

```powershell
py -m venv artifacts/osm-tools
./artifacts/osm-tools/Scripts/python.exe -m pip install osmium==4.3.2
./artifacts/osm-tools/Scripts/python.exe backend/scripts/build_osm_snapshot.py artifacts/western-zone-latest.osm.pbf --source-last-modified "2026-10-17T22:31:07Z" --output artifacts/rebuilt-mumbai-v1.json
```

Use the actual source date, not the example date, for a new download. The default
retrieval date is the downloaded file's modification time; preserve it when copying
or pass the original recorded `--retrieved-at`. New data must receive a new version
and matching loader/schema checks; do not silently refresh the committed v1 during
a patient's search. Review statistical differences, names, PIN anomalies and tests.
Tool-only osmium is not a web-server dependency. Preserve the ODbL database notice
at `backend/app/data/osm/README.md`, source links and attribution when redistributing.

## Verification boundaries

Automated tests deny upstream calls for covered locality/PIN/GPS searches and run
actual bundled-data browser searches while live discovery is disabled. Map styles
in browser acceptance are deliberately mocked to avoid external tile dependency;
provider cards in the snapshot browser tests use the real committed OSM dataset.
Native-language, clinician and real contact-accuracy review remain human checks.
A GitHub push may trigger Railway/Vercel, but is not proof of completed deployments.
The final delivery states the actual hosted checks; never infer feature acceptance
from health alone. Nationwide live Overpass remains subject to the previously
observed upstream availability limits.

## Local test results

- Backend: 215 passed, 0 failed. Frontend: 25 passed, 0 failed.
- Browser: the existing 31 scenarios and two real-snapshot map/PIN/GPS scenarios
  pass after correcting a stale-card wait in the new acceptance tests.
- Production build, pip check and build-time snapshot/model/font/OCR validation
  pass. The existing MapLibre lazy-chunk size advisory and Starlette TestClient
  deprecation warning remain informational.

Hosted baseline inspection found the previous Railway deployment for commit
`51dedd6` marked failure while its older health endpoint still returned 200.
The connected Vercel `medi-insight` project had that previous frontend commit
READY. These observations do not verify this snapshot commit. Inspect the new
commit's deployment logs and test the authenticated snapshot endpoint after rollout.
