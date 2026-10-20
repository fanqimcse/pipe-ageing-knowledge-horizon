# pipe-ageing-knowledge-horizon

**How much can a water utility learn about pipe ageing from its own failure
records? Merged replacement histories, selective renewal, and the limits of
inference** — manuscript, code, results and reference library.

Compiled manuscript: [`manuscript/manuscript.pdf`](manuscript/manuscript.pdf)
(elsarticle, Water Research submission format, 26 pp).

## What this repository contains

| Path | Content |
|---|---|
| `manuscript/` | LaTeX source, compiled PDF, `refs.bib`, citation map (`citation_map.md`) |
| `code/` | Analysis pipeline `a89`–`a97` (numbered in execution order) |
| `results/` | Result JSON + execution logs — **the single source of every number in the paper** |
| `figs/` | Figure builder (`../code/make_figs.py` output) |
| `refs/` | Reference verification against Crossref, `refs.bib` build, full-text download attempts with per-reference manifests |

## The provenance discipline

Every number in the manuscript is injected by `code/make_manuscript.py`
from `results/paper_numbers.json` + `results/a96_boot.json`. No result is
hand-typed; `make_figs.py` reads the same files. To rebuild everything:

```bash
# 1. analysis (requires the Kitchener open data, see below)
python code/a94_final.py && python code/a96_boot.py && python code/a97_extra.py
# 2. figures and manuscript
python code/make_figs.py && python code/make_manuscript.py
cd manuscript && pdflatex manuscript && bibtex manuscript && pdflatex manuscript && pdflatex manuscript
```

## Data

The Kitchener (Ontario, Canada) water-main asset and break layers are
published as open data by the City of Kitchener (datasets *watermains* and
*water main breaks*). We redistribute neither; place the two GeoJSON
downloads in a directory pointed to by the `KW` environment variable
(the loader is `code/../a83_params.py::load_kitchener`, shared with the
earlier review round).

## Headline results (all from `results/`)

- **Merged replacement histories**: renewal reuses `WATMAINID`, so 187 of
  1,526 previously failed pipes (12.3 %) carry break records predating their
  installation year; 330 of 3,010 break records (11.0 %) belong to a
  predecessor (median 8 yr, max 34 yr earlier).
- **Recurrence rate ratio** (age-stratified Mantel–Haenszel):
  1.4253 [1.2802, 1.5870] before the repair → 1.4141 [1.2699, 1.5746] after;
  bias direction confirmed at 21/21 non-degenerate ages; distribution-free
  bias bound |D| ≤ |φ−1|·max(1, φ⁻¹) = 0.4141.
- **Two worlds**: age exponent β = 2.371 ± 0.059 (full stock, left-truncated)
  vs 0.243 ± 0.265 (complete-history cohort); intensities differ 10.9× /
  42.8× / 113.1× at ages 30 / 57 / 90 yr, while 51.2 % of network length is
  already older than the 28-yr observation window.
- **Knowledge horizon**: S_I(a;γ) retention model calibrated to γ̂ ≈ 0.055/yr
  gives H(0.5) ≈ 46 yr > W, but a cluster bootstrap gives γ ∈
  [0.012, 0.211]/yr — the regime discriminant is **undecided** in these
  records (an honest negative result).
- **Sentinel randomised-deferral design**: deferring 20 % of failure-triggered
  renewals by 15 yr recovers ≈ 21.7 events (world F) vs ≈ 0.4 (world Y) —
  decisive in either direction.

## References

`refs/refs.bib` is generated from Crossref records by DOI (34 entries); two
entries lack Crossref author fields and were completed by hand (flagged in
the file history). Full texts: four download passes (Unpaywall, OpenAlex,
Semantic Scholar, direct repository links) are documented in
`refs/download_manifest*.txt`; paywalled items are listed with their DOI and
the claim they support rather than fabricated as "downloaded".

## License

Code and text: MIT. Data remain under the City of Kitchener's open-data terms.
