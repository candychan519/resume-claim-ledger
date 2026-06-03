Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

새로운 기능 및 개선 사항에 대 한 최신 PowerShell을 설치 하세요! https://aka.ms/P
SWindows

PSReadline 모듈을 로드할 수 없습니다. PSReadline 없이 콘솔이 실행되고 있습니다.
PS C:\Users\wjfeo\dev\resume-claim-ledger> Remove-Item -ErrorAction SilentlyCont
inue $env:TEMP\readme-empty.yml; uv run resume-ledger scan qa/empty-resume.md --
out $env:TEMP\readme-empty.yml; Select-String -Path $env:TEMP\readme-empty.yml -
Pattern "schema_version: 1"; Write-Output empty_PASS
Wrote 0 claims to C:\Users\wjfeo\AppData\Local\Temp\readme-empty.yml

C:\Users\wjfeo\AppData\Local\Temp\readme-empty.yml:1:schema_version: 1
empty_PASS


PS C:\Users\wjfeo\dev\resume-claim-ledger>






