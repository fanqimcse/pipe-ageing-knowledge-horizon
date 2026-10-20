# 参考文献全文获取状态汇总

稿件共引用 **34** 条文献（其中 **31** 条在正文中被 `\cite` 实际引用，
另 3 条在 `refs.bib` 中作为背景条目保留）。全部书目字段由 **Crossref DOI 记录程序化生成**
（`refs/build_refs.py`），无一条手写。

## 下载尝试

| 轮次 | 渠道 | 结果 |
|---|---|---|
| 1 | Unpaywall（`build_refs.py` 内联） | 0 / 34 |
| 2 | OpenAlex + Unpaywall + 已知直链 | 0 / 34 |
| 3 | 已知开放副本直链 | 0 / 34 |
| 4 | Semantic Scholar + OpenAlex | 0 / 34 |
| 5 | arXiv API + PNAS 直链 + Project Euclid + arXiv 预印本直链 | **1 / 34** |
| 6 | arXiv API（修正查询串转义后重试） | 0 / 34（API 在本机超时） |

**最终：取得全文 1 / 34**（`Hardt2025`，arXiv:2310.16608，593,682 B，存于 `refs/pdf/Hardt2025.pdf`）。

## 33 条未获取的逐条原因

- **Elsevier / IWA / Taylor & Francis / Wiley / Oxford 付费墙**（HTTP 403 / 410）：
  Scheidegger2013、Scheidegger2015、LeGat2013、LeGat2000、Renaud2012、Renaud2014、
  LeGat2013b、Kleiner2001、Rajani2012、Alvisi2010、Winkler2018、Ouellet2018、
  Cox1972、Mantel1959、Nelson1969、Prentice1981、Slud1983、Zheng1995、
  Scharfstein1999、Wang2001、Bartlett2014、Drent2020
- **ASCE / JSTOR / 图书**：Kleiner2002、Crowder1994、Andersen1993、Kalbfleisch2002、
  KleinMoeschberger2003、Manski2003、Tamer2010、BarlowProschan1965
- **直链返回落地页而非 PDF / 403**：Aalen1978、Lin1995（Project Euclid）、Tsiatis1975（PNAS）
- **arXiv API 在本机不可达**（`TimeoutError` / `HTTPError`）：全部条目的预印本检索均失败

逐条机器可读记录见 `refs/download_manifest.txt`、`download_manifest2.txt`、
`download_manifest3.txt`、`download_manifest4.txt`、`download_manifest5.txt`、`download_manifest6.txt`。

## 声明

**没有任何一条被伪报为"已下载"。** 引用对应表 `manuscript/citation_map.md` 中每条文献的
「全文」字段直接取自上述清单；未获取者一律标注 `blocked` 及原因。
书目正确性不依赖全文：所有字段来自 Crossref 的权威 DOI 记录。
