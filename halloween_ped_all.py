"""Child (<18) pedestrian deaths on Oct 31, by year, from NHTSA FARS.

Usage: python halloween_ped.py FARS2010NationalCSV.zip FARS2011NationalCSV.zip ...
   or: python halloween_ped.py folder_with_zips
Download zips: NHTSA FARS data page -> National CSV for each year.
Requires: pandas.
"""
import sys, zipfile, glob, os
import pandas as pd

def read(z, name):
    # file name case varies between years (PERSON.CSV / person.csv)
    match = next(n for n in z.namelist() if os.path.basename(n).upper() == name)
    with z.open(match) as f:
        return pd.read_csv(f, encoding="latin-1", low_memory=False)

paths = []
for a in sys.argv[1:]:
    paths += glob.glob(os.path.join(a, "*.zip")) if os.path.isdir(a) else [a]

rows = []
for p in sorted(paths):
    with zipfile.ZipFile(p) as z:
        acc = read(z, "ACCIDENT.CSV")[["ST_CASE", "YEAR", "MONTH", "DAY"]]
        per = read(z, "PERSON.CSV")[["ST_CASE", "PER_TYP", "INJ_SEV", "AGE"]]
    d = per.merge(acc, on="ST_CASE")
    d = d[(d.MONTH == 10) & (d.DAY == 31) & (d.PER_TYP == 5)
          & (d.INJ_SEV == 4)]
    rows.append(d.groupby("YEAR").size())

out = pd.concat(rows).sort_index()
print(out.to_string())
print("Total:", out.sum())
