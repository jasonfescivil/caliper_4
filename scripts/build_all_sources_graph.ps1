# Build All-Sources Graph for Caliper v2
# This creates a unified graph combining federal, state, and design sources

Write-Host "===== Building Unified Graph from All Sources =====" -ForegroundColor Cyan
Write-Host ""

# Option 1: Build from existing cloud corpus (if you have exported markdown files)
Write-Host "Option 1: Build from existing local corpus" -ForegroundColor Yellow

# Check if cloud corpus directories exist
$corpusDirs = @(
    "data_v2/cloud_corpus_federal",
    "data_v2/cloud_corpus_state", 
    "data_v2/cloud_corpus_design"
)

$existingCorpus = @()
foreach ($dir in $corpusDirs) {
    if (Test-Path $dir) {
        Write-Host "✓ Found: $dir" -ForegroundColor Green
        $existingCorpus += $dir
    } else {
        Write-Host "✗ Missing: $dir" -ForegroundColor Red
    }
}

if ($existingCorpus.Count -gt 0) {
    Write-Host ""
    Write-Host "Creating combined corpus directory..." -ForegroundColor Cyan
    
    # Create a combined corpus directory
    $combinedCorpus = "data_v2/cloud_corpus_all"
    if (!(Test-Path $combinedCorpus)) {
        New-Item -ItemType Directory -Path $combinedCorpus -Force | Out-Null
    }
    
    # Copy all markdown files from each corpus to the combined directory
    Write-Host "Copying files to combined corpus..." -ForegroundColor Cyan
    foreach ($corpus in $existingCorpus) {
        $files = Get-ChildItem -Path "$corpus" -Filter "*.md" -Recurse
        Write-Host "  Copying $($files.Count) files from $corpus" -ForegroundColor Gray
        foreach ($file in $files) {
            # Prefix filename with corpus type to avoid conflicts
            $prefix = Split-Path -Leaf $corpus
            $prefix = $prefix -replace "cloud_corpus_", ""
            $newName = "${prefix}_$($file.Name)"
            Copy-Item -Path $file.FullName -Destination "$combinedCorpus\$newName" -Force
        }
    }
    
    $totalFiles = (Get-ChildItem -Path $combinedCorpus -Filter "*.md").Count
    Write-Host "Combined corpus has $totalFiles files" -ForegroundColor Green
    Write-Host ""
    
    # Build graph from combined corpus
    Write-Host "Building graph from combined corpus..." -ForegroundColor Cyan
    Write-Host "Command:" -ForegroundColor Yellow
    $buildCmd = @"
poetry run caliper_v2 --llm-provider gemini --llm-model "models/gemini-2.5-pro" graph build --corpus $combinedCorpus --out data_v2/graph --relation-mode heuristic --k-hop 2 --rebuild
"@
    Write-Host $buildCmd -ForegroundColor White
    Write-Host ""
    
    # Execute the build
    Invoke-Expression $buildCmd
    
} else {
    Write-Host "No local corpus found. Use Option 2 to build from cloud." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host ""

# Option 2: Build directly from cloud indexes
Write-Host "Option 2: Build directly from LlamaCloud (downloads then builds)" -ForegroundColor Yellow
Write-Host ""
Write-Host "This command will:" -ForegroundColor Cyan
Write-Host "  1. Export documents from all three cloud indexes" -ForegroundColor Gray
Write-Host "  2. Build a unified graph from the exported documents" -ForegroundColor Gray
Write-Host ""

Write-Host "Command to build from cloud:" -ForegroundColor Yellow
$cloudBuildCmd = @"
poetry run caliper_v2 --llm-provider gemini --llm-model "models/gemini-2.5-pro" graph build-cloud --indexes federal,state,design --out-corpus data_v2/cloud_corpus_all --graph-out data_v2/graph --relation-mode heuristic --k-hop 2
"@
Write-Host $cloudBuildCmd -ForegroundColor White
Write-Host ""

Write-Host "Choose which option to run:" -ForegroundColor Cyan
Write-Host "  - If you have local corpus files, Option 1 was attempted above" -ForegroundColor Gray
Write-Host "  - To download fresh from cloud and build, copy and run the Option 2 command" -ForegroundColor Gray
Write-Host ""

# Check if graph was created
if (Test-Path "data_v2/graph") {
    Write-Host "===== Graph Statistics =====" -ForegroundColor Cyan
    poetry run caliper_v2 graph stats --graph-dir data_v2/graph
    
    Write-Host ""
    Write-Host "===== Testing the Graph =====" -ForegroundColor Cyan
    Write-Host "Test command:" -ForegroundColor Yellow
    $testCmd = @"
poetry run caliper_v2 --llm-provider gemini --llm-model "models/gemini-2.5-pro" graph retrieve "What are WWTP requirements?" --graph-dir data_v2/graph --hops 2 --limit 100 --out data_v2/context/test_unified_graph.json
"@
    Write-Host $testCmd -ForegroundColor White
}

Write-Host ""
Write-Host "===== Next Steps =====" -ForegroundColor Green
Write-Host "Once the graph is built, you can use it with:" -ForegroundColor Cyan
Write-Host '  poetry run caliper_v2 --llm-provider gemini --llm-model "models/gemini-2.5-pro" graph retrieve "YOUR_QUESTION" --graph-dir data_v2/graph --hops 2 --limit 200 --mix-with-text --text-indexes federal,state,design --top-k 60 --rerank-top-n 24 --out OUTPUT.json' -ForegroundColor White