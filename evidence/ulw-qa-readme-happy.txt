Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

새로운 기능 및 개선 사항에 대 한 최신 PowerShell을 설치 하세요! https://aka.ms/P
SWindows

PSReadline 모듈을 로드할 수 없습니다. PSReadline 없이 콘솔이 실행되고 있습니다.
PS C:\Users\wjfeo\dev\resume-claim-ledger> Remove-Item -ErrorAction SilentlyCont
inue $env:TEMP\readme-claims.yml,$env:TEMP\readme-report.md,$env:TEMP\readme-adv
ice.md; uv run resume-ledger scan qa/sample-resume.md --out $env:TEMP\readme-cla
ims.yml; uv run resume-ledger review $env:TEMP\readme-claims.yml; uv run resume-
ledger report $env:TEMP\readme-claims.yml --out $env:TEMP\readme-report.md; uv r
un resume-ledger advise $env:TEMP\readme-claims.yml --out $env:TEMP\readme-advic
e.md; if ((Test-Path $env:TEMP\readme-claims.yml) -and (Test-Path $env:TEMP\read
me-report.md) -and (Test-Path $env:TEMP\readme-advice.md)) { Write-Output happy_
PASS } else { Write-Output happy_FAIL }
Wrote 3 claims to C:\Users\wjfeo\AppData\Local\Temp\readme-claims.yml
       Claim Review
┏━━━━━━━━━━━━━━━━┳━━━━━━━┓
┃ Status         ┃ Count ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━┩
│ verified       │     1 │
│ needs_evidence │     1 │
│ too_broad      │     1 │
│ rewrite_needed │     0 │
└────────────────┴───────┘
Wrote report to C:\Users\wjfeo\AppData\Local\Temp\readme-report.md
Wrote advice to C:\Users\wjfeo\AppData\Local\Temp\readme-advice.md
happy_PASS
PS C:\Users\wjfeo\dev\resume-claim-ledger>
