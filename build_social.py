"""Build social/bluesky.png (1200x1350) from the same data as the site. Needs Microsoft Edge."""
import json, subprocess, pathlib

ped = json.load(open("site_data.json", encoding="utf8"))
road = json.load(open("site_data_all.json", encoding="utf8"))
states = json.load(open("us_states.json", encoding="utf8"))


def rnd(c):
    return [rnd(x) for x in c] if isinstance(c[0], list) else [round(c[0], 2), round(c[1], 2)]


for f in states["features"]:
    f["geometry"]["coordinates"] = rnd(f["geometry"]["coordinates"])
data = dict(pedcal=ped["cal"], pts=road["pts"], states=states)
t = open("social/graphic_template.html", encoding="utf8").read()
html = pathlib.Path("social/graphic.html")
html.write_text(t.replace("__DATA__", json.dumps(data, separators=(",", ":"))), encoding="utf8")
edge = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
subprocess.run([edge, "--headless", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                f"--screenshot={pathlib.Path('social/bluesky.png').resolve()}", "--window-size=1200,1350",
                html.resolve().as_uri()], check=True)

# 1200x630 link-preview image (og:image) used by the site's Open Graph tags
subprocess.run([edge, "--headless", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                f"--screenshot={pathlib.Path('social/og.png').resolve()}", "--window-size=1200,630",
                pathlib.Path("social/og.html").resolve().as_uri()], check=True)
