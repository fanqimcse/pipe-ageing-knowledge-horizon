# 引用对应表（citation map）

生成方式：自动扫描 `manuscript.tex`，对每条被引文献列出（1）Crossref 权威记录（题名/刊名/年/DOI）；（2）稿件中支撑它的**原句**；（3）该文献在本研究中承担的论证角色（`refs.bib` 的 note 字段）；（4）全文获取状态（四轮下载尝试的结果清单见 `refs/download_manifest*.txt`）。

## Scheidegger2013
- **题名**: Extension of pipe failure models to consider the absence of data from replaced pipes
- **出处**: Water Research (2013)  **DOI**: 10.1016/j.watres.2013.04.017
- **论证角色**: 被更换管道造成的数据缺失；failure model + replacement model 联合似然
- **全文**: Scheidegger2013          blocked  SSLError
- **稿件中支撑句**:
  - “Physically, a replaced pipe disappears from the asset register of the old pipe, so part of the failure history is missing by construction  \citep {Scheidegger2013,Ouellet2018}.”
  - “In the water-domain literature,  \citet {Scheidegger2013} treat missing replaced-pipe data by augmenting the likelihood with a renewal model, and the LEYP2s model of  \citet {LeGat2013} embeds the post-failure repair probability and a Yule-type amplification of the failure rate in the number of past failures.”
  - “We do not propose a new failure model; the models we use are instances of established frameworks  \citep {LeGat2013,Scheidegger2013}.”
  - “ \section {The recurrence rate ratio and the direction of bias}  \label {sec:phi}  \subsection {Estimand} Following the two-state framework of  \citet {LeGat2013} and  \citet {Scheidegger2013}, let $h(a)= \lambda  a^{ \beta -1}$ be the age-specific failure intensity of a never-failed pipe, and let the post-repair intensity of a previously failed pipe be amplified by a factor $ \phi   \ge  1$ (the LEYP2s Yule factor is the more general $(1+ \alpha  N(t-))$; we use the constant-$ \phi $ special case), as sketched in Fig.~ \ref {fig:model}.”
  - “Claims about 60- or 90-year-old pipes made from these records are claims about a chosen shape, not measurements --- a point the competing-risks literature has made for half a century  \citep {Tsiatis1975,Crowder1994} and that the water-domain corrected estimators  \citep {Scheidegger2013,LeGat2013} implicitly inherit.”
  - “(iv)~The two-state model with instantaneous repair and constant $ \phi $ is a special case of established frameworks  \citep {LeGat2013,Scheidegger2013}; we use it because its bias is analytically tractable and bounded, not because it is the best available description of the data.”
  - “ \subsection {Relation to prior work} The corrected-estimator route of  \citet {Scheidegger2013} and  \citet {LeGat2013} and the audit route of  \citet {Bartlett2014} are complementary to what we do here: we neither propose a new estimator nor a new correction, but (a) document a record-linkage defect that any of those methods would silently absorb, (b) give the horizon construct  \eqref {eq:SI}--(P3) that makes ``how far can we see'' a number rather than a slogan, and (c) show that the ambiguity a horizon implies is resolvable by a randomised deferral of exactly the kind that reliability theo”

## Scheidegger2015
- **题名**: Statistical failure models for water distribution pipes – A review from a unified perspective
- **出处**: Water Research (2015)  **DOI**: 10.1016/j.watres.2015.06.027
- **论证角色**: 管道失效统计模型综述（统一视角）
- **全文**: Scheidegger2015          blocked  SSLError
- **稿件中支撑句**:
  - “ \documentclass [review,12pt,authoryear]{elsarticle}  \usepackage {amsmath,amssymb}  \usepackage {graphicx}  \usepackage {booktabs}  \usepackage {multirow}  \usepackage [colorlinks=true,linkcolor=blue,citecolor=blue,urlcolor=blue]{hyperref}  \usepackage {lineno}  \modulolinenumbers [5]  \emergencystretch =1.5em  \journal {Water Research}  \begin {document}  \begin {frontmatter}  \title {How much can a water utility learn about pipe ageing from its own failure records? Merged replacement histories, selective renewal, and the limits of inference}  \author [a]{First Author \corref {cor1}}  \ead {”
  - “Throughout, a pipe's state is N (never failed within the observation window) or B (failed at least once and instantaneously repaired, the standard assumption in this literature  \citep {LeGat2013,Scheidegger2015}).”

## LeGat2013
- **题名**: Extending the Yule process to model recurrent pipe failures in water supply networks
- **出处**: Urban Water Journal (2014)  **DOI**: 10.1080/1573062x.2013.783088
- **论证角色**: LEYP2s：失效后修复概率 + Yule 因子；我们的 φ 是其退化特例
- **全文**: LeGat2013                blocked  HTTP 429 @api.semanticscholar.org
- **稿件中支撑句**:
  - “In the water-domain literature,  \citet {Scheidegger2013} treat missing replaced-pipe data by augmenting the likelihood with a renewal model, and the LEYP2s model of  \citet {LeGat2013} embeds the post-failure repair probability and a Yule-type amplification of the failure rate in the number of past failures.”
  - “We do not propose a new failure model; the models we use are instances of established frameworks  \citep {LeGat2013,Scheidegger2013}.”
  - “Throughout, a pipe's state is N (never failed within the observation window) or B (failed at least once and instantaneously repaired, the standard assumption in this literature  \citep {LeGat2013,Scheidegger2015}).”
  - “Both the recurrence rate ratio (Section~ \ref {sec:phi}) and any covariate depending on the number of past failures  \citep {LeGat2013} are affected.”
  - “ \section {The recurrence rate ratio and the direction of bias}  \label {sec:phi}  \subsection {Estimand} Following the two-state framework of  \citet {LeGat2013} and  \citet {Scheidegger2013}, let $h(a)= \lambda  a^{ \beta -1}$ be the age-specific failure intensity of a never-failed pipe, and let the post-repair intensity of a previously failed pipe be amplified by a factor $ \phi   \ge  1$ (the LEYP2s Yule factor is the more general $(1+ \alpha  N(t-))$; we use the constant-$ \phi $ special case), as sketched in Fig.~ \ref {fig:model}.”
  - “Claims about 60- or 90-year-old pipes made from these records are claims about a chosen shape, not measurements --- a point the competing-risks literature has made for half a century  \citep {Tsiatis1975,Crowder1994} and that the water-domain corrected estimators  \citep {Scheidegger2013,LeGat2013} implicitly inherit.”
  - “(iv)~The two-state model with instantaneous repair and constant $ \phi $ is a special case of established frameworks  \citep {LeGat2013,Scheidegger2013}; we use it because its bias is analytically tractable and bounded, not because it is the best available description of the data.”
  - “ \subsection {Relation to prior work} The corrected-estimator route of  \citet {Scheidegger2013} and  \citet {LeGat2013} and the audit route of  \citet {Bartlett2014} are complementary to what we do here: we neither propose a new estimator nor a new correction, but (a) document a record-linkage defect that any of those methods would silently absorb, (b) give the horizon construct  \eqref {eq:SI}--(P3) that makes ``how far can we see'' a number rather than a slogan, and (c) show that the ambiguity a horizon implies is resolvable by a randomised deferral of exactly the kind that reliability theo”

## LeGat2000
- **题名**: Using maintenance records to forecast failures in water networks
- **出处**: Urban Water (2000)  **DOI**: 10.1016/s1462-0758(00)00057-1
- **论证角色**: 用维修记录预测供水网络失效（早期非齐次 Poisson / 队列方法）
- **全文**: LeGat2000                blocked  HTTP 429 @api.semanticscholar.org
- **稿件中支撑句**:
  - “ \documentclass [review,12pt,authoryear]{elsarticle}  \usepackage {amsmath,amssymb}  \usepackage {graphicx}  \usepackage {booktabs}  \usepackage {multirow}  \usepackage [colorlinks=true,linkcolor=blue,citecolor=blue,urlcolor=blue]{hyperref}  \usepackage {lineno}  \modulolinenumbers [5]  \emergencystretch =1.5em  \journal {Water Research}  \begin {document}  \begin {frontmatter}  \title {How much can a water utility learn about pipe ageing from its own failure records? Merged replacement histories, selective renewal, and the limits of inference}  \author [a]{First Author \corref {cor1}}  \ead {”

## Renaud2012
- **题名**: Using a break prediction model for drinking water networks asset management: From research to practice
- **出处**: Water Supply (2012)  **DOI**: 10.2166/ws.2012.040
- **论证角色**: 破裂预测模型用于资产管理：从研究到实践
- **全文**: Renaud2012               blocked  HTTP 429 @api.semanticscholar.org
- **稿件中支撑句**:
  - “ \documentclass [review,12pt,authoryear]{elsarticle}  \usepackage {amsmath,amssymb}  \usepackage {graphicx}  \usepackage {booktabs}  \usepackage {multirow}  \usepackage [colorlinks=true,linkcolor=blue,citecolor=blue,urlcolor=blue]{hyperref}  \usepackage {lineno}  \modulolinenumbers [5]  \emergencystretch =1.5em  \journal {Water Research}  \begin {document}  \begin {frontmatter}  \title {How much can a water utility learn about pipe ageing from its own failure records? Merged replacement histories, selective renewal, and the limits of inference}  \author [a]{First Author \corref {cor1}}  \ead {”

## Renaud2014
- **题名**: Water pipes: why ‘lifetime’ is not an adequate concept on which to base pipe renewal strategies
- **出处**: Water Practice and Technology (2014)  **DOI**: 10.2166/wpt.2014.032
- **论证角色**: 「寿命」不是管道更新策略的恰当概念
- **全文**: Renaud2014               10.2166/wpt.2014.032                 paywalled-or-blocked   https://irsteadoc.irstea.fr/cemoa/PUB00042134 -> SSLError: HTTPSConnectionPool(host='irsteadoc.irstea.fr', port=443): Max retries exceeded with url:
- **稿件中支撑句**:
  - “Ageing-intensity estimates are routinely extrapolated to ages at which the network holds most of its value, while the observation window of the records is short relative to asset lives  \citep {Renaud2014,LeGat2013b}.”

## LeGat2013b
- **题名**: Is the service life of water distribution pipelines linked to their failure rate?
- **出处**: Water Supply (2013)  **DOI**: 10.2166/ws.2013.089
- **论证角色**: 服务寿命与失效率是否相关（更换与失效的耦合）
- **全文**: LeGat2013b               10.2166/ws.2013.089                  paywalled-or-blocked   https://irsteadoc.irstea.fr/cemoa/PUB00039690 -> SSLError: HTTPSConnectionPool(host='irsteadoc.irstea.fr', port=443): Max retries exceeded with url:
- **稿件中支撑句**:
  - “Ageing-intensity estimates are routinely extrapolated to ages at which the network holds most of its value, while the observation window of the records is short relative to asset lives  \citep {Renaud2014,LeGat2013b}.”

## Kleiner2001
- **题名**: Comprehensive review of structural deterioration of water mains: statistical models
- **出处**: Urban Water (2001)  **DOI**: 10.1016/s1462-0758(01)00033-4
- **论证角色**: 水管理化统计模型综述（领域背景）
- **全文**: Kleiner2001              10.1016/s1462-0758(01)00033-4        paywalled-or-blocked   http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.2.7855 -> HTTP 502
- **稿件中支撑句**:
  - “ \documentclass [review,12pt,authoryear]{elsarticle}  \usepackage {amsmath,amssymb}  \usepackage {graphicx}  \usepackage {booktabs}  \usepackage {multirow}  \usepackage [colorlinks=true,linkcolor=blue,citecolor=blue,urlcolor=blue]{hyperref}  \usepackage {lineno}  \modulolinenumbers [5]  \emergencystretch =1.5em  \journal {Water Research}  \begin {document}  \begin {frontmatter}  \title {How much can a water utility learn about pipe ageing from its own failure records? Merged replacement histories, selective renewal, and the limits of inference}  \author [a]{First Author \corref {cor1}}  \ead {”

## Kleiner2002
- **题名**: Forecasting Variations and Trends in Water-Main Breaks
- **出处**: Journal of Infrastructure Systems (2002)  **DOI**: 10.1061/(asce)1076-0342(2002)8:4(122)
- **论证角色**: 爆管的时间变化与趋势预测（领域背景）
- **全文**: Kleiner2002              10.1061/(asce)1076-0342(2002)8:4(122) paywalled-or-blocked   http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.9.4126 -> HTTP 502
- **稿件中支撑句**:
  - “ \documentclass [review,12pt,authoryear]{elsarticle}  \usepackage {amsmath,amssymb}  \usepackage {graphicx}  \usepackage {booktabs}  \usepackage {multirow}  \usepackage [colorlinks=true,linkcolor=blue,citecolor=blue,urlcolor=blue]{hyperref}  \usepackage {lineno}  \modulolinenumbers [5]  \emergencystretch =1.5em  \journal {Water Research}  \begin {document}  \begin {frontmatter}  \title {How much can a water utility learn about pipe ageing from its own failure records? Merged replacement histories, selective renewal, and the limits of inference}  \author [a]{First Author \corref {cor1}}  \ead {”

## Rajani2012
- **题名**: Exploration of the relationship between water main breaks and temperature covariates
- **出处**: Urban Water Journal (2012)  **DOI**: 10.1080/1573062x.2011.630093
- **论证角色**: 爆管与温度协变量（领域背景）
- **全文**: Rajani2012               10.1080/1573062x.2011.630093         paywalled-or-blocked   https://nrc-publications.canada.ca/fra/voir/objet/?id=7c91a647-aadd-40 -> HTTP 410
- **稿件中支撑句**:
  - “ \documentclass [review,12pt,authoryear]{elsarticle}  \usepackage {amsmath,amssymb}  \usepackage {graphicx}  \usepackage {booktabs}  \usepackage {multirow}  \usepackage [colorlinks=true,linkcolor=blue,citecolor=blue,urlcolor=blue]{hyperref}  \usepackage {lineno}  \modulolinenumbers [5]  \emergencystretch =1.5em  \journal {Water Research}  \begin {document}  \begin {frontmatter}  \title {How much can a water utility learn about pipe ageing from its own failure records? Merged replacement histories, selective renewal, and the limits of inference}  \author [a]{First Author \corref {cor1}}  \ead {”

## Alvisi2010
- **题名**: Comparative analysis of two probabilistic pipe breakage models applied to a real water distribution system
- **出处**: Civil Engineering and Environmental Systems (2010)  **DOI**: 10.1080/10286600802224064
- **论证角色**: 两种概率型爆管模型的比较（领域背景）
- **全文**: Alvisi2010               10.1080/10286600802224064            paywalled-or-blocked   http://hdl.handle.net/11392/530286 -> HTTP 403
- **稿件中支撑句**:
  - “ \documentclass [review,12pt,authoryear]{elsarticle}  \usepackage {amsmath,amssymb}  \usepackage {graphicx}  \usepackage {booktabs}  \usepackage {multirow}  \usepackage [colorlinks=true,linkcolor=blue,citecolor=blue,urlcolor=blue]{hyperref}  \usepackage {lineno}  \modulolinenumbers [5]  \emergencystretch =1.5em  \journal {Water Research}  \begin {document}  \begin {frontmatter}  \title {How much can a water utility learn about pipe ageing from its own failure records? Merged replacement histories, selective renewal, and the limits of inference}  \author [a]{First Author \corref {cor1}}  \ead {”

## Winkler2018
- **题名**: Pipe failure modelling for water distribution networks using boosted decision trees
- **出处**: Structure and Infrastructure Engineering (2018)  **DOI**: 10.1080/15732479.2018.1443145
- **论证角色**: boosted decision trees 爆管建模（领域背景）
- **全文**: Winkler2018              10.1080/15732479.2018.1443145        paywalled-or-blocked   http://resolver.tudelft.nl/uuid:fdc2b0f4-a106-4245-8600-35c3622d6f33 -> not a PDF (30784 bytes, b'<!DOCTYPE ht')
- **稿件中支撑句**:
  - “ \documentclass [review,12pt,authoryear]{elsarticle}  \usepackage {amsmath,amssymb}  \usepackage {graphicx}  \usepackage {booktabs}  \usepackage {multirow}  \usepackage [colorlinks=true,linkcolor=blue,citecolor=blue,urlcolor=blue]{hyperref}  \usepackage {lineno}  \modulolinenumbers [5]  \emergencystretch =1.5em  \journal {Water Research}  \begin {document}  \begin {frontmatter}  \title {How much can a water utility learn about pipe ageing from its own failure records? Merged replacement histories, selective renewal, and the limits of inference}  \author [a]{First Author \corref {cor1}}  \ead {”

## Ouellet2018
- **题名**: A method to consider replaced pipes in modeling of sewer pipe deterioration
- **出处**: Urban Water Journal (2018)  **DOI**: 10.1080/1573062x.2018.1455883
- **论证角色**: 在排水管道劣化建模中考虑已更换管（与本文同一问题、不同介质）
- **全文**: Ouellet2018              10.1080/1573062x.2018.1455883        paywalled-or-blocked   https://espace.inrs.ca/id/eprint/7734/ -> HTTP 403
- **稿件中支撑句**:
  - “Physically, a replaced pipe disappears from the asset register of the old pipe, so part of the failure history is missing by construction  \citep {Scheidegger2013,Ouellet2018}.”

## Cox1972
- **题名**: Regression Models and Life-Tables
- **出处**: Journal of the Royal Statistical Society Series B: Statistical Methodology (1972)  **DOI**: 10.1111/j.2517-6161.1972.tb00899.x
- **论证角色**: 比例风险回归（方法背景）
- **全文**: Cox1972                  blocked  HTTP 429 @api.semanticscholar.org
- **稿件中支撑句**:
  - “For recurrent events with informative censoring, semiparametric estimators exist but require modelling the censoring mechanism  \citep {Wang2001,Prentice1981, Aalen1978,Andersen1993,Cox1972,Lin1995}.”
  - “ \subsection {Estimation} We estimate $ \phi $ by the age-stratified Mantel--Haenszel rate ratio  \citep {Mantel1959} with one-year strata, using B-state versus N-state person-time and events, which is robust to the strong age dependence of the baseline intensity  \citep {Cox1972}.”
  - “The deferred arm keeps observing pipes at exactly the ages where the two worlds diverge, and its breaks are counted against a randomised exposure, so selection is absent by construction  \citep {Mantel1959,Cox1972}.”

## Mantel1959
- **题名**: Statistical Aspects of the Analysis of Data From Retrospective Studies of Disease
- **出处**: JNCI: Journal of the National Cancer Institute (1959)  **DOI**: 10.1093/jnci/22.4.719
- **论证角色**: 分层率比估计（本文 φ̂ 的估计量）
- **全文**: Mantel1959               10.1093/jnci/22.4.719                paywalled-or-blocked   https://pubmed.ncbi.nlm.nih.gov/13655060 -> HTTP 203
- **稿件中支撑句**:
  - “ \subsection {Estimation} We estimate $ \phi $ by the age-stratified Mantel--Haenszel rate ratio  \citep {Mantel1959} with one-year strata, using B-state versus N-state person-time and events, which is robust to the strong age dependence of the baseline intensity  \citep {Cox1972}.”
  - “The deferred arm keeps observing pipes at exactly the ages where the two worlds diverge, and its breaks are counted against a randomised exposure, so selection is absent by construction  \citep {Mantel1959,Cox1972}.”

## Aalen1978
- **题名**: Nonparametric Inference for a Family of Counting Processes
- **出处**: The Annals of Statistics (1978)  **DOI**: 10.1214/aos/1176344247
- **论证角色**: 计数过程非参数推断（Nelson–Aalen 的理论基础）
- **全文**: Aalen1978                10.1214/aos/1176344247               paywalled-or-blocked   http://projecteuclid.org/euclid.aos/1176344247 -> not a PDF (1060 bytes, b'<html style=')
- **稿件中支撑句**:
  - “For recurrent events with informative censoring, semiparametric estimators exist but require modelling the censoring mechanism  \citep {Wang2001,Prentice1981, Aalen1978,Andersen1993,Cox1972,Lin1995}.”

## Prentice1981
- **题名**: On the regression analysis of multivariate failure time data
- **出处**: Biometrika (1981)  **DOI**: 10.1093/biomet/68.2.373
- **论证角色**: 多变量失效时间数据的回归分析（复发事件的 marginal/conditional 框架）
- **全文**: Prentice1981             10.1093/biomet/68.2.373              paywalled-or-blocked   https://doi.org/10.2307/2335582 -> HTTP 403
- **稿件中支撑句**:
  - “For recurrent events with informative censoring, semiparametric estimators exist but require modelling the censoring mechanism  \citep {Wang2001,Prentice1981, Aalen1978,Andersen1993,Cox1972,Lin1995}.”

## Andersen1993
- **题名**: Statistical Models Based on Counting Processes
- **出处**: Springer Series in Statistics (1993)  **DOI**: 10.1007/978-1-4612-4348-9
- **论证角色**: 基于计数过程的统计模型（方法背景）
- **全文**: Andersen1993             blocked  HTTP 404 @api.semanticscholar.org
- **稿件中支撑句**:
  - “For recurrent events with informative censoring, semiparametric estimators exist but require modelling the censoring mechanism  \citep {Wang2001,Prentice1981, Aalen1978,Andersen1993,Cox1972,Lin1995}.”

## Slud1983
- **题名**: Dependent competing risks and summary survival curves
- **出处**: Biometrika (1983)  **DOI**: 10.1093/biomet/70.3.643
- **论证角色**: 相依竞争风险与边缘生存曲线不可识别（信息性删失的定性后果已知）
- **全文**: Slud1983                 10.1093/biomet/70.3.643              paywalled-or-blocked   https://doi.org/10.2307/2336500 -> HTTP 403
- **稿件中支撑句**:
  - “In competing-risks settings the marginal failure distribution is not identified without assumptions on the dependence between risks  \citep {Tsiatis1975,Crowder1994}, and dependent censoring biases marginal survival estimators in ways that can only be bounded or sensitivity-analysed  \citep {Slud1983,Zheng1995,Scharfstein1999}.”
  - “This is the operational content of non-identifiability in competing-risks and dependent-censoring settings  \citep {Tsiatis1975,Crowder1994,Slud1983,Manski2003}: the window fixes one point of the cumulative-hazard curve, and the extrapolation beyond it is a choice of shape, not a measurement.”

## Zheng1995
- **题名**: Estimates of marginal survival for dependent competing risks based on an assumed copula
- **出处**: Biometrika (1995)  **DOI**: 10.1093/biomet/82.1.127
- **论证角色**: 基于 copula 的相依竞争风险边缘生存估计
- **全文**: Zheng1995                10.1093/biomet/82.1.127              paywalled-or-blocked   https://doi.org/10.2307/2337633 -> HTTP 403
- **稿件中支撑句**:
  - “In competing-risks settings the marginal failure distribution is not identified without assumptions on the dependence between risks  \citep {Tsiatis1975,Crowder1994}, and dependent censoring biases marginal survival estimators in ways that can only be bounded or sensitivity-analysed  \citep {Slud1983,Zheng1995,Scharfstein1999}.”

## Tsiatis1975
- **题名**: A nonidentifiability aspect of the problem of competing risks.
- **出处**: Proceedings of the National Academy of Sciences (1975)  **DOI**: 10.1073/pnas.72.1.20
- **论证角色**: 竞争风险的不可识别性（部分识别的思想源头）
- **全文**: Tsiatis1975              blocked  HTTP 404 @api.semanticscholar.org
- **稿件中支撑句**:
  - “In competing-risks settings the marginal failure distribution is not identified without assumptions on the dependence between risks  \citep {Tsiatis1975,Crowder1994}, and dependent censoring biases marginal survival estimators in ways that can only be bounded or sensitivity-analysed  \citep {Slud1983,Zheng1995,Scharfstein1999}.”
  - “This is the operational content of non-identifiability in competing-risks and dependent-censoring settings  \citep {Tsiatis1975,Crowder1994,Slud1983,Manski2003}: the window fixes one point of the cumulative-hazard curve, and the extrapolation beyond it is a choice of shape, not a measurement.”
  - “Claims about 60- or 90-year-old pipes made from these records are claims about a chosen shape, not measurements --- a point the competing-risks literature has made for half a century  \citep {Tsiatis1975,Crowder1994} and that the water-domain corrected estimators  \citep {Scheidegger2013,LeGat2013} implicitly inherit.”

## Crowder1994
- **题名**: Identifiability Crises in Competing Risks
- **出处**: International Statistical Review / Revue Internationale de Statistique (1994)  **DOI**: 10.2307/1403768
- **论证角色**: 竞争风险中的可识别性危机
- **全文**: Crowder1994              10.2307/1403768                      paywalled-or-blocked   https://doi.org/10.2307/1403768 -> not a PDF (3038 bytes, b'<!DOCTYPE ht')
- **稿件中支撑句**:
  - “In competing-risks settings the marginal failure distribution is not identified without assumptions on the dependence between risks  \citep {Tsiatis1975,Crowder1994}, and dependent censoring biases marginal survival estimators in ways that can only be bounded or sensitivity-analysed  \citep {Slud1983,Zheng1995,Scharfstein1999}.”
  - “This is the operational content of non-identifiability in competing-risks and dependent-censoring settings  \citep {Tsiatis1975,Crowder1994,Slud1983,Manski2003}: the window fixes one point of the cumulative-hazard curve, and the extrapolation beyond it is a choice of shape, not a measurement.”
  - “Claims about 60- or 90-year-old pipes made from these records are claims about a chosen shape, not measurements --- a point the competing-risks literature has made for half a century  \citep {Tsiatis1975,Crowder1994} and that the water-domain corrected estimators  \citep {Scheidegger2013,LeGat2013} implicitly inherit.”

## Scharfstein1999
- **题名**: Adjusting for Nonignorable Drop-Out Using Semiparametric Nonresponse Models
- **出处**: Journal of the American Statistical Association (1999)  **DOI**: 10.1080/01621459.1999.10473862
- **论证角色**: 非可忽略退出的半参数非响应模型（敏感性分析范式）
- **全文**: Scharfstein1999          10.1080/01621459.1999.10473862       paywalled-or-blocked   https://doi.org/10.1080/01621459.1999.10473862 -> HTTP 403
- **稿件中支撑句**:
  - “In competing-risks settings the marginal failure distribution is not identified without assumptions on the dependence between risks  \citep {Tsiatis1975,Crowder1994}, and dependent censoring biases marginal survival estimators in ways that can only be bounded or sensitivity-analysed  \citep {Slud1983,Zheng1995,Scharfstein1999}.”

## Wang2001
- **题名**: Analyzing Recurrent Event Data With Informative Censoring
- **出处**: Journal of the American Statistical Association (2001)  **DOI**: 10.1198/016214501753209031
- **论证角色**: 带信息性删失的复发事件数据分析
- **全文**: Wang2001                 blocked  HTTP 429 @api.semanticscholar.org
- **稿件中支撑句**:
  - “For recurrent events with informative censoring, semiparametric estimators exist but require modelling the censoring mechanism  \citep {Wang2001,Prentice1981, Aalen1978,Andersen1993,Cox1972,Lin1995}.”

## Lin1995
- **题名**: Semiparametric Analysis of General Additive-Multiplicative Hazard Models for Counting Processes
- **出处**: The Annals of Statistics (1995)  **DOI**: 10.1214/aos/1176324320
- **论证角色**: 加性—乘性危险模型的半参数分析
- **全文**: Lin1995                  blocked  HTTP 429 @api.semanticscholar.org
- **稿件中支撑句**:
  - “For recurrent events with informative censoring, semiparametric estimators exist but require modelling the censoring mechanism  \citep {Wang2001,Prentice1981, Aalen1978,Andersen1993,Cox1972,Lin1995}.”

## Bartlett2014
- **题名**: Improving upon the efficiency of complete case analysis when covariates are MNAR
- **出处**: Biostatistics (2014)  **DOI**: 10.1093/biostatistics/kxu023
- **论证角色**: 缺失非随机时完整病例分析的效率改进；明确用于审计既往研究的偏差量级
- **全文**: Bartlett2014             blocked  HTTP 429 @api.semanticscholar.org
- **稿件中支撑句**:
  - “Partial identification provides the natural language for the resulting limits: some quantities are bounded, not point-estimated  \citep {Manski2003,Tamer2010}, and quantifying such bias bounds is precisely how one should audit studies that use administratively censored records  \citep {Bartlett2014}.”
  - “Bounded-but-signed is often decision-sufficient, and it is the correct language for records whose censoring is informative  \citep {Manski2003,Bartlett2014}.”
  - “ \subsection {Relation to prior work} The corrected-estimator route of  \citet {Scheidegger2013} and  \citet {LeGat2013} and the audit route of  \citet {Bartlett2014} are complementary to what we do here: we neither propose a new estimator nor a new correction, but (a) document a record-linkage defect that any of those methods would silently absorb, (b) give the horizon construct  \eqref {eq:SI}--(P3) that makes ``how far can we see'' a number rather than a slogan, and (c) show that the ambiguity a horizon implies is resolvable by a randomised deferral of exactly the kind that reliability theo”

## Manski2003
- **题名**: Partial Identification of Probability Distributions
- **出处**: Springer Series in Statistics (2003)  **DOI**: 10.1007/b97478
- **论证角色**: 部分识别（bounding）范式
- **全文**: Manski2003               blocked  HTTP 429 @api.semanticscholar.org
- **稿件中支撑句**:
  - “Partial identification provides the natural language for the resulting limits: some quantities are bounded, not point-estimated  \citep {Manski2003,Tamer2010}, and quantifying such bias bounds is precisely how one should audit studies that use administratively censored records  \citep {Bartlett2014}.”
  - “This is the operational content of non-identifiability in competing-risks and dependent-censoring settings  \citep {Tsiatis1975,Crowder1994,Slud1983,Manski2003}: the window fixes one point of the cumulative-hazard curve, and the extrapolation beyond it is a choice of shape, not a measurement.”
  - “Bounded-but-signed is often decision-sufficient, and it is the correct language for records whose censoring is informative  \citep {Manski2003,Bartlett2014}.”

## Tamer2010
- **题名**: Partial Identification in Econometrics
- **出处**: Annual Review of Economics (2010)  **DOI**: 10.1146/annurev.economics.050708.143401
- **论证角色**: 计量经济学中的部分识别综述
- **全文**: Tamer2010                blocked  ReadTimeout
- **稿件中支撑句**:
  - “Partial identification provides the natural language for the resulting limits: some quantities are bounded, not point-estimated  \citep {Manski2003,Tamer2010}, and quantifying such bias bounds is precisely how one should audit studies that use administratively censored records  \citep {Bartlett2014}.”

## Hardt2025
- **题名**: Performative Prediction: Past and Future
- **出处**: Statistical Science (2025)  **DOI**: 10.1214/25-sts986
- **论证角色**: Performative prediction（政策—数据反馈回路已被命名）
- **全文**: Hardt2025                blocked  HTTP 404 @api.semanticscholar.org
- **稿件中支撑句**:
  - “When the extrapolation is wrong, renewal programmes inherit the error; and because renewal itself shapes the records, the error can be self-reinforcing, a mechanism now studied formally as performative feedback in machine learning systems  \citep {Hardt2025}.”

## Drent2020
- **题名**: Censored lifetime learning: Optimal Bayesian age-replacement policies
- **出处**: Operations Research Letters (2020)  **DOI**: 10.1016/j.orl.2020.10.005
- **论证角色**: 删失寿命学习：贝叶斯年龄更换（单机视角的近邻工作）
- **全文**: Drent2020                10.1016/j.orl.2020.10.005            paywalled-or-blocked   https://research.tue.nl/nl/publications/5121c525-1b97-4e69-ab4b-4ab053 -> not a PDF (49125 bytes, b'\n\n\n\n<!DOCTYP')
- **稿件中支撑句**:
  - “Related ``learning under censoring'' issues arise for single machines, where optimal age-replacement policies deliberately remove the units whose failures would be most informative  \citep {BarlowProschan1965,Drent2020}.”
  - “Unlike the learning-versus-downtime trade-offs studied for single machines  \citep {Drent2020,BarlowProschan1965}, the deferred asset here is one of 13,921, and the randomised arm is a tiny fraction of the renewal programme; the design's cost is $m$ additional breaks spread over a year, not a change of policy.”
  - “ \subsection {Relation to prior work} The corrected-estimator route of  \citet {Scheidegger2013} and  \citet {LeGat2013} and the audit route of  \citet {Bartlett2014} are complementary to what we do here: we neither propose a new estimator nor a new correction, but (a) document a record-linkage defect that any of those methods would silently absorb, (b) give the horizon construct  \eqref {eq:SI}--(P3) that makes ``how far can we see'' a number rather than a slogan, and (c) show that the ambiguity a horizon implies is resolvable by a randomised deferral of exactly the kind that reliability theo”

## BarlowProschan1965
- **题名**: Mathematical Theory of Reliability
- **出处**: Society for Industrial and Applied Mathematics (1996)  **DOI**: 10.1137/1.9781611971194
- **论证角色**: 可靠性数学理论（年龄更换教科书公式）
- **全文**: BarlowProschan1965       blocked  HTTP 404 @api.semanticscholar.org
- **稿件中支撑句**:
  - “Related ``learning under censoring'' issues arise for single machines, where optimal age-replacement policies deliberately remove the units whose failures would be most informative  \citep {BarlowProschan1965,Drent2020}.”
  - “Unlike the learning-versus-downtime trade-offs studied for single machines  \citep {Drent2020,BarlowProschan1965}, the deferred asset here is one of 13,921, and the randomised arm is a tiny fraction of the renewal programme; the design's cost is $m$ additional breaks spread over a year, not a change of policy.”
  - “ \subsection {Relation to prior work} The corrected-estimator route of  \citet {Scheidegger2013} and  \citet {LeGat2013} and the audit route of  \citet {Bartlett2014} are complementary to what we do here: we neither propose a new estimator nor a new correction, but (a) document a record-linkage defect that any of those methods would silently absorb, (b) give the horizon construct  \eqref {eq:SI}--(P3) that makes ``how far can we see'' a number rather than a slogan, and (c) show that the ambiguity a horizon implies is resolvable by a randomised deferral of exactly the kind that reliability theo”
