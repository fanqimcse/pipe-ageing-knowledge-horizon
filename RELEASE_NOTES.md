# v1.0.0 — Management as Censoring: Selective Renewal and the Knowledge Horizon of Pipe Ageing

Companion code, data-derived results, figures and manuscript for the R24 study
submitted-style manuscript prepared for *Water Research* (Elsevier `elsarticle`, author-year).

## Headline results

- **Information survival curve** $S_I(a;\gamma)=e^{-\gamma a}M(a)/F(a)$ with
  $M(a)=\int_0^a f(u)e^{\gamma u}\,du$; Proposition A ($0<S_I\le 1$),
  Proposition B ($\partial S_I/\partial\gamma<0$, proved via Gauss–Jacobi quadrature with
  the weight absorbed, so negativity holds at the discrete level too), and Proposition B$'$
  (knowledge horizon $H(\kappa;\gamma)=\sup\{a:\inf_{u\le a}S_I(u;\gamma)\ge\kappa\}$ is
  non-increasing in $\gamma$).
- **Uniform bound** (T2): $|D|\le|\varphi-1|\max\{(1-p)/\varphi,\ p\}\le|\varphi-1|\max(1,\varphi^{-1})$,
  verified on 540 parameter combinations with worst-case slack $0.0$ and tightness ratio $1.0000$.
- **Data**: Kitchener water mains (13,921 pipe segments, 817.6 km; 1997+ cohort 8,459 segments,
  398.9 km). $\hat\varphi=1.43$ (Mantel–Haenszel, age-stratified).
- **Calibrated excess-removal intensity** $\hat\gamma\in\{0.0453,0.0550,0.0646,0.0725\}$ /yr
  for $\beta\in\{1.5,2.0,2.5,2.907\}$; horizon $H(0.5)=45.6\text{–}47.3$ yr.
- **Honest negative result**: cluster bootstrap gives $\hat\gamma=0.0550$,
  95% CI $[0.0124, 0.2113]$ and $H(0.5)\in[12.1, 196.5]$ yr — a 15-fold span, so the
  data **cannot** discriminate between the two regimes. This is reported in the manuscript
  rather than hidden.

## Repository layout

```
code/        analysis scripts a89–a97, make_figs.py, make_manuscript.py
results/     paper_numbers.json (single source of every number in the manuscript)
             a96_boot.json, run logs
figs/        fig1–fig5 (PDF + PNG, single/double column widths)
manuscript/  manuscript.tex, manuscript.pdf, refs.bib, citation_map.md/.json
refs/        build_refs.py (Crossref), download scripts, 4 download manifests
```

## Reproducing

```bash
python code/a94_final.py          # all manuscript numbers -> results/paper_numbers.json
python code/a96_boot.py           # cluster bootstrap for gamma -> results/a96_boot.json
python code/a97_extra.py          # Table 1 statistics
python code/make_figs.py          # figs/fig1..fig5.{pdf,png}
python code/make_manuscript.py    # manuscript/manuscript.tex
```

Requires Python 3.11+ with `numpy`, `scipy`, `pandas`. Raw Kitchener data are not
redistributable here; see README for access notes.

## References — honest statement

All 34 bibliography entries were generated programmatically from **Crossref DOI records**
(`refs/build_refs.py`); no bibliographic field was hand-typed. `manuscript/citation_map.md`
lists, for each cited work, the exact manuscript sentence it supports.

Full-text PDF download was attempted in four independent rounds (Unpaywall, OpenAlex,
Semantic Scholar, known open mirrors). **0 of 34** were obtained — all targets are behind
publisher paywalls (HTTP 403/410) or rate-limited. Per-item status is recorded in
`refs/download_manifest*.txt`. No entry is claimed as "downloaded" that was not.
