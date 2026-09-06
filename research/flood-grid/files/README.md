# Flood-grid study: reproducibility package

This package contains the complete 360-scenario, 11,880-solve experiment: source code, four native IEEE 123 feeder inputs, the USGS Rainelle flood-depth raster, pinned Python dependencies, and every recorded solve. It also includes the separate public-facility sampling analysis used for the Rainelle event context.

## Verify the published experiment

Unzip the package into a new directory, then run:

```sh
python3 verify_artifacts.py
```

This uses only Python's standard library. It verifies every packaged file and streams the complete compressed result through SHA-256. The result expands to 400,692,377 bytes with SHA-256 `16bb93472871c6bb17fa9e884259579a27ead0acc3a680dff57544a8cb3e51d4`.

To recalculate all 288 aggregate values and counts from the retained solves and verify the worked backup example:

```sh
python3 check_results.py
```

To inspect the JSON directly without writing a decompressed copy:

```python
import json, lzma
with lzma.open("reference/study.json.xz", "rt") as stream:
    study = json.load(stream)
print(study["campaign_accounting"])
print(study["aggregate_results"])
```

Allow about 3 GB of memory when loading the complete JSON. `reference/summary.json` contains the inputs, design, sitings, aggregate tables and accounting in a smaller file.

## Reproduce the experiment

On NixOS, run `nix-shell` in the extracted directory first; the included shell supplies the native Expat and C++ runtime libraries. On Debian or Ubuntu, install `libexpat1` and `libstdc++6` if those runtime libraries are absent.

Use Python 3.13.14 and the exact package versions in `requirements-lock.txt`. With [uv](https://docs.astral.sh/uv/):

```sh
uv venv --python 3.13.14 .venv
uv pip install --python .venv/bin/python -r requirements-lock.txt
.venv/bin/python verify_artifacts.py
.venv/bin/python run_synthetic_flood_grid_resilience.py
.venv/bin/python generate_synthetic_resilience_note.py
```

Alternatively, create a Python 3.13 virtual environment with `python3 -m venv .venv`, activate it, and run `python -m pip install -r requirements-lock.txt`.

The simulation writes `synthetic_flood_grid_v1/study.json`, `REPORT.md`, and `manifest.json`. The report generator adds HTML, SVG and PDF reports. The published reference remains separate in `reference/`. Run in a fresh extracted directory so an earlier local simulation output is preserved.

The experiment uses seeds 1103, 2203, 3303, 4403, 5503 and 6603, one through four failed assets, and all 15 two-slot assignments. Output timestamps and recorded platform strings vary between runs; compare the scenario records, aggregate results and accounting. The original Python and native OpenDSS versions are recorded in `reference/manifest.json`.

The original direct-dependency file is preserved as `requirements-synthetic-grid-study.txt`; `requirements-lock.txt` additionally pins its installed transitive dependencies.

## Reproduce the Rainelle event samples

```sh
.venv/bin/python run_public_exposure_study.py
```

This reads the same USGS raster and the four public facility point records in `data_v2/`. It selects the two Rainelle facilities and writes `public_exposure_v1/`. The original observations and their input hashes are in `reference/public_exposure_v1/`.

## Files and interpretation

- `run_synthetic_flood_grid_resilience.py`: exact original simulation source.
- `model/ieee123_isolated/`: the four exact native dependency files used by the simulation, plus their upstream license.
- `data/Meadow_Sewell_dem_derived.zip`: the original USGS depth-raster input.
- `reference/study.json.xz`: the complete original result, compressed losslessly with XZ.
- `reference/summary.json`: the compact original results summary.
- `reference/manifest.json`: original generator, input, output and engine bindings.
- `ARTIFACTS.json`: path, size and SHA-256 for each distributed artifact.
- `SOURCES.md`: input provenance and upstream terms.

Every solve records designated critical-load service, all enabled feeder-load voltage states, backup source measurements, isolation boundaries and the complete feasibility decision. The `flood_correlated_scenarios` and `independent_outage_scenarios` arrays retain all individual outcomes, including infeasible cases.
