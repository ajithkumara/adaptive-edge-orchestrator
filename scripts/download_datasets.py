import urllib.request, os, hashlib, json
from pathlib import Path
from datetime import datetime, timezone

Path("/app/data/cwru").mkdir(parents=True, exist_ok=True)
Path("/app/data/skab").mkdir(parents=True, exist_ok=True)

CWRU_FILES = {
    "normal_0hp.mat":     "https://engineering.case.edu/sites/default/files/97.mat",
    "ball_0hp.mat":       "https://engineering.case.edu/sites/default/files/118.mat",
    "inner_race_0hp.mat": "https://engineering.case.edu/sites/default/files/105.mat",
    "outer_race_0hp.mat": "https://engineering.case.edu/sites/default/files/130.mat",
    "normal_1hp.mat":     "https://engineering.case.edu/sites/default/files/98.mat",
    "ball_1hp.mat":       "https://engineering.case.edu/sites/default/files/119.mat",
    "inner_race_1hp.mat": "https://engineering.case.edu/sites/default/files/106.mat",
    "outer_race_1hp.mat": "https://engineering.case.edu/sites/default/files/131.mat",
}

SKAB_BASE = "https://raw.githubusercontent.com/waico/SKAB/master/data/valve1/"
SKAB_FILES = {
    "skab_valve1_0.csv": f"{SKAB_BASE}0.csv",
    "skab_valve1_1.csv": f"{SKAB_BASE}1.csv",
    "skab_valve1_2.csv": f"{SKAB_BASE}2.csv",
    "skab_valve1_3.csv": f"{SKAB_BASE}3.csv",
    "skab_valve1_4.csv": f"{SKAB_BASE}4.csv",
}

def download(url, dest):
    if Path(dest).exists() and Path(dest).stat().st_size > 1000:
        sha = hashlib.sha256(open(dest,"rb").read()).hexdigest()[:12]
        print(f"  {Path(dest).name}... SKIP (already exists  sha256={sha})")
        return Path(dest).stat().st_size, sha
    print(f"  {Path(dest).name}...", end=" ", flush=True)
    try:
        urllib.request.urlretrieve(url, dest)
        size = os.path.getsize(dest)
        sha  = hashlib.sha256(open(dest,"rb").read()).hexdigest()[:12]
        print(f"OK  {size//1024}KB  sha256={sha}")
        return size, sha
    except Exception as e:
        print(f"FAILED: {e}")
        return 0, ""

manifest = {"cwru": {}, "skab": {}}

print("\n=== Downloading CWRU ===")
for fname, url in CWRU_FILES.items():
    size, sha = download(url, f"/app/data/cwru/{fname}")
    manifest["cwru"][fname] = {"url": url, "sha256": sha, "bytes": size}

print("\n=== Downloading SKAB ===")
for fname, url in SKAB_FILES.items():
    size, sha = download(url, f"/app/data/skab/{fname}")
    manifest["skab"][fname] = {"url": url, "sha256": sha, "bytes": size}

manifest["random_state"] = 42
manifest["cwru_fault_types"] = ["normal","ball","inner_race","outer_race"]
manifest["downloaded_at"] = datetime.now(timezone.utc).isoformat()

with open("/app/config/datasets.json","w") as f:
    json.dump(manifest, f, indent=2)

cwru_ok = sum(1 for v in manifest["cwru"].values() if v["bytes"] > 0)
skab_ok = sum(1 for v in manifest["skab"].values() if v["bytes"] > 0)
print(f"\nCWRU: {cwru_ok}/{len(CWRU_FILES)} files OK")
print(f"SKAB: {skab_ok}/{len(SKAB_FILES)} files OK")
print("datasets.json saved ✔")
print("Next run will SKIP already-downloaded files.")
