# Flood-Aware Feeder Protection: Served Load and Backup Feasibility

## Abstract

Hardening and backup can restore similar amounts of critical load while producing different numbers of electrically feasible states. We compare the two interventions on an IEEE 123-node feeder with synthetic flood-depth assignments and equal two-asset budgets. With two depth-correlated failures, hardening serves a mean of 181.65 kW and is feasible in all six scenarios. Backup serves an all-solve mean of 181.35 kW but is feasible in only three scenarios. A backup can serve the critical load while exceeding its rating because it also supplies ordinary loads on the islanded branch. Across 360 scenarios and 11,880 AC power-flow solves, we report served-load means with feasible-case counts. We test both depth-correlated and depth-independent failures and retain the load, source and isolation measurements used to assess electrical feasibility.

## Introduction

A backup source can supply a critical load at acceptable voltage while exceeding its own rating. An evaluation based only on restored kW would miss that overload. Hardening and backup change the supply path in different ways: hardening preserves the upstream connection, while backup supplies the loads on the branch isolated by a failure.

We compare these interventions with two protected assets per policy on the IEEE 123-node feeder. Each solve records critical-load service and electrical feasibility. Depth-independent failures provide a comparison in which selecting the deepest assets no longer directly follows the failure rule.

## Experimental Design

### Flood-depth assignments and failures

We draw six depths without replacement from the 319,264 valid 3-m raster cells in the June 2016 Rainelle flood map [1]. We assign them in fixed order to six terminal assets of the IEEE 123-node feeder [2]. Seeds 1103, 2203, 3303, 4403, 5503 and 6603 produce six asset-depth rankings. The depth values come from the observed map; their assignment to feeder assets is synthetic.

For each ranking, depth-correlated failures disconnect the deepest one, two, three or four assets. Depth-independent failures give equal weight to every failure subset of the same size. These rules produce 24 correlated and 336 independent scenarios.

### Intervention policies

Each intervention policy has a two-asset budget. Depth-informed hardening and backup select the two deepest assets. The random-placement comparison enumerates all 15 two-asset assignments. Each scenario has one no-action solve, two depth-informed solves and 30 random-placement solves, giving 33 solves per scenario and 11,880 in total. The budget equates asset counts, not technology costs.

### Electrical model and acceptance criteria

The designated critical loads are A: S84c (20 kW), B: S83c (20 kW), C: S90b (40 kW), D: S92c (40 kW), E: S94a (40 kW) and F: S96b (20 kW), totaling 180 kW nominally. Failure disables the corresponding line, respectively L83, L84, L89, L91, L93 or L95, and its capacitor where present: C83, C90b or C92c. Other feeder loads remain enabled.

Hardening prevents the branch disconnection. Backup adds a single-phase, 2.402-kV source rated at 60 kVA on the isolated side of the disabled line. This source supplies the island in the radial voltage-source power-flow model. Apparent-power and current ratings are acceptance tests on the solved state, so acceptable load voltage alone does not establish that the backup is within its rating.

A state is electrically feasible when the solve converges, every energized feeder-load bus is within 0.95–1.05 pu, every critical load intended to remain supplied meets its service requirement, each backup is within its ratings, and each disabled isolation line has zero current. Intended service covers assets that have not failed or have hardening or backup. A critical load counts as served when its voltage is in band and its delivered real power is at least 99% of nominal demand. Deenergized loads are recorded separately.

### Service metrics

Let P_j be the sum of actual solved real power delivered to served critical loads in result j, and let F_j = 1 when that complete state is feasible. For N cases, the all-solve mean is sum(P_j)/N and the feasible-only mean is sum(F_j P_j)/sum(F_j). We report feasible and total case counts with each feasible-only mean. Because P_j uses solved power, it can slightly exceed the 180-kW nominal critical demand.

## Results

### Flood-correlated failures

| Policy / failed assets | 1 | 2 | 3 | 4 |
|---|---:|---:|---:|---:|
| No action | 145.26 (5/6) | 125.67 (5/6) | 93.33 (5/6) | 67.84 (6/6) |
| Depth hardening | 181.65 (6/6) | 181.65 (6/6) | 149.56 (5/6) | 124.68 (6/6) |
| Depth backup | 181.21 (5/6) | 181.65 (3/6) | 151.19 (4/6) | 126.24 (4/6) |
| All-solve mean | 181.29 | 181.35 | 151.36 | 124.47 |
| Random hardening | 158.91 (80/90) | 143.64 (76/90) | 124.05 (78/90) | 107.53 (73/90) |
| Random backup | 157.24 (75/90) | 142.28 (65/90) | 120.95 (65/90) | 105.14 (60/90) |
| All-solve mean | 159.09 | 143.60 | 123.61 | 105.59 |

Values are feasible-only mean served critical load in kW (feasible / all solves). All-solve rows include infeasible results. Feasible subsets differ across policies.

Table I reports the correlated cases. Each column gives a failure count from one to four. Each depth-informed policy is evaluated over six depth assignments; each random-placement policy is evaluated over 90 assignment-placement combinations.

With two failed assets, depth hardening is feasible in all six cases and serves a mean of 181.65 kW. Depth backup has an all-solve mean of 181.35 kW, only 0.30 kW lower, but is feasible in three of six cases. Its feasible-only mean is 181.65 kW because that average includes only the three accepted states. Either mean alone would hide the difference in feasible-case counts.

With four correlated failures, depth hardening is feasible in six cases and has a mean of 124.68 kW. Depth backup is feasible in four cases and has a feasible-only mean of 126.24 kW. No action produces 67.84 kW in all six feasible cases. Random hardening has a feasible-only mean of 107.53 kW across 73 of 90 feasible cases; random backup has a mean of 105.14 kW across 60 of 90.

### Served load with an overloaded backup

In the correlated scenario with seed 2203 and failed assets A and D, depth backup serves 181.60 kW across the critical loads. Asset A's 20-kW load is served at 0.990 pu. Its backup supplies 67.14 kVA and 28.24 A, exceeding the 60-kVA and 24.98-A limits.

Opening L83 isolates the branch containing buses 84 and 85. The backup at bus 84 supplies critical load S84c (20 kW, 10 kvar) and ordinary downstream load S85c (40 kW, 20 kvar). Their combined nominal demand is 60 kW and 30 kvar, or 67.08 kVA. Sizing the backup against the critical load alone omits demand connected to the same island. This case therefore contributes restored critical kW to the all-solve mean even though its backup is overloaded.

### Depth-independent failures

| Policy / failed assets | 1 | 2 | 3 | 4 |
|---|---:|---:|---:|---:|
| No action | 149.27 (30/36) | 124.56 (72/90) | 90.11 (102/120) | 62.05 (84/90) |
| Depth hardening | 160.74 (32/36) | 141.20 (74/90) | 119.98 (98/120) | 98.66 (77/90) |
| Depth backup | 159.26 (30/36) | 140.88 (62/90) | 116.13 (88/120) | 98.38 (64/90) |
| All-solve mean | 160.77 | 139.97 | 119.17 | 98.33 |

Values are feasible-only mean served critical load in kW (feasible / all solves). All-solve rows include infeasible results. Feasible subsets differ across policies.

Table II uses the same six depth assignments as Table I and tests every failure subset of one through four assets independently of depth. The one-, two-, three- and four-failure cases contain 36, 90, 120 and 90 scenarios, respectively.

With two failed assets, depth hardening has 74 feasible cases and a feasible-only mean of 141.20 kW. Depth backup has 62 feasible cases and a feasible-only mean of 140.88 kW. No action has 72 feasible cases and a feasible-only mean of 124.56 kW. Each policy is evaluated over the same 90 scenarios.

A feasible-only mean averages P_j conditional on F_j = 1 under that policy. Different policies can accept different subsets, so differences between their feasible-only means do not measure paired gains over the same cases. Reporting counts shows how much of the tested set each mean represents. The full records retain common scenario identifiers for comparisons on matching failure sets.

### Constraint outcomes across the campaign

Each intervention family has 5,760 results: one depth-informed placement and 15 random placements across 360 scenarios. Hardening has 949 infeasible results (16.5%), and backup has 1,575 (27.3%). Among the infeasible backup results, 899 violate an apparent-power or current limit. Source limits are not the only cause of rejection, and constraint categories may overlap. The records include load voltages, critical-load service, backup-source measurements and island-boundary currents. The worked example shows the network path and connected demand behind one source overload.

## Discussion

The correlated design favors depth-informed placement because the failure and intervention rules use the same depth ranking. Independent failures separate this placement effect from electrical acceptance. Both comparisons require checking whether restored service belongs to a feasible state.

Hardening preserves the upstream connection; backup supplies island loads. In the worked branch, the 60-kVA source exceeds the critical load's nominal apparent demand of 22.36 kVA but falls below the combined critical and ordinary demand of 67.08 kVA. Connected island demand is therefore the relevant sizing quantity.

Similar served-load means do not make the interventions interchangeable. With two correlated failures, similar all-solve means accompany a twofold difference in feasible-case counts. With four failures, backup has a higher feasible-only mean but fewer feasible states. Reporting the mean and feasible-case count preserves this distinction and keeps rejected states visible.

## Reproducibility

The public reproduction package [3] contains simulation and report sources, feeder inputs, the flood raster, Python dependencies, execution instructions, the complete result file and a standard-library integrity checker. Full results are also available as losslessly compressed JSON [4], including all 11,880 solves, per-load voltage records, source and isolation checks, failure sets and input hashes.

The check_results.py script recomputes 288 aggregate values and counts from the retained solves and checks the seed-2203 example. Published reference outputs are stored separately from newly generated outputs. The package provides reproduction commands, engine versions and file hashes.

## References

[1] U.S. Geological Survey, June 2016 Rainelle flood-map data release. https://doi.org/10.5066/F76T0K4K [2] EPRI OpenDSS, IEEE 123-node test feeder, maintained in the DSS-Extensions examples repository. https://github.com/dss-extensions/electricdss-tst [3] Flood-grid experiment: complete source, inputs, environment and reproduction instructions. https://dhruvs.vercel.app/research/flood-grid/reproducibility.zip [4] Flood-grid experiment: complete retained results, 360 scenarios and 11,880 solves. https://dhruvs.vercel.app/research/flood-grid/files/reference/study.json.xz
