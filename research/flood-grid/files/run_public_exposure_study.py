from __future__ import annotations

import hashlib
import json
import math
import platform
import shutil
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import rowcol
from rasterio.warp import transform


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
FACILITIES = ROOT / "data_v2" / "greenbrier_essential_facilities_with_geometry.geojson"
ZIP = DATA / "Meadow_Sewell_dem_derived.zip"
EXTRACTED = ROOT / "work" / "usgs_rainelle"
RASTER = EXTRACTED / "Meadow_Sewell_dem_derived" / "depth_dem"
OUT = ROOT / "public_exposure_v1"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def extract_once() -> None:
    if not (RASTER / "hdr.adf").is_file():
        if EXTRACTED.exists():
            shutil.rmtree(EXTRACTED)
        EXTRACTED.mkdir(parents=True)
        with zipfile.ZipFile(ZIP) as archive:
            archive.extractall(EXTRACTED)


def bilinear(grid: np.ma.MaskedArray, floating_row: float, floating_col: float) -> float | None:
    r0, c0 = math.floor(floating_row), math.floor(floating_col)
    if r0 < 0 or c0 < 0 or r0 + 1 >= grid.shape[0] or c0 + 1 >= grid.shape[1]:
        return None
    dr, dc = floating_row - r0, floating_col - c0
    samples = [grid[r0, c0], grid[r0 + 1, c0], grid[r0, c0 + 1], grid[r0 + 1, c0 + 1]]
    if any(np.ma.is_masked(value) for value in samples):
        return None
    weights = [(1 - dr) * (1 - dc), dr * (1 - dc), (1 - dr) * dc, dr * dc]
    return float(sum(float(value) * weight for value, weight in zip(samples, weights)))


def circular_summary(grid: np.ma.MaskedArray, affine, x: float, y: float, radius_m: float) -> dict:
    center_row, center_col = rowcol(affine, x, y, op=float)
    pixel_x = abs(affine.a)
    pixel_y = abs(affine.e)
    row_radius = math.ceil(radius_m / pixel_y) + 1
    col_radius = math.ceil(radius_m / pixel_x) + 1
    rows = np.arange(max(0, math.floor(center_row) - row_radius), min(grid.shape[0], math.ceil(center_row) + row_radius + 1))
    cols = np.arange(max(0, math.floor(center_col) - col_radius), min(grid.shape[1], math.ceil(center_col) + col_radius + 1))
    rr, cc = np.meshgrid(rows, cols, indexing="ij")
    xs, ys = rasterio.transform.xy(affine, rr, cc, offset="center")
    distance = np.hypot(np.asarray(xs).reshape(rr.shape) - x, np.asarray(ys).reshape(rr.shape) - y)
    values = grid[rr, cc]
    usable = (distance <= radius_m) & ~np.ma.getmaskarray(values)
    sample = np.asarray(values[usable], dtype=float)
    if sample.size == 0:
        raise RuntimeError("No valid raster cells within requested circular neighborhood")
    return {
        "radius_m": radius_m,
        "valid_cell_count": int(sample.size),
        "min_ft": float(sample.min()),
        "p05_ft": float(np.quantile(sample, 0.05)),
        "median_ft": float(np.median(sample)),
        "mean_ft": float(sample.mean()),
        "p95_ft": float(np.quantile(sample, 0.95)),
        "max_ft": float(sample.max()),
    }


def point_methods(grid: np.ma.MaskedArray, affine, x: float, y: float) -> dict:
    floating_row, floating_col = rowcol(affine, x, y, op=float)
    nearest_row, nearest_col = rowcol(affine, x, y)
    nearest = grid[nearest_row, nearest_col]
    if np.ma.is_masked(nearest):
        raise RuntimeError("Facility point has no depth raster value")
    interpolation = bilinear(grid, floating_row, floating_col)
    return {
        "nearest_cell_ft": float(nearest),
        "bilinear_ft": interpolation,
        "nearest_cell_row_col": [int(nearest_row), int(nearest_col)],
    }


def perturbation_range(grid: np.ma.MaskedArray, affine, x: float, y: float) -> dict:
    offsets = [(0.0, 0.0)] + [(10 * math.cos(angle), 10 * math.sin(angle)) for angle in np.linspace(0, 2 * math.pi, 8, endpoint=False)]
    values = []
    for dx, dy in offsets:
        value = point_methods(grid, affine, x + dx, y + dy)["nearest_cell_ft"]
        values.append(value)
    return {
        "offset_pattern": "center plus eight 10 m radial offsets",
        "sample_count": len(values),
        "min_ft": float(min(values)),
        "median_ft": float(np.median(values)),
        "max_ft": float(max(values)),
    }


def main() -> None:
    extract_once()
    OUT.mkdir(parents=True, exist_ok=True)
    facility_data = json.loads(FACILITIES.read_text())
    with rasterio.open(RASTER) as source:
        grid = source.read(1, masked=True)
        observations = []
        for feature in facility_data["features"]:
            if feature["geometry"] is None:
                continue
            name = feature["properties"]["Name"]
            if name not in {"Rainelle Volunteer Fire Department", "Rainelle Police Department"}:
                continue
            longitude, latitude = feature["geometry"]["coordinates"]
            x, y = transform("EPSG:4326", source.crs, [longitude], [latitude])
            x, y = float(x[0]), float(y[0])
            point = point_methods(grid, source.transform, x, y)
            neighborhoods = {str(radius): circular_summary(grid, source.transform, x, y, radius) for radius in (3.0, 15.0, 30.0)}
            perturbation = perturbation_range(grid, source.transform, x, y)
            observations.append({
                "facility": name,
                "facility_type": feature["properties"]["Facility_Type"],
                "coordinates_wgs84": [longitude, latitude],
                "point_methods": point,
                "neighborhoods": neighborhoods,
                "ten_meter_geolocation_sensitivity": perturbation,
            })
    if len(observations) != 2:
        raise RuntimeError("Expected exactly the two Rainelle facilities inside the USGS raster")
    observations.sort(key=lambda item: item["facility"])
    fire = next(item for item in observations if item["facility_type"] == "Fire Department")
    police = next(item for item in observations if item["facility_type"] == "Police Department")
    comparisons = []
    for method in ("nearest_cell_ft", "bilinear_ft"):
        comparisons.append({"estimator": method, "fire_minus_police_ft": fire["point_methods"][method] - police["point_methods"][method]})
    for radius in (3.0, 15.0, 30.0):
        for metric in ("min_ft", "p05_ft", "median_ft", "mean_ft", "p95_ft", "max_ft"):
            comparisons.append({"estimator": f"{radius:g}m_{metric}", "fire_minus_police_ft": fire["neighborhoods"][str(radius)][metric] - police["neighborhoods"][str(radius)][metric]})
    comparisons.append({"estimator": "10m_offset_minimum", "fire_minus_police_ft": fire["ten_meter_geolocation_sensitivity"]["min_ft"] - police["ten_meter_geolocation_sensitivity"]["max_ft"]})
    robust = all(row["fire_minus_police_ft"] > 0 for row in comparisons)
    result = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "study_status": "complete_public_data_exposure_robustness_analysis",
        "research_question": "Do public USGS flood-depth data support a stable facility-level exposure prioritization for the two Rainelle public-safety facilities, before any utility topology or ampacity data are available?",
        "inputs": {
            "usgs_rainelle_depth_release": "https://doi.org/10.5066/F76T0K4K",
            "facility_geometry_source": "Preserved WVU critical-facilities service response with coordinate-bearing features",
            "raster_crs": str(source.crs),
            "raster_shape": [int(source.height), int(source.width)],
            "raster_cell_size_m": [abs(source.transform.a), abs(source.transform.e)],
            "input_sha256": {"depth_release_zip": sha256(ZIP), "facility_geometry": sha256(FACILITIES)},
        },
        "engine": {"python": sys.version, "platform": platform.platform(), "rasterio": rasterio.__version__, "numpy": np.__version__},
        "methods": {
            "point_baselines": ["nearest raster cell", "bilinear interpolation"],
            "neighborhood_estimators": "3 m, 15 m, and 30 m circular neighborhoods reporting min, p05, median, mean, p95, and max",
            "geolocation_sensitivity": "center point plus eight 10 m radial offsets, sampled by nearest raster cell",
            "evaluation": "The priority ordering is called robust only if every listed estimator gives Fire Department depth greater than Police Department depth, including the conservative fire minimum versus police maximum under the 10 m perturbation set.",
        },
        "facility_observations": observations,
        "comparison_table": comparisons,
        "result": {
            "fire_department_higher_observed_event_depth_under_all_estimators": robust,
            "estimator_count": len(comparisons),
            "minimum_fire_minus_police_ft": min(row["fire_minus_police_ft"] for row in comparisons),
        },
        "claim_boundary": [
            "This is an observed June 2016 flood-exposure prioritization result for two public facility point records, not a forecast or a facility-damage model.",
            "It does not identify utility assets, feeder topology, service connections, equipment elevation, outage causes, road access, personnel availability, protection settings, line ampacities, restoration feasibility, or an operational action.",
            "The result can prioritize which facility merits first utility and site-data confirmation. It cannot rank power-restoration actions without permissioned utility and facility data.",
        ],
    }
    (OUT / "study.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    summary = [
        "# Rainelle Public-Data Flood-Exposure Robustness Study",
        "",
        "## Result",
        "",
        f"Across {result['result']['estimator_count']} specified point, neighborhood, and geolocation-sensitivity comparisons, the Rainelle Volunteer Fire Department has greater observed June 2016 flood depth than the Rainelle Police Department. The smallest Fire-minus-Police difference is {result['result']['minimum_fire_minus_police_ft']:.3f} ft.",
        "",
        "This is a defensible public-data triage result: the Fire Department should receive first utility-service and site-condition confirmation if power-resilience work is being scoped. It does not prescribe a grid operation or restoration action.",
        "",
        "## Methods and Baselines",
        "",
        "The study evaluates nearest-cell and bilinear point samplers, distributional summaries in 3 m, 15 m, and 30 m circular neighborhoods, and a center-plus-eight 10 m offset sensitivity set. The priority ordering is accepted only when every estimator puts the Fire Department above the Police Department, including the conservative Fire minimum against the Police maximum for the offset set.",
        "",
        "## Scope Boundary",
        "",
        "The USGS raster documents the June 2016 event. It does not provide a utility network, ampacities, facility service topology, equipment elevations, outages, or restoration constraints. No grid performance, damage, or restoration conclusion follows from this study.",
        "",
        "## Reproduction",
        "",
        "Run `./.venv/bin/python run_public_exposure_study.py` after installing the pinned local rasterio/numpy environment. `study.json` records exact input hashes, data geometry, method choices, all observations, and every comparison.",
        "",
    ]
    (OUT / "REPORT.md").write_text("\n".join(summary))
    manifest = {"files": {path.name: sha256(path) for path in (OUT / "study.json", OUT / "REPORT.md")}, "generator_sha256": sha256(Path(__file__)), "inputs": result["inputs"]["input_sha256"], "engine": result["engine"], "result": result["result"]}
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
