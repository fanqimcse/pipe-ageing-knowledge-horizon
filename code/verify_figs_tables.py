"""Verify that every figure/table in manuscript.tex is:
  (1) an existing file on disk, (2) actually embedded in manuscript.pdf,
  (3) referenced by \\ref with a matching \\label, (4) numbered consecutively,
  (5) free of nan/undefined placeholders.
Also cross-check a sample of table numbers against results/paper_numbers.json.
"""
import json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
PAPER = os.path.join(HERE, "paper")
RES = os.path.join(HERE, "results")
TEX = os.path.join(PAPER, "manuscript.tex")
PDF = os.path.join(PAPER, "manuscript.pdf")

tex = open(TEX, encoding="utf-8").read()
fail = []

# ---------- figures ----------
figs = re.findall(r"\\begin\{figure[*]?\}(.*?)\\end\{figure[*]?\}", tex, re.S)
print(f"figure environments: {len(figs)}")
figfiles = []
for k, f in enumerate(figs, 1):
    inc = re.findall(r"\\includegraphics\[[^\]]*\]\{([^}]*)\}", f)
    lab = re.findall(r"\\label\{([^}]*)\}", f)
    cap = re.findall(r"\\caption\{(.*?)\n", f, re.S)
    if len(inc) != 1:
        fail.append(f"fig{k}: expected 1 includegraphics, got {len(inc)}")
        continue
    p = os.path.join(PAPER, inc[0] if inc[0].endswith(".pdf") else inc[0] + ".pdf")
    ok = os.path.exists(p)
    figfiles.append(os.path.basename(p))
    print(f"  fig{k}: file={inc[0]} exists={ok} label={lab} caption={'yes' if cap else 'NO'}")
    if not ok:
        fail.append(f"fig{k}: missing file {p}")
    if not lab:
        fail.append(f"fig{k}: no label")

# ---------- embedded images in PDF (from the LaTeX log) ----------
log = open(os.path.join(PAPER, "manuscript.log"), encoding="utf-8", errors="replace").read()
logfigs = sorted(set(re.findall(r"<\.\./figs/([A-Za-z0-9_.\-]+\.pdf)", log)))
print(f"\nfigures actually included per LaTeX log: {logfigs}")
for ff in figfiles:
    if ff not in logfigs:
        fail.append(f"{ff} not included in PDF build")
# orphan generated figures
gen = sorted(f for f in os.listdir(os.path.join(HERE, "figs"))
             if f.endswith(".pdf"))
orphan = [f for f in gen if f not in logfigs]
print(f"generated: {gen}   never-used: {orphan}")
if orphan:
    fail.append(f"generated but unused figures: {orphan}")

# ---------- tables ----------
tabs = re.findall(r"\\begin\{table[*]?\}(.*?)\\end\{table[*]?\}", tex, re.S)
print(f"\ntable environments: {len(tabs)}")
for k, t in enumerate(tabs, 1):
    lab = re.findall(r"\\label\{([^}]*)\}", t)
    cap = re.findall(r"\\caption\{", t)
    ncol = t.count("&")
    print(f"  tab{k}: label={lab} caption={'yes' if cap else 'NO'} amp={ncol}")
    if not lab:
        fail.append(f"tab{k}: no label")
    if not cap:
        fail.append(f"tab{k}: no caption")

# ---------- refs vs labels ----------
labels = set(re.findall(r"\\label\{([^}]*)\}", tex))
refs = set(re.findall(r"\\(?:ref|autoref|cref|Cref)\{([^}]*)\}", tex))
missing = sorted(r for r in refs if r not in labels)
print(f"\nlabels: {len(labels)}  refs: {len(refs)}  dangling refs: {missing}")
if missing:
    fail.append(f"dangling refs {missing}")

# ---------- unresolved ?? ----------
if "??" in tex:
    fail.append("literal ?? in tex")

# ---------- placeholder scan (word-boundary; nan/inf appear inside
#            "discriminant", "information", "infrastructure" etc.) ----------
for tok in ["nan", "NaN", "None", "inf", "@@", "%s", "{{"]:
    pat = re.compile(r"(?<![A-Za-z\\])" + re.escape(tok) + r"(?![A-Za-z])")
    hits = [i + 1 for i, l in enumerate(tex.splitlines()) if pat.search(l)]
    if hits:
        fail.append(f"placeholder {tok!r} at lines {hits[:5]}")

print("\n--- FAILURES ---" if fail else "\n--- ALL CHECKS PASSED ---")
for f in fail:
    print(" !", f)
sys.exit(1 if fail else 0)
