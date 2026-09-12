from pathlib import Path
import urllib.request, concurrent.futures, hashlib, json
root=Path(__file__).parent/'data'/'raw'
def fetch(pair):
 name,url=pair
 p=root/name
 if not p.exists():
  with urllib.request.urlopen(url,timeout=60) as r: p.write_bytes(r.read())
 print(name,p.stat().st_size,flush=True)
 return {'file':name,'url':url,'retrieved':'2026-09-12','sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
jobs=[(f'saipe_{y}.txt',f'https://www2.census.gov/programs-surveys/saipe/datasets/{y}/{y}-state-and-county/est{str(y)[2:]}all.txt') for y in range(2015,2025)]
jobs += [('mortgage_rates.csv','https://fred.stlouisfed.org/graph/fredgraph.csv?id=MORTGAGE30US')]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool: manifest=list(pool.map(fetch,jobs))
manifest.append({'file':'County_zhvi.csv','url':'User-provided Zillow County ZHVI export; https://www.zillow.com/research/data/','retrieved':'User attachment recovered 2026-09-12','sha256':hashlib.sha256((root/'County_zhvi.csv').read_bytes()).hexdigest()})
(root.parent/'source_manifest.json').write_text(json.dumps(manifest,indent=2))
