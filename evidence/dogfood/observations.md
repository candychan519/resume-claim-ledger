# Dogfood Observations

## Inputs
- Resume: `01_resume/current/20260531_권찬민_이력서_v1.4_MASTER_최근3축반영본.md`
- Job description: `03_applications/20251201_naver-cloud/네이버클라우드채용공고.txt`
- Evidence directory: `02_career-assets/portfolio-ppt-sourcepack/04_evidence`

## Results
- `scan` generated 52 claim records.
- `coordinate` produced this action summary:
  - `ready`: 0
  - `needs_evidence`: 51
  - `soften_wording`: 0
  - `jd_gap`: 0
  - `submission_blocker`: 1
- Source resume and JD hashes were identical before and after the dogfood run.

## Observations
- JD keyword matching surfaced relevant requirements for many platform and MLOps claims.
- Evidence matching did not connect the current portfolio evidence directory to most scanned claims because the generated ledger uses generic evidence notes such as "구체적인 근거, 지표, 산출물 링크 중 하나가 필요합니다."
- A concise summary output is useful for this real workflow because the full action report is long when a resume has 50+ claims.
- A future improvement could let users maintain explicit evidence aliases in the ledger, but this follow-up keeps the tool report-only and deterministic.
