# Data Sources & Attribution

This platform never fabricates football results, squads, statistics or records. Every
match, score, goalscorer and shootout comes from an openly-licensed dataset; tournament
metadata (hosts, formats) is curated public-record fact; and current-tournament placements
are either verified from the public record or **derived from the imported match data** (the
final/last match of an edition). Fields with no available data are shown as "Not recorded"
rather than estimated.

## Primary historical source — martj42 / international_results

| | |
|---|---|
| **Repository** | https://github.com/martj42/international_results |
| **License** | **CC0 1.0 (public domain)** — no restrictions, commercial use permitted |
| **License URL** | https://creativecommons.org/publicdomain/zero/1.0/ |
| **Coverage** | 49,940 men's international results, 1872 → 2026 (incl. **1,068 World Cup finals matches**) |
| **Files used** | `results.csv`, `shootouts.csv`, `goalscorers.csv`, `former_names.csv` |
| **Player data** | `goalscorers.csv` provides per-goal scorer, minute, own-goal and penalty flags |
| **Attribution** | CC0 waives attribution requirements; we credit the project anyway |

**What it provides:** match date, teams, score (regulation + extra time), tournament label,
city, venue country, neutral-ground flag; penalty-shootout winners; individual goalscorers.

**What it does NOT provide:** group-stage composition, explicit knockout round labels,
player profiles (DOB, position, club, appearances), lineups, or women's internationals. These
gaps are surfaced honestly in the UI (see Limitations below) rather than filled with guesses.

> Note: although the project README describes coverage "up to 2024", the live dataset is
> updated past that point and includes the full 48-team **2026 World Cup** (104 matches).

## Curated verified seed (tournament metadata)

`backend/app/ingestion/reference_data.py` holds hand-verified **public-record facts** used only
for display and structure — not performance statistics:

- World Cup edition metadata: host country, number of teams, tournament format (1930–2026).
- Confirmed champions / runners-up / third place for 1930–2022 (FIFA official record).
- Country attributes: confederation, FIFA code, ISO-2 code (for flag images).

For editions where the seed does not provide a champion (e.g. 2026), placements are **derived
from the match data itself** (champion = winner of the final/last match; third = winner of the
third-place play-off) and labelled with `data_confidence = "derived"`.

## Current / live enrichment — API-Football (API-SPORTS)

| | |
|---|---|
| **Provider** | https://www.api-football.com/ |
| **Plan** | Free tier — **100 requests/day**, 10 requests/minute |
| **License** | Commercial API, subject to provider terms; **not redistributed** |
| **Usage here** | On-demand only, via the ingestion CLI (`sync-status`, `sync-tournament`). Never polled on page load. The key is server-side only and never exposed to the browser. |

Because the free plan allows only 100 requests/day, API-Football is **not** used for bulk
historical ingestion — martj42 is the backbone. API-Football is reserved for current/live
enrichment where quota allows.

## Flag images — flagcdn.com

Country flags are loaded by ISO-2 code from https://flagcdn.com (free, hotlink-friendly,
public-domain flag imagery). Defunct nations (Soviet Union, Yugoslavia, West Germany,
Czechoslovakia, Zaire, etc.) have no modern flag and fall back to a neutral monogram badge —
historical team identities are not misrepresented with a successor state's flag.

## Provenance tracking

Every imported row records its `source_key`; `data_source` rows store each source's license and
last-sync time; `import_job` rows log each ingestion run. The in-app **Data Status** page and the
`GET /api/v1/data-status` endpoint surface this provenance.

## Known data limitations

- **Group tables / standings** — not derivable from martj42; the Groups tab shows a clear
  "not available" state. Match results are available under Fixtures.
- **Full knockout bracket** — round labels are not in the source. The Bracket view shows the
  final and third-place play-off (derived from fixture chronology + verified placements).
- **Player profiles & appearances** — only goals are in the source; profile fields are
  "Not recorded".
- **Women's World Cup, Club World Cup, qualification** — competition rows exist but are not yet
  populated (martj42 is men's full internationals only; women's data needs a separate source).
