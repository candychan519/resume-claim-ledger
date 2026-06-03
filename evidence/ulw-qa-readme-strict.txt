Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

새로운 기능 및 개선 사항에 대 한 최신 PowerShell을 설치 하세요! https://aka.ms/P
SWindows

PSReadline 모듈을 로드할 수 없습니다. PSReadline 없이 콘솔이 실행되고 있습니다.
PS C:\Users\wjfeo\dev\resume-claim-ledger> Remove-Item -ErrorAction SilentlyCont
inue $env:TEMP\readme-strict.md; uv run resume-ledger report qa/claims.yml --out
 $env:TEMP\readme-strict.md --strict; $code=$LASTEXITCODE; Write-Output "strict_
exit:$code"; if ($code -ne 0) { Write-Output strict_PASS } else { Write-Output s
trict_FAIL }
Wrote report to C:\Users\wjfeo\AppData\Local\Temp\readme-strict.md
Strict mode blocked unresolved claim statuses: needs_evidence, too_broad
strict_exit:1
strict_PASS
PS C:\Users\wjfeo\dev\resume-claim-ledger>







