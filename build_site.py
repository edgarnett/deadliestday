"""Merge the analysis outputs and US state outlines into site/template.html -> site/index.html."""
import json

ped = json.load(open("site_data.json", encoding="utf8"))        # halloween_deadliest.py
road = json.load(open("site_data_all.json", encoding="utf8"))   # halloween_all.py
states = json.load(open("us_states.json", encoding="utf8"))
users = json.load(open("road_types.json", encoding="utf8"))                # road_types.py


def rnd(c):
    return [rnd(x) for x in c] if isinstance(c[0], list) else [round(c[0], 2), round(c[1], 2)]


for f in states["features"]:
    f["geometry"]["coordinates"] = rnd(f["geometry"]["coordinates"])

data = dict(pedcal=ped["cal"], weekday=ped["weekday"], years=ped["years"],
            roadcal=road["cal"], pts=road["pts"], types=road["types"], n_days=road["n_days"],
            states=states, usertypes=users)
t = open("site/template.html", encoding="utf8").read().replace("__SHARE__", open("site/share.js", encoding="utf8").read())
open("site/index.html", "w", encoding="utf8").write(t.replace("__DATA__", json.dumps(data, separators=(",", ":"))))
