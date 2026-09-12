import json
import lzma
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parent
with lzma.open(ROOT/'reference/study.json.xz','rt') as stream:
    study=json.load(stream)
correlated=study['flood_correlated_scenarios']
independent=study['independent_outage_scenarios']
assert len(correlated)==24 and len(independent)==336
scenarios=correlated+independent
policies=('no_action','depth_informed_hardening','depth_informed_backup')
assert all(len(row['policies']['random_two_slot_hardening_cases'])==15 and len(row['policies']['random_two_slot_backup_cases'])==15 for row in scenarios)
checks=0

def compare_summary(results,expected):
    global checks
    all_values=[r['served_critical_kw'] for r in results]
    feasible=[r['served_critical_kw'] for r in results if r['electrically_feasible_under_defined_constraints']]
    actual={
        'solve_count':len(results),
        'feasible_solve_count':len(feasible),
        'feasible_solve_fraction':len(feasible)/len(results),
        'mean_solved_critical_kw_unconstrained':sum(all_values)/len(all_values),
        'min_solved_critical_kw_unconstrained':min(all_values),
        'max_solved_critical_kw_unconstrained':max(all_values),
        'mean_critical_kw_among_feasible_solves':sum(feasible)/len(feasible) if feasible else None,
        'min_critical_kw_among_feasible_solves':min(feasible) if feasible else None,
        'max_critical_kw_among_feasible_solves':max(feasible) if feasible else None,
    }
    assert actual.keys()==expected.keys()
    for key,value in actual.items():
        if value is None:
            assert expected[key] is None,key
        else:
            assert math.isclose(value,expected[key],rel_tol=1e-12,abs_tol=1e-9),key
        checks+=1

for count in range(1,5):
    aggregate=study['aggregate_results'][str(count)]
    for key,rows in [('flood_correlated',correlated),('independent_outage',independent)]:
        selected=[row for row in rows if row['outage_count']==count]
        for policy in policies:
            compare_summary([row['policies'][policy] for row in selected],aggregate[key][policy])
    selected=[row for row in correlated if row['outage_count']==count]
    for family in ['hardening','backup']:
        results=[case['result'] for row in selected for case in row['policies']['random_two_slot_'+family+'_cases']]
        compare_summary(results,aggregate['random_baselines_under_flood_correlated'][family])

family_results={family:[result for row in scenarios for result in [row['policies']['depth_informed_'+family],*[case['result'] for case in row['policies']['random_two_slot_'+family+'_cases']]]] for family in ['hardening','backup']}
assert all(len(results)==5760 for results in family_results.values())
assert sum(not r['electrically_feasible_under_defined_constraints'] for r in family_results['hardening'])==949
assert sum(not r['electrically_feasible_under_defined_constraints'] for r in family_results['backup'])==1575
assert sum(not r['electrically_feasible_under_defined_constraints'] and any(not s['within_defined_source_limits'] for s in r['backup_source_reports']) for r in family_results['backup'])==899
example=next(row for row in correlated if row['seed']==2203 and row['outage_count']==2)
assert example['failed_assets']==['A','D']
backup=example['policies']['depth_informed_backup']
source=next(s for s in backup['backup_source_reports'] if s['source']=='backup_a')
service=next(s for s in backup['service'] if s['asset']=='A')
assert service['served'] and not backup['electrically_feasible_under_defined_constraints']
assert round(backup['served_critical_kw'],2)==181.60
assert round(source['apparent_kva'],2)==67.14
assert round(source['current_a'],2)==28.24
assert round(source['rated_current_a'],2)==24.98
assert round(service['voltage_pu'],3)==0.990
print(json.dumps({'passed':True,'scenarios':len(scenarios),'retained_solves':len(scenarios)*33,'aggregate_numeric_checks':checks,'hardening_infeasible':949,'backup_infeasible':1575,'backup_source_limit_violations':899,'example':{'seed':2203,'failed_assets':['A','D'],'served_critical_kw':backup['served_critical_kw'],'backup_a_kva':source['apparent_kva'],'backup_a_current_a':source['current_a'],'backup_a_rated_current_a':source['rated_current_a'],'asset_a_voltage_pu':service['voltage_pu']}},indent=2))
