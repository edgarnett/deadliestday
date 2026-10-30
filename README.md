# DeadliestDay.org

Halloween (October 31) is the deadliest day of the year for child pedestrians in the US.
This repo holds the analysis and the static site behind [deadliestday.org](https://deadliestday.org).

Data: NHTSA [Fatality Analysis Reporting System (FARS)](https://www.nhtsa.gov/research-data/fatality-analysis-reporting-system-fars), National CSV files, 2000–2024.

## Reproduce

The FARS zips (about 600 MB) are not in the repo. Download one National CSV zip per year into a folder:

```
https://static.nhtsa.gov/nhtsa/downloads/FARS/<year>/National/FARS<year>NationalCSV.zip
```

Then, with [uv](https://docs.astral.sh/uv/):

```
uv run python halloween_deadliest.py <folder>   # per-day child pedestrian deaths, weekday table -> site_data.json
uv run python halloween_all.py <folder>         # all road deaths, map points -> site_data_all.json
uv run python halloween_compare.py <folder>     # Halloween vs other days (prints)
uv run python build_site.py                     # -> site/index.html
uv run python build_social.py                   # -> social/bluesky.png (needs Microsoft Edge)
```

`halloween_ped_all.py` is the all-ages version of the original child-pedestrian script. The `site_data*.json` files are checked in, so `build_site.py` runs without the zips.

The site is a single self-contained file, `site/index.html` (copied to `deploy/` for upload to Cloudflare Pages).

## Method notes

- Deaths are people with injury severity "fatal" (died within 30 days), counted by crash date.
- Pedestrians are FARS person type 5. Children are under 18; unknown ages are not counted as children.
- Single-weekday comparisons rest on 3–4 Halloweens each, so they are suggestive only.
- The 6 pm–midnight ratios in the site's comparison chart are typed in from the output of `halloween_compare.py`.

## Licenses

Code: MIT, see `LICENSE`. FARS data is a US government work in the public domain. State outlines in `us_states.json` come from [PublicaMundi/MappingAPI](https://github.com/PublicaMundi/MappingAPI) and derive from US Census boundaries.
