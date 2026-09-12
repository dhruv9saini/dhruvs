import hashlib
import json
import lzma
from pathlib import Path

ROOT=Path(__file__).resolve().parent

def digest(path):
    value=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):
            value.update(block)
    return value.hexdigest()

manifest=json.loads((ROOT/'ARTIFACTS.json').read_text())
for item in manifest['files']:
    path=ROOT/item['path']
    assert path.is_file(),item['path']
    assert path.stat().st_size==item['bytes'],item['path']
    assert digest(path)==item['sha256'],item['path']
study=json.loads((ROOT/'reference/manifest.json').read_text())
assert digest(ROOT/'run_synthetic_flood_grid_resilience.py')==study['generator_sha256']
assert digest(ROOT/'data/Meadow_Sewell_dem_derived.zip')==study['inputs']['depth_zip_sha256']
for path,expected in study['inputs']['native_dss_dependencies'].items():
    assert digest(ROOT/path)==expected,path
expected=json.loads((ROOT/'reference/uncompressed_data.json').read_text())
data_hash=hashlib.sha256()
data_bytes=0
with lzma.open(ROOT/'reference/study.json.xz','rb') as stream:
    for block in iter(lambda:stream.read(1024*1024),b''):
        data_hash.update(block)
        data_bytes+=len(block)
assert data_hash.hexdigest()==expected['sha256']==study['files']['study.json']
assert data_bytes==expected['bytes']
empirical=json.loads((ROOT/'reference/public_exposure_v1/manifest.json').read_text())
assert digest(ROOT/'run_public_exposure_study.py')==empirical['generator_sha256']
assert digest(ROOT/'data_v2/greenbrier_essential_facilities_with_geometry.geojson')==empirical['inputs']['facility_geometry']
assert digest(ROOT/'data/Meadow_Sewell_dem_derived.zip')==empirical['inputs']['depth_release_zip']
for path,expected_hash in empirical['files'].items():
    assert digest(ROOT/'reference/public_exposure_v1'/path)==expected_hash,path
print(json.dumps({'passed':True,'verified_files':len(manifest['files']),'uncompressed_result_bytes':data_bytes,'result_sha256':data_hash.hexdigest(),'original_simulation_and_empirical_input_bindings_exact':True},indent=2))
