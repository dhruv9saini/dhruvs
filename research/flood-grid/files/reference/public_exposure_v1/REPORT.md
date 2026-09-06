# Rainelle Public-Data Flood-Exposure Robustness Study

## Result

Across 21 specified point, neighborhood, and geolocation-sensitivity comparisons, the Rainelle Volunteer Fire Department has greater observed June 2016 flood depth than the Rainelle Police Department. The smallest Fire-minus-Police difference is 0.146 ft.

This is a defensible public-data triage result: the Fire Department should receive first utility-service and site-condition confirmation if power-resilience work is being scoped. It does not prescribe a grid operation or restoration action.

## Methods and Baselines

The study evaluates nearest-cell and bilinear point samplers, distributional summaries in 3 m, 15 m, and 30 m circular neighborhoods, and a center-plus-eight 10 m offset sensitivity set. The priority ordering is accepted only when every estimator puts the Fire Department above the Police Department, including the conservative Fire minimum against the Police maximum for the offset set.

## Scope Boundary

The USGS raster documents the June 2016 event. It does not provide a utility network, ampacities, facility service topology, equipment elevations, outages, or restoration constraints. No grid performance, damage, or restoration conclusion follows from this study.

## Reproduction

Run `./.venv/bin/python run_public_exposure_study.py` after installing the pinned local rasterio/numpy environment. `study.json` records exact input hashes, data geometry, method choices, all observations, and every comparison.
