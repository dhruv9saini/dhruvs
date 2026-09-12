# Data and source provenance

## Flood-depth raster

Credit: U.S. Geological Survey. June 2016 Rainelle flood-map data release, DOI [10.5066/F76T0K4K](https://doi.org/10.5066/F76T0K4K). The archive `Meadow_Sewell_dem_derived.zip` is the exact input used in the experiment, with SHA-256 `09d7100eca1c5f224c9bb93af4bd02e036e48794a03235622d519ca5903039d8`.

USGS-produced data are in the U.S. public domain; see the agency's [copyright and credit policy](https://www.usgs.gov/information-policies-and-instructions/copyrights-and-credits). The original raster archive and its contents are distributed unchanged.

## IEEE 123 feeder

The four files under `model/ieee123_isolated/` preserve the exact OpenDSS IEEE 123 feeder inputs used in this experiment. Their hashes are bound in `reference/manifest.json`; use this snapshot when reproducing the reported results.

The [DSS-Extensions OpenDSS examples repository](https://github.com/dss-extensions/electricdss-tst) maintains the upstream IEEE 123 test case and identifies its source as the official EPRI OpenDSS repository. Its copyright, redistribution conditions and disclaimer are retained verbatim in `model/ieee123_isolated/UPSTREAM_LICENSE.txt`. Existing source comments and notices are preserved.

## Public facility geometry

`data_v2/greenbrier_essential_facilities_with_geometry.geojson` preserves four public-facility point records from the WVU critical-facilities service used by the original sampling analysis. The fields are facility name, facility type and county, with point geometry. The separate empirical analysis selects the Rainelle Volunteer Fire Department and Rainelle Police Department. Its exact input hash is retained in `reference/public_exposure_v1/manifest.json`.

## Experiment source and outputs

The simulation, empirical sampler and report generator are the original study sources. The complete result retains its original bytes after XZ decompression. Packaging, checksums and instructions were added for public reproducibility; the simulation was not rerun to create this release.
