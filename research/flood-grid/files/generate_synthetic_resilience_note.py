from __future__ import annotations

import hashlib
import html
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "synthetic_flood_grid_v1"


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def summary_row(count: str, result: dict) -> str:
    flood = result["flood_correlated"]
    random = result["random_baselines_under_flood_correlated"]
    def feasible(item: dict) -> str:
        value = item["mean_critical_kw_among_feasible_solves"]
        text = "none" if value is None else f"{value:.2f}"
        return f"{text} ({item['feasible_solve_count']}/{item['solve_count']})"
    def backup(item: dict) -> str:
        feasible_value = item["mean_critical_kw_among_feasible_solves"]
        feasible_text = "none" if feasible_value is None else f"{feasible_value:.2f}"
        return f"{item['mean_solved_critical_kw_unconstrained']:.2f} / {feasible_text} ({item['feasible_solve_count']}/{item['solve_count']})"
    return (
        f"<tr><td>{count}</td>"
        f"<td>{feasible(flood['no_action'])}</td>"
        f"<td>{feasible(flood['depth_informed_hardening'])}</td>"
        f"<td>{backup(flood['depth_informed_backup'])}</td>"
        f"<td>{feasible(random['hardening'])}</td>"
        f"<td>{backup(random['backup'])}</td></tr>"
    )


def conditional_row(count: str, result: dict) -> str:
    def feasible(item: dict) -> str:
        value = item["mean_critical_kw_among_feasible_solves"]
        text = "none" if value is None else f"{value:.2f}"
        return f"{text} ({item['feasible_solve_count']}/{item['solve_count']})"
    def backup(item: dict) -> str:
        feasible_value = item["mean_critical_kw_among_feasible_solves"]
        feasible_text = "none" if feasible_value is None else f"{feasible_value:.2f}"
        return f"{item['mean_solved_critical_kw_unconstrained']:.2f} / {feasible_text} ({item['feasible_solve_count']}/{item['solve_count']})"
    independent = result["independent_outage"]
    return f"<tr><td>{count}</td><td>{feasible(independent['no_action'])}</td><td>{feasible(independent['depth_informed_hardening'])}</td><td>{backup(independent['depth_informed_backup'])}</td></tr>"


def pdf_text(value: str) -> str:
    return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def write_pdf(path: Path, lines: list[str]) -> None:
    commands = ["BT", "/F1 12 Tf", "56 744 Td", "16 TL"]
    for index, line in enumerate(lines):
        if index:
            commands.append("T*")
        commands.append(f"({pdf_text(line)}) Tj")
    commands.append("ET")
    stream = "\n".join(commands).encode("ascii")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream",
    ]
    output = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for index, item in enumerate(objects, 1):
        offsets.append(len(output))
        output.extend(f"{index} 0 obj\n".encode("ascii"))
        output.extend(item)
        output.extend(b"\nendobj\n")
    startxref = len(output)
    output.extend(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode("ascii"))
    output.extend(b"".join(f"{offset:010d} 00000 n \n".encode("ascii") for offset in offsets[1:]))
    output.extend(f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{startxref}\n%%EOF\n".encode("ascii"))
    path.write_bytes(output)


def main() -> None:
    study_path = OUT / "study.json"
    manifest_path = OUT / "manifest.json"
    study = json.loads(study_path.read_text())
    rows = "".join(summary_row(count, study["aggregate_results"][count]) for count in ("1", "2", "3", "4"))
    independent_rows = "".join(conditional_row(count, study["aggregate_results"][count]) for count in ("1", "2", "3", "4"))
    all_rows = study["flood_correlated_scenarios"] + study["independent_outage_scenarios"]
    backup_cases = [
        result
        for row in all_rows
        for result in [row["policies"]["depth_informed_backup"], *[case["result"] for case in row["policies"]["random_two_slot_backup_cases"]]]
    ]
    accounting = study["campaign_accounting"]
    assert len(backup_cases) == accounting["retained_backup_policy_result_count"]
    source_limited = sum(
        not result["electrically_feasible_under_defined_constraints"]
        and any(not item["within_defined_source_limits"] for item in result["backup_source_reports"])
        for result in backup_cases
    )
    source_limited_total = sum(not result["electrically_feasible_under_defined_constraints"] for result in backup_cases)
    assert source_limited_total == accounting["infeasible_retained_backup_policy_result_count"]
    assert source_limited == accounting["infeasible_backup_results_with_source_limit_violation_count"]
    hardening_cases = [
        result
        for row in all_rows
        for result in [row["policies"]["depth_informed_hardening"], *[case["result"] for case in row["policies"]["random_two_slot_hardening_cases"]]]
    ]
    hardening_infeasible = sum(not result["electrically_feasible_under_defined_constraints"] for result in hardening_cases)
    assert len(hardening_cases) == accounting["retained_hardening_policy_result_count"]
    assert hardening_infeasible == accounting["infeasible_retained_hardening_policy_result_count"]
    title = "Synthetic Flood-Grid Resilience Experiment"
    design = study["design"]
    html_note = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{title}</title><style>body{{font:16px Arial,sans-serif;line-height:1.5;color:#172033;max-width:1080px;margin:32px auto;padding:0 24px}}h1{{font-size:30px;margin-bottom:4px}}h2{{margin-top:30px}}.muted{{color:#52606d}}table{{border-collapse:collapse;width:100%;margin:14px 0}}th,td{{border:1px solid #c8d0d8;padding:8px;text-align:right}}th:first-child,td:first-child{{text-align:left}}th{{background:#edf2f7}}a{{color:#075985}}</style></head><body><h1>{title}</h1><p class="muted">Complete deterministic 11,880-solve AC power-flow campaign. Generated {html.escape(study['created_at_utc'])}.</p><h2>Empirical Rainelle event context</h2><p>The public USGS June 2016 Rainelle flood-depth raster sampled 6.925 ft at a public Fire Department point and 0.915 ft at a public Police Department point. Those observed point samples establish event context only. They are not mapped to the IEEE 123 feeder, the synthetic terminal assets, a real utility, or the simulated outage mechanism.</p><p><a href="https://doi.org/10.5066/F76T0K4K">USGS Rainelle flood-map data release</a> provides the empirical depth field used to construct the disclosed synthetic depth assignments below.</p><h2>Question and experiment</h2><p>{html.escape(study['research_question'])}</p><p>{html.escape(design['synthetic_siting'])}</p><p>{html.escape(design['flood_correlated_outage'])}</p><p>{html.escape(design['full_feeder_background'])}</p><h2>Flood-correlated results</h2><p>All values are mean served designated critical load in kW across six fixed synthetic sitings. A feasible value includes only solves satisfying every stated constraint. Backup cells show <em>unconstrained solved mean / feasible-only mean (feasible solves / all solves)</em>; unconstrained results are not claimed as feasible service. Feasible-only means are conditional summaries of the selected feasible subset, so they are not unconditional policy-performance estimates and should not be compared without their denominators. Each random comparison enumerates all 15 two-slot assignments.</p><table><tr><th>Failed assets</th><th>No action feasible</th><th>Depth hardening feasible</th><th>Depth backup: unconstrained / feasible</th><th>Random hardening feasible</th><th>Random backup: unconstrained / feasible</th></tr>{rows}</table><h2>Independent-outage comparison</h2><p>For the same six synthetic sitings and outage count, every combination of failed assets is evaluated. This comparison does not rank failure by assigned depth. Values use the same feasible-only and backup labeling as the flood-correlated table.</p><table><tr><th>Failed assets</th><th>No action feasible</th><th>Depth hardening feasible</th><th>Depth backup: unconstrained / feasible</th></tr>{independent_rows}</table><h2>Observed constraints and adverse outcomes</h2><p>The retained hardening-policy denominator is {len(hardening_cases)} results, of which {hardening_infeasible} were infeasible. The retained backup-policy denominator is {len(backup_cases)} results: one depth-informed backup plus 15 random backup assignments for each of {len(all_rows)} scenarios. {source_limited_total} backup results were infeasible. Constraint categories overlap: {source_limited} had a modeled source apparent-power or current limit violation, and voltage-band failures are retained separately in the machine-readable result. These retained outcomes are part of the result, not discarded cases. The study records the minimum and maximum bus-voltage values for every enabled IEEE 123 load in every solve.</p><p>{html.escape(design['thermal_boundary'])}</p><h2>What the result supports</h2><p>{html.escape(study['claim_boundary'][0])}</p><p>{html.escape(study['claim_boundary'][2])}</p><h2>Reproducibility</h2><p>The campaign contains {study['campaign_accounting']['scenario_count']} scenarios and {study['campaign_accounting']['actual_solve_count']} AC solves. The four native IEEE 123 dependency hashes, random-policy results, per-load voltage records, source checks, isolation checks, and generator binding are in <a href="study.json">study.json</a> and <a href="manifest.json">manifest.json</a>. The concise machine-readable report is <a href="REPORT.md">REPORT.md</a>. <a href="source.html">Source view</a> contains both generators and links to the four hosted native IEEE 123 inputs; the empirical raster remains available from the linked USGS release.</p></body></html>'''
    (OUT / "research_note.html").write_text(html_note)
    svg_rows = "".join(
        f'<text x="56" y="{248 + i * 31}" class="body">{count} failed: no action feasible {study["aggregate_results"][count]["flood_correlated"]["no_action"]["mean_critical_kw_among_feasible_solves"]:.1f}; hardening feasible {study["aggregate_results"][count]["flood_correlated"]["depth_informed_hardening"]["mean_critical_kw_among_feasible_solves"]:.1f}; backup unconstrained {study["aggregate_results"][count]["flood_correlated"]["depth_informed_backup"]["mean_solved_critical_kw_unconstrained"]:.1f} kW</text>'
        for i, count in enumerate(("1", "2", "3", "4"))
    )
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="792" height="612" viewBox="0 0 792 612"><style>.title{{font:700 25px sans-serif;fill:#172033}}.heading{{font:700 15px sans-serif;fill:#172033}}.body{{font:13px sans-serif;fill:#172033}}.small{{font:11px sans-serif;fill:#52606d}}</style><rect width="792" height="612" fill="white"/><text x="56" y="56" class="title">Synthetic Flood-Grid Resilience Experiment</text><text x="56" y="82" class="small">Complete deterministic experiment: 360 scenarios and 11,880 AC power-flow solves</text><text x="56" y="126" class="heading">Design</text><text x="56" y="150" class="body">Six synthetic IEEE 123 terminal assets receive empirical Rainelle depth samples in six fixed sitings.</text><text x="56" y="172" class="body">Flood-correlated failures select the deepest assets; each policy receives two intervention slots.</text><text x="56" y="194" class="body">Every ordinary feeder load remains enabled and every solve retains minimum and maximum load voltage.</text><text x="56" y="232" class="heading">Flood-correlated means: feasible no action/hardening; unconstrained backup</text>{svg_rows}<text x="56" y="402" class="heading">Limits and interpretation</text><text x="56" y="426" class="body">Hardening had {hardening_infeasible} infeasible results among {len(hardening_cases)} retained policy results. Backup had {source_limited_total} among {len(backup_cases)},</text><text x="56" y="446" class="body">including {source_limited} source-limit violations; voltage-band failures are retained separately. Unconstrained backup service is not feasible service.</text><text x="56" y="486" class="body">The depth-ranked failure rule and depth-informed policy are aligned by design. This is a controlled mechanism test,</text><text x="56" y="506" class="body">not predictive validation, a utility study, or a deployment recommendation.</text><text x="56" y="552" class="small">USGS Rainelle flood depth: https://doi.org/10.5066/F76T0K4K. See study.json and manifest.json for retained results and hashes.</text></svg>'''
    svg_path = OUT / "research_note.svg"
    svg_path.write_text(svg)
    pdf_lines = [
        title,
        "Complete deterministic experiment: 360 scenarios and 11,880 AC power-flow solves.",
        "",
        "Design",
        "Six synthetic IEEE 123 terminal assets receive empirical Rainelle depth samples in six fixed sitings.",
        "Flood-correlated failures select the deepest assets; every policy has two intervention slots.",
        "Every ordinary feeder load remains enabled and every solve retains its load-voltage state.",
        "",
        "Flood-correlated mean served designated critical load (kW)",
        *[
            f"{count} failed: no action feasible {study['aggregate_results'][count]['flood_correlated']['no_action']['mean_critical_kw_among_feasible_solves']:.1f}; hardening feasible {study['aggregate_results'][count]['flood_correlated']['depth_informed_hardening']['mean_critical_kw_among_feasible_solves']:.1f}; backup unconstrained {study['aggregate_results'][count]['flood_correlated']['depth_informed_backup']['mean_solved_critical_kw_unconstrained']:.1f}."
            for count in ("1", "2", "3", "4")
        ],
        "",
        "Limits and interpretation",
        f"Hardening had {hardening_infeasible} infeasible results among {len(hardening_cases)} retained policy results. Backup had {source_limited_total} infeasible results among {len(backup_cases)} retained policy results.",
        f"The backup set includes {source_limited} source-limit violations; voltage-band failures are retained separately. Unconstrained backup service is not feasible service.",
        "The depth-ranked failure rule and depth-informed policy are aligned by design. This is a controlled mechanism test,",
        "not predictive validation, a utility study, or a deployment recommendation.",
        "",
        "USGS Rainelle flood depth: https://doi.org/10.5066/F76T0K4K",
        "See study.json and manifest.json for retained results and hashes.",
    ]
    write_pdf(OUT / "research_note.pdf", pdf_lines)
    delivery_manifest = {
        "generator_sha256": digest(Path(__file__)),
        "study_sha256": digest(study_path),
        "study_manifest_sha256": digest(manifest_path),
        "delivery_files": {name: digest(OUT / name) for name in ("research_note.html", "research_note.svg", "research_note.pdf")},
        "campaign_accounting": study["campaign_accounting"],
    }
    (OUT / "delivery_manifest.json").write_text(json.dumps(delivery_manifest, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
