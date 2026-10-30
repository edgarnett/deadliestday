"""Road deaths by user type per year, FARS 2000-2024. Usage: python road_types.py folder_with_zips -> road_types.json"""
import sys, zipfile, glob, os, json
import pandas as pd

def read(z, name, cols):
    m = next(n for n in z.namelist() if os.path.basename(n).upper() == name)
    with z.open(m) as f:
        df = pd.read_csv(f, encoding="latin-1", low_memory=False, usecols=lambda c: c.upper() in cols)
    df.columns = [c.upper() for c in df.columns]
    return df

CATS = ["Drivers", "Passengers", "Motorcyclists", "Pedestrians", "Bicyclists", "Other / unknown"]
rows = {}
for p in sorted(glob.glob(os.path.join(sys.argv[1], "*.zip"))):
    with zipfile.ZipFile(p) as z:
        per = read(z, "PERSON.CSV", {"ST_CASE", "VEH_NO", "PER_TYP", "INJ_SEV", "YEAR"})
        veh = read(z, "VEHICLE.CSV", {"ST_CASE", "VEH_NO", "BODY_TYP"})
    year = int(per.YEAR.iloc[0]) if "YEAR" in per else int(os.path.basename(p)[4:8])
    per = per[per.INJ_SEV == 4].merge(veh.drop_duplicates(["ST_CASE", "VEH_NO"]), on=["ST_CASE", "VEH_NO"], how="left")
    moto = per.BODY_TYP.between(80, 89)
    def cat(r):
        return None
    t = per.PER_TYP
    c = pd.Series("Other / unknown", index=per.index)
    c[t == 5] = "Pedestrians"
    c[t.isin([6, 7])] = "Bicyclists"
    c[t.isin([1, 2]) & ~moto] = c[t.isin([1, 2]) & ~moto].index.map(lambda i: "Drivers" if t[i] == 1 else "Passengers")
    c[t.isin([1, 2]) & moto] = "Motorcyclists"
    rows[year] = c.value_counts().reindex(CATS, fill_value=0).astype(int).to_dict()
    print(year, sum(rows[year].values()), rows[year])
json.dump(dict(cats=CATS, years={str(y): rows[y] for y in sorted(rows)}), open("road_types.json", "w"))
