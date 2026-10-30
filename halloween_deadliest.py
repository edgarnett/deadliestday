"""Build site data: Oct 31 vs every calendar day, and Halloween by weekday. FARS 2000-2024."""
import sys, zipfile, glob, os, json
import pandas as pd

def read(z, name):
    m = next(n for n in z.namelist() if os.path.basename(n).upper() == name)
    with z.open(m) as f:
        return pd.read_csv(f, encoding="latin-1", low_memory=False)

fr = []
for p in sorted(glob.glob(os.path.join(sys.argv[1], "*.zip"))):
    with zipfile.ZipFile(p) as z:
        acc = read(z, "ACCIDENT.CSV")[["ST_CASE", "YEAR", "MONTH", "DAY"]]
        per = read(z, "PERSON.CSV")[["ST_CASE", "PER_TYP", "INJ_SEV", "AGE"]]
    d = per.merge(acc, on="ST_CASE")
    fr.append(d[(d.PER_TYP == 5) & (d.INJ_SEV == 4)])
d = pd.concat(fr)
d["date"] = pd.to_datetime(dict(year=d.YEAR, month=d.MONTH, day=d.DAY), errors="coerce")
d = d.dropna(subset=["date"])
days = pd.date_range("2000-01-01", "2024-12-31")
tot = d.groupby("date").size().reindex(days, fill_value=0)
kid = d[d.AGE < 18].groupby("date").size().reindex(days, fill_value=0)
df = pd.DataFrame({"all": tot, "kids": kid}, index=days)
df["md"] = df.index.strftime("%m-%d"); df["wd"] = df.index.dayofweek  # Mon=0, Sat=5
df["hal"] = df.md == "10-31"

# calendar-day totals (drop Feb 29 from ranking noise? keep, flag)
cal = df.groupby("md")[["all", "kids"]].sum()
n_years = df.groupby("md").size()
cal["years"] = n_years
print("TOP child days:\n", cal.sort_values("kids", ascending=False).head(6))
print("TOP all-age days:\n", cal.sort_values("all", ascending=False).head(6))
print("median child/day over calendar:", cal.kids.median(), "mean:", cal.kids.mean())

# Halloween by weekday
h = df[df.hal].copy()
h["year"] = h.index.year
names = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
print("\nHalloween by weekday")
wk = []
for w in range(7):
    s = h[h.wd == w]
    base = df[(~df.hal) & (df.wd == w)]
    row = dict(day=names[w], years=list(s.year), n=len(s), kids=int(s.kids.sum()), all=int(s["all"].sum()),
               kids_per=float(s.kids.mean()) if len(s) else None, all_per=float(s["all"].mean()) if len(s) else None,
               base_kids=float(base.kids.mean()), base_all=float(base["all"].mean()))
    wk.append(row); print(row)
sat = h[h.wd == 5]; non = h[h.wd != 5]
print("\nSat Halloweens:", sat[["kids","all"]].to_dict("index"))
print("Sat mean kids %.2f all %.2f | non-Sat mean kids %.2f all %.2f" % (sat.kids.mean(), sat["all"].mean(), non.kids.mean(), non["all"].mean()))
print("Weekend (Fri-Sun) vs weekday Halloween means all:", h[h.wd.isin([4,5,6])]["all"].mean(), h[~h.wd.isin([4,5,6])]["all"].mean())

out = dict(
  cal=[dict(md=k, kids=int(r.kids), all=int(r["all"])) for k, r in cal.iterrows()],
  weekday=wk,
  years=[dict(year=int(y), wd=names[int(r.wd)], kids=int(r.kids), all=int(r["all"])) for y, r in h.set_index("year").iterrows()],
)
json.dump(out, open("site_data.json", "w"))
