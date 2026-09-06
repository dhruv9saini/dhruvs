from __future__ import annotations

import hashlib
import itertools
import json
import platform
import shutil
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import opendssdirect as dss
import rasterio


ROOT = Path(__file__).resolve().parent
ZIP = ROOT / "data" / "Meadow_Sewell_dem_derived.zip"
EXTRACTED = ROOT / "work" / "usgs_rainelle"
RASTER = EXTRACTED / "Meadow_Sewell_dem_derived" / "depth_dem"
MASTER = ROOT / "model" / "ieee123_isolated" / "IEEE123Master.dss"
OUT = ROOT / "synthetic_flood_grid_v1"
SEEDS = (1103, 2203, 3303, 4403, 5503, 6603)
OUTAGE_COUNTS = (1, 2, 3, 4)
BUDGET = 2
BACKUP_CAPACITY_KVA = 60.0
SOLVE_COUNT = 0
ASSETS = (
    {"asset": "A", "line": "L83", "load": "s84c", "bus": "84.3", "kw": 20.0, "kvar": 10.0},
    {"asset": "B", "line": "L84", "load": "s83c", "bus": "83.3", "kw": 20.0, "kvar": 10.0, "capacitor": "C83"},
    {"asset": "C", "line": "L89", "load": "s90b", "bus": "90.2", "kw": 40.0, "kvar": 20.0, "capacitor": "C90b"},
    {"asset": "D", "line": "L91", "load": "s92c", "bus": "92.3", "kw": 40.0, "kvar": 20.0, "capacitor": "C92c"},
    {"asset": "E", "line": "L93", "load": "s94a", "bus": "94.1", "kw": 40.0, "kvar": 20.0},
    {"asset": "F", "line": "L95", "load": "s96b", "bus": "96.2", "kw": 20.0, "kvar": 10.0},
)


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def extract_once() -> None:
    if (RASTER / "hdr.adf").is_file():
        return
    if EXTRACTED.exists():
        shutil.rmtree(EXTRACTED)
    EXTRACTED.mkdir(parents=True)
    with zipfile.ZipFile(ZIP) as archive:
        archive.extractall(EXTRACTED)


def synthetic_siting(seed: int, values: np.ndarray) -> list[dict]:
    rng = np.random.default_rng(seed)
    selected = rng.choice(values, size=len(ASSETS), replace=False)
    output = [dict(asset, synthetic_flood_depth_ft=float(depth)) for asset, depth in zip(ASSETS, selected)]
    return output


def voltage(bus: str) -> float:
    bus_name, phase = bus.split(".")
    dss.Circuit.SetActiveBus(bus_name)
    values = dict(zip(dss.Bus.Nodes(), dss.Bus.puVmagAngle()[0::2]))
    return float(values[int(phase)])


def load_voltage_state(name: str) -> dict:
    dss.Circuit.SetActiveElement(f"Load.{name}")
    enabled = bool(dss.CktElement.Enabled())
    bus_name = dss.CktElement.BusNames()[0].split(".")[0]
    dss.Circuit.SetActiveBus(bus_name)
    values = [float(value) for value in dss.Bus.puVmagAngle()[0::2]]
    energized = bool(values) and max(values) >= 0.1
    minimum = min(values) if values else None
    maximum = max(values) if values else None
    return {
        "load": name,
        "enabled": enabled,
        "minimum_bus_voltage_pu": minimum,
        "maximum_bus_voltage_pu": maximum,
        "energized": energized,
        "energized_voltage_in_0_95_to_1_05_pu_band": energized and minimum is not None and maximum is not None and minimum >= 0.95 and maximum <= 1.05,
    }


def source_measurement(name: str) -> dict:
    dss.Circuit.SetActiveElement(f"Vsource.{name}")
    powers = dss.CktElement.Powers()
    currents = dss.CktElement.CurrentsMagAng()[0::2]
    apparent = abs(complex(powers[0], powers[1]))
    current = float(max(currents)) if currents else 0.0
    rated_current = BACKUP_CAPACITY_KVA / 2.402
    return {
        "source": name,
        "apparent_kva": apparent,
        "current_a": current,
        "rated_current_a": rated_current,
        "within_defined_source_limits": apparent <= BACKUP_CAPACITY_KVA + 1e-6 and current <= rated_current + 1e-6,
    }


def solve(assets: list[dict], failed: set[str], hardened: set[str], backup: set[str]) -> dict:
    global SOLVE_COUNT
    SOLVE_COUNT += 1
    dss.Basic.ClearAll()
    dss.Text.Command(f'Compile "{MASTER}"')
    active_backups = []
    isolated = []
    for asset in assets:
        if asset["asset"] not in failed or asset["asset"] in hardened:
            continue
        dss.Text.Command(f"Edit Line.{asset['line']} enabled=no")
        if "capacitor" in asset:
            dss.Text.Command(f"Edit Capacitor.{asset['capacitor']} enabled=no")
        isolated.append(asset)
        if asset["asset"] in backup:
            source_name = f"backup_{asset['asset'].lower()}"
            dss.Text.Command(f"New Vsource.{source_name} phases=1 bus1={asset['bus']} basekv=2.402 pu=1 baseMVA={BACKUP_CAPACITY_KVA / 1000.0} puZ1=0.01")
            active_backups.append((source_name, asset))
    dss.Solution.Solve()
    converged = bool(dss.Solution.Converged())
    source_reports = [source_measurement(name) for name, _ in active_backups] if converged else []
    boundary_reports = []
    for asset in isolated:
        dss.Lines.Name(asset["line"])
        currents = dss.CktElement.CurrentsMagAng()[0::2]
        current = float(max(currents)) if currents else 0.0
        boundary_reports.append({"asset": asset["asset"], "line": asset["line"], "open": not dss.CktElement.Enabled(), "current_a": current})
    full_feeder_load_state = [load_voltage_state(name) for name in dss.Loads.AllNames()] if converged else []
    feeder_summary = {
        "enabled_load_count": sum(item["enabled"] for item in full_feeder_load_state),
        "energized_load_count": sum(item["enabled"] and item["energized"] for item in full_feeder_load_state),
        "deenergized_load_count": sum(item["enabled"] and not item["energized"] for item in full_feeder_load_state),
        "energized_loads_in_voltage_band_count": sum(item["enabled"] and item["energized_voltage_in_0_95_to_1_05_pu_band"] for item in full_feeder_load_state),
        "all_energized_loads_in_voltage_band": bool(full_feeder_load_state) and all(not item["enabled"] or not item["energized"] or item["energized_voltage_in_0_95_to_1_05_pu_band"] for item in full_feeder_load_state),
    }
    service = []
    for asset in assets:
        expected = asset["kw"]
        intended = asset["asset"] not in failed or asset["asset"] in hardened or asset["asset"] in backup
        dss.Circuit.SetActiveElement(f"Load.{asset['load']}")
        powers = dss.CktElement.Powers()
        load_kw = float(powers[0])
        load_voltage = voltage(asset["bus"])
        served = intended and converged and 0.95 <= load_voltage <= 1.05 and load_kw >= 0.99 * expected
        service.append({"asset": asset["asset"], "intended_to_be_served": intended, "served": served, "served_kw": load_kw if served else 0.0, "actual_load_kw": load_kw, "voltage_pu": load_voltage})
    feasible = converged and feeder_summary["all_energized_loads_in_voltage_band"] and all(item["within_defined_source_limits"] for item in source_reports) and all(item["open"] and item["current_a"] == 0.0 for item in boundary_reports) and all(item["served"] for item in service if item["intended_to_be_served"])
    return {
        "electrically_feasible_under_defined_constraints": feasible,
        "converged": converged,
        "served_critical_kw": sum(item["served_kw"] for item in service),
        "service": service,
        "full_feeder_load_state": full_feeder_load_state,
        "full_feeder_voltage_summary": feeder_summary,
        "backup_source_reports": source_reports,
        "isolation_boundary_reports": boundary_reports,
        "thermal_assessment": "not performed: IEEE 123 source line ampacities are not used or inferred in this study",
    }


def summarize(values: list[float]) -> dict:
    array = np.asarray(values, dtype=float)
    return {"count": int(array.size), "mean_served_critical_kw": float(array.mean()), "min_served_critical_kw": float(array.min()), "max_served_critical_kw": float(array.max())}


def constrained_summary(results: list[dict]) -> dict:
    unconstrained = [result["served_critical_kw"] for result in results]
    feasible = [result["served_critical_kw"] for result in results if result["electrically_feasible_under_defined_constraints"]]
    return {
        "solve_count": len(results),
        "feasible_solve_count": len(feasible),
        "feasible_solve_fraction": float(len(feasible) / len(results)),
        "mean_solved_critical_kw_unconstrained": float(np.mean(unconstrained)),
        "min_solved_critical_kw_unconstrained": float(np.min(unconstrained)),
        "max_solved_critical_kw_unconstrained": float(np.max(unconstrained)),
        "mean_critical_kw_among_feasible_solves": float(np.mean(feasible)) if feasible else None,
        "min_critical_kw_among_feasible_solves": float(np.min(feasible)) if feasible else None,
        "max_critical_kw_among_feasible_solves": float(np.max(feasible)) if feasible else None,
    }


def policy_results(assets: list[dict], failed: set[str], depth_order: list[str]) -> dict:
    names = [asset["asset"] for asset in assets]
    all_slots = list(itertools.combinations(names, BUDGET))
    depth_slots = set(depth_order[:BUDGET])
    no_action = solve(assets, failed, set(), set())
    depth_hardening = solve(assets, failed, depth_slots, set())
    depth_backup = solve(assets, failed, set(), depth_slots)
    random_hardening = [{"intervention_slots": list(slots), "result": solve(assets, failed, set(slots), set())} for slots in all_slots]
    random_backup = [{"intervention_slots": list(slots), "result": solve(assets, failed, set(), set(slots))} for slots in all_slots]
    return {
        "no_action": no_action,
        "depth_informed_hardening": depth_hardening,
        "depth_informed_backup": depth_backup,
        "random_two_slot_hardening_cases": random_hardening,
        "random_two_slot_backup_cases": random_backup,
        "random_two_slot_hardening_baseline": summarize([item["result"]["served_critical_kw"] for item in random_hardening]),
        "random_two_slot_backup_baseline": summarize([item["result"]["served_critical_kw"] for item in random_backup]),
    }


def main() -> None:
    global SOLVE_COUNT
    SOLVE_COUNT = 0
    extract_once()
    OUT.mkdir(parents=True, exist_ok=True)
    with rasterio.open(RASTER) as source:
        valid = np.asarray(source.read(1, masked=True).compressed(), dtype=float)
        raster_info = {"crs": str(source.crs), "shape": [int(source.height), int(source.width)], "cell_size_m": [abs(source.transform.a), abs(source.transform.e)], "valid_depth_cell_count": int(valid.size)}
    mapped_depths = []
    correlated = []
    independent = []
    for seed in SEEDS:
        assets = synthetic_siting(seed, valid)
        depth_order = [asset["asset"] for asset in sorted(assets, key=lambda item: item["synthetic_flood_depth_ft"], reverse=True)]
        mapped_depths.append({"seed": seed, "assets": assets, "depth_rank_descending": depth_order})
        for outage_count in OUTAGE_COUNTS:
            correlated_failed = set(depth_order[:outage_count])
            correlated.append({"seed": seed, "outage_count": outage_count, "failed_assets": sorted(correlated_failed), "policies": policy_results(assets, correlated_failed, depth_order)})
            for failed_tuple in itertools.combinations([asset["asset"] for asset in assets], outage_count):
                failed = set(failed_tuple)
                independent.append({"seed": seed, "outage_count": outage_count, "failed_assets": list(failed_tuple), "policies": policy_results(assets, failed, depth_order)})
    def aggregate(entries: list[dict], policy: str) -> dict:
        return constrained_summary([entry["policies"][policy] for entry in entries])
    def aggregate_random(entries: list[dict], policy: str) -> dict:
        cases = [case["result"] for entry in entries for case in entry["policies"][policy]]
        return constrained_summary(cases)
    aggregate_results = {}
    for outage_count in OUTAGE_COUNTS:
        corr = [row for row in correlated if row["outage_count"] == outage_count]
        ind = [row for row in independent if row["outage_count"] == outage_count]
        aggregate_results[str(outage_count)] = {
            "flood_correlated": {policy: aggregate(corr, policy) for policy in ("no_action", "depth_informed_hardening", "depth_informed_backup")},
            "independent_outage": {policy: aggregate(ind, policy) for policy in ("no_action", "depth_informed_hardening", "depth_informed_backup")},
            "random_baselines_under_flood_correlated": {
                "hardening": aggregate_random(corr, "random_two_slot_hardening_cases"),
                "backup": aggregate_random(corr, "random_two_slot_backup_cases"),
            },
        }
    all_scenarios = correlated + independent
    retained_backup_results = [
        result
        for scenario in all_scenarios
        for result in (
            [scenario["policies"]["depth_informed_backup"]]
            + [case["result"] for case in scenario["policies"]["random_two_slot_backup_cases"]]
        )
    ]
    infeasible_backup_results = [result for result in retained_backup_results if not result["electrically_feasible_under_defined_constraints"]]
    source_limited_backup_results = [
        result
        for result in infeasible_backup_results
        if any(not source["within_defined_source_limits"] for source in result["backup_source_reports"])
    ]
    retained_hardening_results = [
        result
        for scenario in all_scenarios
        for result in (
            [scenario["policies"]["depth_informed_hardening"]]
            + [case["result"] for case in scenario["policies"]["random_two_slot_hardening_cases"]]
        )
    ]
    infeasible_hardening_results = [result for result in retained_hardening_results if not result["electrically_feasible_under_defined_constraints"]]
    study = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "complete_synthetic_flood_grid_resilience_experiment",
        "research_question": "Under explicitly synthetic placement of IEEE 123 critical terminal assets onto empirical USGS Rainelle flood-depth samples, how do flood-correlated and depth-independent outages change served critical load under equal-count hardening and backup baselines?",
        "inputs": {"usgs_depth_release": "https://doi.org/10.5066/F76T0K4K", "depth_zip_sha256": digest(ZIP), "native_dss_dependencies": {str(path.relative_to(ROOT)): digest(path) for path in (MASTER, MASTER.parent / "IEEELineCodes.DSS", MASTER.parent / "IEEE123Regulators.DSS", MASTER.parent / "IEEE123Loads.DSS")}, "raster": raster_info},
        "engine": {"python": sys.version, "platform": platform.platform(), "numpy": np.__version__, "rasterio": rasterio.__version__, "opendssdirect": dss.__version__, "opendss_engine": dss.Basic.Version()},
        "design": {
            "synthetic_siting": "For each of six fixed seeds, six valid USGS raster depths are sampled without replacement and assigned in fixed order to six disclosed terminal IEEE 123 assets. This is a controlled synthetic co-location, not a geographic mapping to a real utility.",
            "flood_correlated_outage": "For each synthetic siting, the highest-depth one through four assets fail. This deliberately aligns the failure mechanism with the depth-informed policy; it is a controlled mechanism test, not an independent prediction validation.",
            "independent_outage": "For the same outage count and siting, every combination of failed assets is evaluated, giving the exact uniform independent-outage baseline.",
            "interventions": "Every hardening or backup policy receives exactly two abstract intervention slots. Random baselines enumerate all 15 two-slot assignments. Cross-technology costs are not compared.",
            "full_feeder_background": "Every ordinary IEEE 123 load remains enabled. A failed terminal asset disables only its designated line and listed capacitor when applicable; a backup source energizes the actual isolated terminal island, including any ordinary downstream feeder demand. Every solve records voltage state for each enabled feeder load.",
            "backup_source": f"A modeled 1-phase 2.402 kV, {BACKUP_CAPACITY_KVA:g} kVA source is placed only behind a disabled terminal line. Each solve checks convergence, all energized feeder-load voltage states, delivered critical kW, source apparent power/current, and zero current on disabled isolation lines.",
            "thermal_boundary": "No line ampacity or thermal conclusion is made because the public IEEE 123 files do not provide a suitable basis for this study to assert real or synthetic ampacities.",
        },
        "synthetic_sitings": mapped_depths,
        "flood_correlated_scenarios": correlated,
        "independent_outage_scenarios": independent,
        "aggregate_results": aggregate_results,
        "campaign_accounting": {"scenario_count": len(all_scenarios), "policy_solves_per_scenario": 33, "expected_solve_count": len(all_scenarios) * 33, "actual_solve_count": SOLVE_COUNT, "retained_backup_policy_result_count": len(retained_backup_results), "infeasible_retained_backup_policy_result_count": len(infeasible_backup_results), "infeasible_backup_results_with_source_limit_violation_count": len(source_limited_backup_results), "retained_hardening_policy_result_count": len(retained_hardening_results), "infeasible_retained_hardening_policy_result_count": len(infeasible_hardening_results)},
        "claim_boundary": [
            "The USGS input is an empirical June 2016 Rainelle flood-depth field. The association of those depths to IEEE 123 assets is synthetic and solely supports a controlled resilience experiment.",
            "This does not represent a West Virginia utility, actual asset locations, real customer criticality, outage fragility, access, protection, crews, costs, fuel, equipment elevation, service connections, or restoration operations.",
            "Because the correlated failure rule and the depth-informed intervention rule both use the assigned depth ranking, any depth-informed advantage is mechanism-aligned evidence rather than independent predictive validation. The result is not a forecast or deployment recommendation.",
        ],
    }
    (OUT / "study.json").write_text(json.dumps(study, indent=2, sort_keys=True) + "\n")
    report = [
        "# Synthetic Flood-Grid Resilience Experiment",
        "",
        "## What this experiment measures",
        "",
        "The experiment couples empirical USGS June 2016 Rainelle flood-depth samples with a public IEEE 123 feeder through disclosed synthetic siting. It compares flood-correlated failures, where the deepest assigned assets fail, with exact uniform independent-failure baselines at the same one through four failed-asset counts.",
        "",
        "Every ordinary IEEE 123 load remains enabled. A terminal failure opens only its designated line and listed capacitor when applicable; a backup energizes the actual isolated terminal island, including downstream ordinary demand. Each policy gets two abstract intervention slots. Depth-informed hardening and backup are compared with all 15 random two-slot assignments in their own policy family. Every retained result solves AC power flow and records every enabled feeder load's voltage state, critical served kW, source checks, and island-boundary checks.",
        "",
        "## Aggregate results",
        "",
    ]
    for count in OUTAGE_COUNTS:
        result = aggregate_results[str(count)]
        corr = result["flood_correlated"]
        ind = result["independent_outage"]
        asset_word = "asset" if count == 1 else "assets"
        report.append(f"- {count} failed synthetic {asset_word}: correlated no action {corr['no_action']['mean_critical_kw_among_feasible_solves']:.2f} kW among {corr['no_action']['feasible_solve_count']}/{corr['no_action']['solve_count']} feasible solves; depth-informed hardening {corr['depth_informed_hardening']['mean_critical_kw_among_feasible_solves']:.2f} kW among {corr['depth_informed_hardening']['feasible_solve_count']}/{corr['depth_informed_hardening']['solve_count']} feasible solves; depth-informed backup unconstrained solved mean {corr['depth_informed_backup']['mean_solved_critical_kw_unconstrained']:.2f} kW and feasible-only mean {corr['depth_informed_backup']['mean_critical_kw_among_feasible_solves']:.2f} kW among {corr['depth_informed_backup']['feasible_solve_count']}/{corr['depth_informed_backup']['solve_count']} feasible solves. Independent-outage no action {ind['no_action']['mean_critical_kw_among_feasible_solves']:.2f} kW among {ind['no_action']['feasible_solve_count']}/{ind['no_action']['solve_count']} feasible solves; hardening {ind['depth_informed_hardening']['mean_critical_kw_among_feasible_solves']:.2f} kW among {ind['depth_informed_hardening']['feasible_solve_count']}/{ind['depth_informed_hardening']['solve_count']} feasible solves; backup unconstrained solved mean {ind['depth_informed_backup']['mean_solved_critical_kw_unconstrained']:.2f} kW and feasible-only mean {ind['depth_informed_backup']['mean_critical_kw_among_feasible_solves']:.2f} kW among {ind['depth_informed_backup']['feasible_solve_count']}/{ind['depth_informed_backup']['solve_count']} feasible solves.")
    report += [
        "",
        "## Boundaries",
        "",
        "The correlated failure rule and the depth-informed policy both use the assigned depth ranking. Any advantage is therefore mechanism-aligned, not independent predictive validation. Backup's unconstrained solved-service values include results that violate stated source constraints, so they are not presented as feasible service. No ampacity, thermal, real-utility, equipment-damage, access, cost, or restoration claim is made. The public feeder supplies electrical equations and the USGS raster supplies an observed flood field; their association is synthetic. See `study.json` for all 11,880 policy solves, every feeder-load voltage record, failure set, constraint check, and input hash.",
        "",
    ]
    (OUT / "REPORT.md").write_text("\n".join(report))
    manifest = {"generator_sha256": digest(Path(__file__)), "files": {path.name: digest(path) for path in (OUT / "study.json", OUT / "REPORT.md")}, "inputs": study["inputs"], "engine": study["engine"]}
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
