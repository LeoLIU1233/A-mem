param(
    [string]$Model = "deepseek-chat",
    [string]$ApiBase = "https://api.deepseek.com",
    [double]$Ratio = 0.1,
    [int]$MaxTurnsPerSample = 120,
    [int]$PerCategory = 5,
    [int]$MaxQuestions = 25,
    [string]$RetrieveKMap = "",
    [int[]]$Seeds = @(42, 43, 44),
    [switch]$LegacyC5
)

$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $PSScriptRoot
$envFile = Join-Path $repo ".env"
$resultDir = Join-Path $repo "results"

if (Test-Path -LiteralPath $envFile) {
    Get-Content -LiteralPath $envFile | ForEach-Object {
        if ($_ -match '^\s*([^#][^=]+?)\s*=\s*(.*?)\s*$') {
            $name = $Matches[1]
            $value = $Matches[2].Trim('"').Trim("'")
            if (-not [Environment]::GetEnvironmentVariable($name, "Process")) {
                [Environment]::SetEnvironmentVariable($name, $value, "Process")
            }
        }
    }
}

if (-not $env:DEEPSEEK_API_KEY -and -not $env:OPENAI_API_KEY) {
    throw "Set DEEPSEEK_API_KEY (recommended) or OPENAI_API_KEY before running."
}

New-Item -ItemType Directory -Force -Path $resultDir | Out-Null
Push-Location $repo
try {
    foreach ($mode in @("full", "link_only")) {
        foreach ($seed in $Seeds) {
            $output = Join-Path $resultDir "${mode}_seed${seed}.json"
            $arguments = @(
                "test_advanced_robust.py",
                "--backend", "openai",
                "--model", $Model,
                "--api_base", $ApiBase,
                "--dataset", "data/locomo10.json",
                "--ratio", "$Ratio",
                "--max_turns_per_sample", "$MaxTurnsPerSample",
                "--per_category", "$PerCategory",
                "--max_questions", "$MaxQuestions",
                "--memory_mode", $mode,
                "--seed", "$seed",
                "--output", $output
            )
            if ($RetrieveKMap) {
                $arguments += @("--retrieve_k_map", $RetrieveKMap)
            }
            if ($LegacyC5) {
                $arguments += "--legacy_c5_reference"
            }
            Write-Host "Running mode=$mode seed=$seed"
            & python @arguments
            if ($LASTEXITCODE -ne 0) {
                throw "Evaluation failed with exit code $LASTEXITCODE"
            }
        }
    }

    $resultFiles = Get-ChildItem $resultDir -Filter "*.json" |
        Where-Object { $_.Name -match "^(full|link_only)_seed\d+\.json$" } |
        Sort-Object Name |
        ForEach-Object { $_.FullName }
    & python (Join-Path $PSScriptRoot "summarize_results.py") @resultFiles |
        Tee-Object -FilePath (Join-Path $resultDir "summary.md")
}
finally {
    Pop-Location
}
