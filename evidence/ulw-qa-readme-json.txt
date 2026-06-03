Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

새로운 기능 및 개선 사항에 대 한 최신 PowerShell을 설치 하세요! https://aka.ms/P
SWindows

PSReadline 모듈을 로드할 수 없습니다. PSReadline 없이 콘솔이 실행되고 있습니다.
PS C:\Users\wjfeo\dev\resume-claim-ledger> Remove-Item -ErrorAction SilentlyCont
inue $env:TEMP\readme-advice.json; uv run resume-ledger advise qa/claims.yml --f
ormat json --out $env:TEMP\readme-advice.json; Select-String -Path $env:TEMP\rea
dme-advice.json -Pattern "`"schema_version`": 1"; Select-String -Path $env:TEMP\
readme-advice.json -Pattern "`"suggestions`""; Write-Output json_PASS
Wrote advice to C:\Users\wjfeo\AppData\Local\Temp\readme-advice.json

C:\Users\wjfeo\AppData\Local\Temp\readme-advice.json:2:  "schema_version": 1,
C:\Users\wjfeo\AppData\Local\Temp\readme-advice.json:3:  "suggestions": [
json_PASS


PS C:\Users\wjfeo\dev\resume-claim-ledger>




