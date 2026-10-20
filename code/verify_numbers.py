"""Check that every number appearing in the manuscript's tables can be traced
back to results/*.json (the single source of truth declared in the README)."""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "results")
TEX = os.path.join(HERE, "paper", "manuscript.tex")

blob = ""
for fn in sorted(os.listdir(RES)):
    if not fn.endswith(".json"):
        continue
    p = os.path.join(RES, fn)
    if os.path.getsize(p) == 0:      # superseded / abandoned runs
        continue
    with open(p, encoding="utf-8") as fh:
        blob += json.dumps(json.load(fh))
blob += open(os.path.join(HERE, "make_manuscript.py"), encoding="utf-8").read()

tex = open(TEX, encoding="utf-8").read()
tabs = re.findall(r"\\begin\{table[*]?\}(.*?)\\end\{table[*]?\}", tex, re.S)

NUM = re.compile(r"(?<![A-Za-z\\{}_.\-])(\d+\.(\d{2,}))(?![A-Za-z])")

# every float appearing in the JSON results (plus the generator)
raws = [float(x) for x in re.findall(r"-?\d+\.\d+(?:[eE][-+]?\d+)?", blob)]
# the printed table may be a /1000 rescaling of a stored value (e.g. exposure)
raws = raws + [x / 1000.0 for x in raws] + [x * 1000.0 for x in raws]
# pre-compute the formatted strings a stored value could legitimately produce
forms = set()
for x in raws:
    for d in range(1, 7):
        forms.add("%.*f" % (d, x))

bad, checked = [], 0
for k, t in enumerate(tabs, 1):
    for m in NUM.finditer(t):
        v = m.group(1)
        checked += 1
        if v not in forms:
            bad.append((k, v))
print(f"table numbers checked: {checked}")
print("untraceable to results/*.json:", bad if bad else "none")
sys.exit(1 if bad else 0)
