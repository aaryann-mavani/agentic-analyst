"""PROTOTYPE: download the public data and build data/*.csv. Data files are NOT committed (public repo; licences differ).
Run: python3 prototypes/kpi-qa-PROTOTYPE/tools/fetch_data.py
Sources: Time-MMD (GitHub, pinned commit), Basel open data API, City of Zurich open data, BFE open data. No API key needed.
Terms: BFE data requires attribution and asking permission for commercial use; Basel terms not yet checked; Time-MMD has no licence file.
See docs/research/swiss-open-data.md."""
import os, subprocess, sys, tempfile, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__)); DATA = os.path.join(HERE, "..", "data")
COMMIT = "00281e2d86058286d5548b15a7670e8eda57ef62"
TIMEMMD = ["Economy", "Energy", "Traffic", "Agriculture"]
SWISS = [  # name, url   (order matters: prepare_swiss.py reads them in this order)
 ("basel_monthly.csv", "https://data.bs.ch/api/explore/v2.1/catalog/datasets/100107/exports/csv?delimiter=%2C"),
 ("basel_daily_rooms.csv", "https://data.bs.ch/api/explore/v2.1/catalog/datasets/100106/exports/csv?delimiter=%2C"),
 ("zh_pedestrians.csv", "https://data.stadt-zuerich.ch/dataset/hystreet_fussgaengerfrequenzen/download/hystreet_fussgaengerfrequenzen_seit2021.csv"),
 ("bfe_consumption.csv", "https://www.bfe-ogd.ch/ogd103_stromverbrauch_swissgrid_lv_und_endv.csv"),
 ("bfe_price.csv", "https://www.bfe-ogd.ch/ogd106_preise_strom_boerse.csv")]

def get(url, dest):
    req = urllib.request.Request(url, headers={"User-Agent": "student-project-client"})
    with urllib.request.urlopen(req, timeout=180) as r, open(dest, "wb") as f: f.write(r.read())
    print("downloaded", os.path.basename(dest), os.path.getsize(dest), "bytes")

os.makedirs(DATA, exist_ok=True)
for d in TIMEMMD:
    get(f"https://raw.githubusercontent.com/AdityaLab/Time-MMD/{COMMIT}/numerical/{d}/{d}.csv", os.path.join(DATA, f"{d}.csv"))
paths = []
for name, url in SWISS:   # each download goes in its own new directory; raw files are treated as untrusted data
    d = tempfile.mkdtemp(); p = os.path.join(d, name); get(url, p); paths.append(p)
lst = os.path.join(tempfile.mkdtemp(), "paths.txt"); open(lst, "w").write("\n".join(paths) + "\n")
subprocess.run([sys.executable, "-I", os.path.join(HERE, "prepare_swiss.py"), lst], check=True)
