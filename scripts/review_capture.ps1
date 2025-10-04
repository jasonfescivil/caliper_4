param(
    [string]$Question1 = "What are the G1 requirements for engineering reports?",
    [string]$Question2 = "Infiltration basin drawdown criteria",
    [string]$Question3 = "Define peak hour factor",
    [string]$Indexes = "federal,state,design_standards"
)

$ErrorActionPreference = 'Continue'

function New-ReviewFolder {
  $ts = Get-Date -Format 'yyyyMMdd-HHmmss'
  $root = Join-Path -Path ".artifacts\review-junie" -ChildPath $ts
  New-Item -ItemType Directory -Force -Path $root | Out-Null
  return $root
}

function Write-Section($path, $title) {
  Add-Content -Path $path -Value ("`n==== {0} ====`n" -f $title)
}

$root = New-ReviewFolder
$sessionLog = Join-Path $root 'session_transcript.txt'
Start-Transcript -Path $sessionLog -Force | Out-Null

# 1) Environment & deps
$envFile = Join-Path $root 'env_and_deps.txt'
Write-Output "Python/Poetry/Package Versions" | Tee-Object -FilePath $envFile
try { poetry --version 2>&1 | Tee-Object -FilePath $envFile -Append } catch {}
try { python --version 2>&1 | Tee-Object -FilePath $envFile -Append } catch {}
try { poetry show 2>&1 | Tee-Object -FilePath $envFile -Append } catch {}

# Env var presence
$envReport = Join-Path $root 'env_vars.txt'
$need = @('LLAMA_CLOUD_API_KEY','COHERE_API_KEY','OPENAI_API_KEY','ANTHROPIC_API_KEY','GEMINI_API_KEY','XAI_API_KEY',
          'FEDERAL_BASE_ID','FEDERAL_SUMMARY_ID','STATE_BASE_ID','STATE_SUMMARY_ID','DESIGN_BASE_ID','DESIGN_SUMMARY_ID')
foreach ($k in $need) {
  $v = if (Test-Path Env:$k) { 'present' } else { 'missing' }
  Add-Content -Path $envReport -Value ("{0}={1}" -f $k,$v)
}

# 2) Static sweep
$staticOut = Join-Path $root 'static_sweep.txt'
try { Select-String -Path 'src\**\*.py' -Pattern 'TODO','XXX','FIXME' -SimpleMatch -Recurse -ErrorAction SilentlyContinue | Out-File -FilePath $staticOut -Encoding utf8 } catch {}

# 3) Reverse dependency sketch: entrypoints and CLI help
$cliOut = Join-Path $root 'cli_help.txt'
try { poetry run caliper_v2 --help 2>&1 | Tee-Object -FilePath $cliOut } catch {}

# 4) Runtime traces (3 reps)
$hasCloud = Test-Path Env:LLAMA_CLOUD_API_KEY

# Cloud or local example 1
$ctx1 = Join-Path $root 'ctx_g1.json'
if ($hasCloud) {
  $cmd1 = @('poetry','run','caliper_v2','retrieve',"$Question1","--indexes","$Indexes","--cloud","--dense-k","12","--sparse-k","12","--alpha","0.5","--rerank-top-n","12","--out","$ctx1")
} else {
  $cmd1 = @('poetry','run','caliper_v2','retrieve',"$Question1","--indexes","design_standards","--search-mode","hybrid","--top-k","60","--reranker","st-mini","--out","$ctx1")
}
$log1 = Join-Path $root 'trace_retrieve_1.txt'
try { & $cmd1 2>&1 | Tee-Object -FilePath $log1 } catch {}

# Local example 2
$ctx2 = Join-Path $root 'ctx_drawdown.json'
$cmd2 = @('poetry','run','caliper_v2','retrieve',"$Question2","--indexes","design_standards","--search-mode","hybrid","--top-k","60","--reranker","st-mini","--out","$ctx2")
$log2 = Join-Path $root 'trace_retrieve_2.txt'
try { & $cmd2 2>&1 | Tee-Object -FilePath $log2 } catch {}

# Graph example 3 (best-effort)
$ctx3 = Join-Path $root 'ctx_graph.json'
$buildGraph = @('poetry','run','caliper_v2','graph','build','--corpus','knowledge_base','--out','data_v2/graph')
$graphLog = Join-Path $root 'trace_graph_build.txt'
try { & $buildGraph 2>&1 | Tee-Object -FilePath $graphLog } catch {}
$cmd3 = @('poetry','run','caliper_v2','graph','retrieve',"$Question3","--graph-dir","data_v2/graph","--out","$ctx3")
$log3 = Join-Path $root 'trace_retrieve_3_graph.txt'
try { & $cmd3 2>&1 | Tee-Object -FilePath $log3 } catch {}

Stop-Transcript | Out-Null

Write-Host "Artifacts written to $root"
