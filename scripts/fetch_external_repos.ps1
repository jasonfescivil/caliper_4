# C:\repos\caliper_3\fetch_external_repos.ps1
# usage:
#   powershell -ExecutionPolicy Bypass -File .\fetch_external_repos.ps1

$ErrorActionPreference = "Stop"
git --version | Out-Null

# Destination: ...\docs\external_docs\<owner>\<repo>
$destRoot = Join-Path $PSScriptRoot "docs\external_docs"
New-Item -ItemType Directory -Force -Path $destRoot | Out-Null

# Long paths (harmless if already set)
git config --global core.longpaths true | Out-Null

# --- Repo catalog ---
$repos = @(
  @{ url = "https://github.com/run-llama/llama_index" }            # LlamaIndex core
  @{ url = "https://github.com/run-llama/llama_cloud_services" }   # LlamaCloud SDKs (incl. LlamaParse)
  @{ url = "https://github.com/run-llama/semtools" }               # CLI tools (parse/search)
  @{ url = "https://github.com/run-llama/create-llama" }           # App scaffold CLI
  @{ url = "https://github.com/run-llama/llama-hub" }              # Data loaders (archived)
  @{ url = "https://github.com/cohere-ai/cohere-python" }          # Cohere Python SDK
  @{ url = "https://github.com/googleapis/python-genai" }          # Google Gen AI SDK
  @{ url = "https://github.com/neo4j/neo4j-python-driver" }        # Neo4j Python driver
  @{ url = "https://github.com/fastapi/typer" }                    # Typer CLI
  @{ url = "https://github.com/Delgan/loguru" }                    # Loguru logging
  @{ url = "https://github.com/pydantic/pydantic-settings" }       # Pydantic settings
  @{ url = "https://github.com/explosion/spaCy" }                  # spaCy
  @{ url = "https://github.com/explosion/spaCy-models" }           # spaCy models (releases)
  @{ url = "https://github.com/microsoft/graphrag" }               # GraphRAG (reference)
)

function Get-OwnerRepoFromUrl([string]$url) {
  if ($url -match "github\.com/([^/]+)/([^/]+)") {
    return @($matches[1], $matches[2])
  }
  throw "Unrecognized GitHub URL format: $url"
}

function CloneOrUpdateRepo([string]$url) {
  $owner, $repo = Get-OwnerRepoFromUrl $url
  $targetDir = Join-Path $destRoot (Join-Path $owner $repo)

  if (-not (Test-Path $targetDir)) {
    New-Item -ItemType Directory -Force -Path (Split-Path $targetDir) | Out-Null
    Write-Host "Cloning $owner/$repo → $targetDir"
    git clone --depth 1 --recurse-submodules $url $targetDir
    return
  }

  if (-not (Test-Path (Join-Path $targetDir ".git"))) {
    throw "Target exists but is not a git repo: $targetDir"
  }

  Write-Host "Updating $owner/$repo in $targetDir"
  Push-Location $targetDir
  try {
    git remote set-url origin $url
    git fetch --all --prune

    # Determine branch to fast-forward:
    # 1) current HEAD if symbolic
    $branch = (git rev-parse --abbrev-ref HEAD 2>$null)
    # 2) upstream of HEAD (quote '@{u}' for PowerShell!)
    if (-not $branch -or $branch -eq "HEAD") {
      $up = (git rev-parse --abbrev-ref '@{u}' 2>$null)
      if ($up) { $branch = ($up -split "/")[-1] }
    }
    # 3) fallbacks
    if (-not $branch -or $branch -eq "HEAD") {
      $branch = "main"
      if (-not (git show-ref --verify --quiet "refs/heads/$branch")) { $branch = "master" }
    }

    git checkout $branch 2>$null
    git pull --ff-only origin $branch
  } catch {
    Write-Warning "Could not fast-forward $owner/$repo ($branch). Fetched latest refs."
  } finally {
    Pop-Location
  }
}

foreach ($r in $repos) { CloneOrUpdateRepo $r.url }

Write-Host "`nAll done. Repos are under $destRoot"
