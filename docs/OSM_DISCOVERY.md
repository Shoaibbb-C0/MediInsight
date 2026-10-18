> **Hybrid update:** Covered Mumbai searches now use a bundled genuine snapshot without Overpass/Nominatim. `OSM_DISCOVERY_ENABLED` controls only nationwide live requests. See [coverage, data gaps, demo and deployment steps](HYBRID_DOCTOR_DEMO.md). The limits below apply to the live adapter.

# OSM doctor discovery — operations and verification

This replaces the Google-based discovery/map integration. No Google key, Cloud
billing, Map ID, paid geocoder or paid map SDK is needed. Supabase authentication,
report ownership and consultation PDF consent are unchanged.

## Local and Railway configuration

1. Install the updated frontend lockfile: `cd frontend` then `npm.cmd ci` on Windows
   (`npm ci` on Linux). Start the existing backend/frontend scripts as before.
2. Backend defaults are Nominatim search and Overpass interpreter. Set privately:
   ```dotenv
   OSM_DISCOVERY_ENABLED=true
   OSM_USER_AGENT="Simplifier2.0/1.0 (+https://github.com/Shoaibbb-C0/Simplifier2.0)"
   OSM_NOMINATIM_URL=https://nominatim.openstreetmap.org/search
   OSM_OVERPASS_URL=https://overpass-api.de/api/interpreter
   ```
   Replace the identification contact with your maintained application URL/contact
   if ownership changes. Endpoint URLs can be changed by environment/restart,
   without a code update. Never accept an endpoint URL from a patient request.
3. Public mode requires **one Railway replica** with a **private persistent writable
   APP_DATA_DIR** shared by its workers. `osm_discovery.sqlite3` holds aggregate
   limits and public location/facility cache; no patient identity/report is stored
   there. Keep that directory private and out of Git. Retain existing Supabase,
   CORS and auth settings. Do not put a private key in a VITE variable.
4. If that persistent single-instance configuration is unavailable, set
   `OSM_DISCOVERY_ENABLED=false` until it is supplied, or configure a suitably
   operated self-hosted service. Do not add replicas with independent quota files.
   No volume, database, paid resource or deployment was created by this change.
5. The frontend uses OpenFreeMap Liberty by default. Optional
   `VITE_OSM_MAP_STYLE_URL=https://tiles.openfreemap.org/styles/liberty` selects a
   compatible style. MapLibre bundles its worker through Vite. Keep visible map
   and listing attribution. Remove obsolete GOOGLE_MAPS_SERVER_KEY,
   VITE_GOOGLE_MAPS_BROWSER_KEY, VITE_GOOGLE_MAPS_MAP_ID and capability-registry
   settings from your deployment dashboards; the new adapter does not read them.
6. The existing Railway Dockerfile and Vercel `/api` external rewrite remain
   unchanged. A GitHub push may trigger their existing integrations. New browser
   environment variables require a Vercel rebuild. No hosting account setting is
   changed by the code.

## Public-service restrictions — developer responsibility

Read [Nominatim's usage policy](https://operations.osmfoundation.org/policies/nominatim/)
and [Overpass shared-capacity guidance](https://dev.overpass-api.de/overpass-doc/en/preface/commons.html)
before enabling public access. The user deliberately selected these services;
operators remain responsible for compliance. Neither provides guaranteed
production capacity. Overpass explicitly recommends operating your own instance
for an application that relies on it as a backend. A public endpoint is suitable
only for a constrained low-volume pilot, not a scalable production SLA.

- Searches run only on explicit submission/geolocation action; no autocomplete,
  background geocoding, scraping, bulk lookup or automatic mirror failover.
- Identified server-side Nominatim requests: at least 1.1 seconds between starts,
  at most 500 uncached requests per UTC day **for the whole shared deployment**.
  Country restricted to India. Named-city search uses settlement filtering;
  structured six-digit PIN search is supported. Ambiguous locations are refused.
- Overpass: at least five seconds between starts; at most 100 uncached requests
  per UTC day. Each response is bounded to 8 MB (at most 800 MB/day), query timeout
  20 seconds, HTTP timeout 25 seconds/connect 5 seconds, no application retry.
- Geocoding cache lasts one day; facility cache ten minutes. SQLite transactions
  coordinate processes sharing the same disk, not separate replicas. At most 300
  cached responses; expired entries are removed on successful cache writes.
- 429/509 triggers a shared 60-second cooldown. Local quota errors include
  Retry-After. Outages/timeouts/incomplete responses return controlled errors,
  never demonstration providers or a fabricated successful empty search.
- Radius is bounded to 1–50 km, at most 250 source elements and 50 returned cards.
  Results may be incomplete and are explicitly marked when capped. Narrow the
  radius for more local matches. No automatic radius expansion.

## Discovery and privacy contract

The existing authenticated report endpoint still resolves ownership before
searching. The backend computes report-related specialty recommendations locally.
Only user-entered place/PIN (and interface language) go to Nominatim. Overpass
receives a general healthcare query, radius and location rounded to three decimal
places. **Specialty, patient identity, cookies, report IDs, findings and report
contents are never sent upstream.** The map fetches public style/vector tiles
for the viewport; marker names/data stay in the browser. External links use
no-referrer and contain no report. Directions send only the facility destination.

Healthcare nodes/ways/relations are accepted only with real medical amenity or
healthcare tags, a supplied name and coordinates. Specialty searches require an
explicit matching `healthcare:speciality`/`healthcare:specialty` tag; unknown tags
are not guessed from a clinic name. General Physician shows medical facilities
without asserting each has a general physician. Missing specialty tags can hide
relevant clinics: switch to General Physician or contact a facility yourself.
OSM community tags are not verified professional registration or availability.

Cards sort by straight-line nearest distance among returned elements. There are
no ratings/reviews, invented credentials, hours, fees or available slots. Call
and website require usable source tags; directions require actual coordinates.
No local booking is created. Demonstration fixtures remain explicitly labelled
and are never substituted into a live query.

Data: [© OpenStreetMap contributors, ODbL](https://www.openstreetmap.org/copyright).
Map: [OpenFreeMap](https://openfreemap.org/quick_start/) / OpenMapTiles / OSM
attribution is retained by the style and renderer. Do not hide it with CSS.

## Acceptance and live boundaries

Run `./scripts/Test-All.ps1 -IncludeBrowser`. Tests mock external services and
exercise location ambiguity, empty results, missing/unsafe tags, nearest-only
sorting, upstream quota/outage/timeout, cache/limits, specialty privacy, owner
isolation, explicit report consent, geolocation denial and manual search fallback.
MapLibre unit tests cover marker selection, selected-card synchronization,
cleanup and WebGL failure. Browser checks use a clearly mocked blank style and
mocked facility data; they are not live OSM coverage claims.

On 19 October 2026 an identified live Nominatim search resolved Panvel,
Maharashtra to one settlement after applying the city filter. The public Overpass
probe did not return usable data and the adapter returned controlled HTTP 503.
Both POST and GET attempts to that same public Overpass endpoint failed; GET explicitly timed out. OpenFreeMap style JSON and the existing Railway production health endpoint returned HTTP 200. No mirror rotation or fabricated listings were used. Live facility coverage and
hosted end-to-end acceptance remain unverified.

After automatic deployments, test the actual HTTPS frontend: allow location or
submit Panvel/Maharashtra/PIN, inspect source links, nearest order, map/card
selection, keyboard access, Hindi/Marathi, denied geolocation, empty results and
outage fallback. Repeat two-account isolation. Public listing/contact accuracy
and coverage in Mumbai, Pune, Kalyan, Nashik, Nagpur and Pusad require real checks;
mocked tests cannot establish them. A real provider scheduler is still required
before confirming any appointment.

## Local verification results — 19 October 2026

- Backend: 167 passed, 0 failed (47 OSM/consultation cases included).
- Frontend: 22 passed, 0 failed; actual browser: 31 passed, 0 failed.
- Production build and pip dependency check pass. npm audit: zero known findings.
- MapLibre is dynamically imported when the map is requested. Its renderer chunk
  exceeds Vite's advisory 500 kB threshold; it is not part of initial app JS.
- The backend suite emits one existing Starlette/httpx TestClient deprecation
  warning. It does not affect these test results.
- Railway Dockerfile and Vercel API rewrite have no changes in this patch.
- Local browser coverage does not verify live tiles, provider accuracy, real
  Supabase/RLS acceptance or hosted rollout of this commit.
