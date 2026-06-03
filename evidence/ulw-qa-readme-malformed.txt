Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

새로운 기능 및 개선 사항에 대 한 최신 PowerShell을 설치 하세요! https://aka.ms/P
SWindows

PSReadline 모듈을 로드할 수 없습니다. PSReadline 없이 콘솔이 실행되고 있습니다.
PS C:\Users\wjfeo\dev\resume-claim-ledger> Remove-Item -ErrorAction SilentlyCont
inue $env:TEMP\readme-malformed-report.md; uv run resume-ledger report qa/malfor
med.yml --out $env:TEMP\readme-malformed-report.md; Select-String -Path $env:TEM
P\readme-malformed-report.md -Pattern "Malformed ledger"; Write-Output malformed
_PASS
Wrote report to C:\Users\wjfeo\AppData\Local\Temp\readme-malformed-report.md

C:\Users\wjfeo\AppData\Local\Temp\readme-malformed-report.md:18:- Malformed led
ger shape: expected claims list.
malformed_PASS


PS C:\Users\wjfeo\dev\resume-claim-ledger>




