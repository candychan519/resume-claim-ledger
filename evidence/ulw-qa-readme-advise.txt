Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

새로운 기능 및 개선 사항에 대 한 최신 PowerShell을 설치 하세요! https://aka.ms/P
SWindows

PSReadline 모듈을 로드할 수 없습니다. PSReadline 없이 콘솔이 실행되고 있습니다.
PS C:\Users\wjfeo\dev\resume-claim-ledger> Remove-Item -ErrorAction SilentlyCont
inue $env:TEMP\readme-advice-claims.yml,$env:TEMP\readme-advice-claims.before.ym
l,$env:TEMP\readme-advice.md; Copy-Item qa/claims.yml $env:TEMP\readme-advice-cl
aims.yml; Copy-Item $env:TEMP\readme-advice-claims.yml $env:TEMP\readme-advice-c
laims.before.yml; uv run resume-ledger advise $env:TEMP\readme-advice-claims.yml
 --out $env:TEMP\readme-advice.md; $diff=Compare-Object (Get-Content $env:TEMP\r
eadme-advice-claims.before.yml) (Get-Content $env:TEMP\readme-advice-claims.yml)
; if ($null -eq $diff) { Write-Output advise_PASS } else { Write-Output advise_F
AIL }
Wrote advice to C:\Users\wjfeo\AppData\Local\Temp\readme-advice.md
advise_PASS
PS C:\Users\wjfeo\dev\resume-claim-ledger>





