"""All road fatalities by day + Halloween pedestrian map points. FARS 2000-2024. Usage: python halloween_all.py folder_with_zips"""
import sys, zipfile, glob, os, json
import pandas as pd

def read(z, name, cols):
    m = next(n for n in z.namelist() if os.path.basename(n).upper() == name)
    with z.open(m) as f:
        df = pd.read_csv(f, encoding="latin-1", low_memory=False, usecols=lambda c: c.upper() in cols)
        df.columns = [c.upper() for c in df.columns]
        return df

fr, pts = [], []
for p in sorted(glob.glob(os.path.join(sys.argv[1], "*.zip"))):
    with zipfile.ZipFile(p) as z:
        acc = read(z, "ACCIDENT.CSV", ["ST_CASE", "YEAR", "MONTH", "DAY", "HOUR", "STATE", "LATITUDE", "LONGITUD"])
        per = read(z, "PERSON.CSV", ["ST_CASE", "PER_TYP", "INJ_SEV", "AGE"])
    d = per[per.INJ_SEV == 4].merge(acc, on="ST_CASE")
    fr.append(d)
d = pd.concat(fr)
d["date"] = pd.to_datetime(dict(year=d.YEAR, month=d.MONTH, day=d.DAY), errors="coerce")
d = d.dropna(subset=["date"])
d["md"] = d.date.dt.strftime("%m-%d")
d["kid"] = d.AGE < 18
d["eve"] = d.HOUR.between(18, 23)
days = pd.date_range("2000-01-01", "2024-12-31")
n_days = len(days)

tot = d.groupby("md").size(); kid = d[d.kid].groupby("md").size()
ped = d[d.PER_TYP == 5].groupby("md").size()
cal = pd.DataFrame({"all": tot, "kids": kid, "ped": ped}).fillna(0).astype(int)
print("All road deaths: Oct31 =", cal.loc["10-31", "all"], "rank", int(cal["all"].rank(ascending=False, method="min")["10-31"]),
      "| top:", cal["all"].sort_values(ascending=False).head(5).to_dict())
print("Child road deaths (<18) Oct31 =", cal.loc["10-31", "kids"], "rank", int(cal["kids"].rank(ascending=False, method="min")["10-31"]),
      "| top:", cal["kids"].sort_values(ascending=False).head(4).to_dict())
mean_other = cal.drop("10-31")
print("mean/day all:", mean_other["all"].mean(), " Oct31 mean/yr:", cal.loc["10-31","all"]/25, "ratio", cal.loc["10-31","all"]/25/(mean_other["all"].sum()/ (n_days-25)))
print("kids ratio:", cal.loc["10-31","kids"]/25/(mean_other["kids"].sum()/(n_days-25)))
ev = d[d.eve]
evc = ev.groupby("md").size(); evk = ev[ev.kid].groupby("md").size()
print("Evening all: Oct31", evc["10-31"], "rank", int(evc.rank(ascending=False, method="min")["10-31"]), "other mean/day", (evc.sum()-evc["10-31"])/(n_days-25)/1, "-> ratio", evc["10-31"]/25/((evc.sum()-evc["10-31"])/(n_days-25)))
print("Evening kids: Oct31", evk["10-31"], "rank", int(evk.rank(ascending=False, method="min")["10-31"]))
# by person type on Halloween
h = d[d.md == "10-31"]
names = {1: "Driver", 2: "Passenger", 3: "Passenger", 4: "Other occupant", 5: "Pedestrian", 6: "Bicyclist", 7: "Other cyclist", 8: "Other non-occ", 9: "Unknown", 10: "Other non-occ", 19: "Unknown"}
print(h.PER_TYP.map(names).value_counts().to_dict())
# Halloween kids per type
print("kids by type:", h[h.kid].PER_TYP.map(names).value_counts().to_dict())
by_year = h.groupby("YEAR").size().to_dict(); by_year_k = h[h.kid].groupby("YEAR").size().to_dict()
# map points: Halloween pedestrians
hp = h[h.PER_TYP == 5].copy()
bad = ~hp.LATITUDE.between(18, 72) | ~hp.LONGITUD.between(-180, -60)
print("ped Halloween:", len(hp), "bad coords:", int(bad.sum()))
hp = hp[~bad]
pts = [dict(lat=round(float(r.LATITUDE), 3), lon=round(float(r.LONGITUD), 3), year=int(r.YEAR), kid=bool(r.kid), age=int(r.AGE) if r.AGE < 120 else None, hour=int(r.HOUR) if r.HOUR < 24 else None) for r in hp.itertuples()]
out = dict(cal=[dict(md=k, all=int(r["all"]), kids=int(r.kids), ped=int(r.ped)) for k, r in cal.iterrows()], pts=pts,
           types=h.PER_TYP.map(names).value_counts().to_dict(), by_year=by_year, by_year_k=by_year_k, n_days=n_days)
json.dump(out, open("site_data_all.json", "w"))
