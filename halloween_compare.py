"""Oct 31 pedestrian deaths vs other days, FARS 2000-2024. Usage: python halloween_compare.py folder_with_zips"""
import sys, zipfile, glob, os
import pandas as pd

def read(z, name):
    m = next(n for n in z.namelist() if os.path.basename(n).upper() == name)
    with z.open(m) as f:
        return pd.read_csv(f, encoding="latin-1", low_memory=False)

frames = []
for p in sorted(glob.glob(os.path.join(sys.argv[1], "*.zip"))):
    with zipfile.ZipFile(p) as z:
        acc = read(z, "ACCIDENT.CSV")[["ST_CASE", "YEAR", "MONTH", "DAY", "HOUR"]]
        per = read(z, "PERSON.CSV")[["ST_CASE", "PER_TYP", "INJ_SEV", "AGE"]]
    d = per.merge(acc, on="ST_CASE")
    frames.append(d[(d.PER_TYP == 5) & (d.INJ_SEV == 4)])
d = pd.concat(frames)
d["date"] = pd.to_datetime(dict(year=d.YEAR, month=d.MONTH, day=d.DAY), errors="coerce")
d = d.dropna(subset=["date"])
d["child"] = d.AGE < 18
d["eve"] = d.HOUR.between(18, 23)
years = range(2000, 2025)
alldays = pd.date_range("2000-01-01", "2024-12-31")

def per_day(mask):
    return d[mask].groupby("date").size().reindex(alldays, fill_value=0)

res = {}
for label, kmask in [("all ages", d.child | ~d.child), ("under 18", d.child)]:
    for win, wmask in [("whole day", d.eve | ~d.eve), ("6pm-midnight", d.eve)]:
        s = per_day(kmask & wmask)
        hal = s[(s.index.month == 10) & (s.index.day == 31)]
        other = s[~((s.index.month == 10) & (s.index.day == 31))]
        # +/- 1 week control nights (Oct 24 and Nov 7)
        ctrl = s[((s.index.month == 10) & (s.index.day == 24)) | ((s.index.month == 11) & (s.index.day == 7))]
        print(f"{label:9} {win:13} Oct31 mean/yr={hal.mean():.2f} total={hal.sum():3d} | "
              f"other-day mean={other.mean():.2f} ratio={hal.mean()/other.mean():.2f} | "
              f"Oct24/Nov7 mean={ctrl.mean():.2f} ratio={hal.mean()/ctrl.mean():.2f}")
        if label == "under 18" and win == "6pm-midnight":
            print("  child eve Oct31 by year:", hal.groupby(hal.index.year).sum().to_dict())
        # Oct 31 rank among days of year
        rk = s.groupby([s.index.month, s.index.day]).sum().rank(ascending=False, method="min")
        print(f"   rank of Oct 31 among calendar days (366): {int(rk[(10,31)])}; max day total: {s.groupby([s.index.month, s.index.day]).sum().max()}")
