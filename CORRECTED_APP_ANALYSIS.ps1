# CORRECTED INDIVIDUAL BRIDGE APPLICATION ANALYSIS
Write-Host "Analyzing Each Bridge Application Individually..." -ForegroundColor Green

$timestamp = Get-Date -Format "dd_MM_yyyy_HHmm"
$baseOutputDir = "C:\Users\Rajkumar\BridgeGAD-00\INDIVIDUAL_APP_ANALYSIS_$timestamp"
$analysisDir = "$baseOutputDir\Analysis"

New-Item -ItemType Directory -Path $baseOutputDir -Force | Out-Null
New-Item -ItemType Directory -Path $analysisDir -Force | Out-Null

$bridgeApps = @(
    @{ Name = "BridgeGAD-00"; Path = "C:\Users\Rajkumar\BridgeGAD-00"; Apps = @("app.py", "enhanced_bridge_app.py", "rajkumar_app.py") },
    @{ Name = "BridgeGAD-01"; Path = "C:\Users\Rajkumar\BridgeGAD-01"; Apps = @("streamlit_app.py", "bridge_drawings.py") },
    @{ Name = "BridgeGAD-02"; Path = "C:\Users\Rajkumar\BridgeGAD-02"; Apps = @("main.py", "app.py", "bridge_generator.py") },
    @{ Name = "BridgeGAD-03"; Path = "C:\Users\Rajkumar\BridgeGAD-03"; Apps = @("app.py", "enhanced_bridge_app.py") },
    @{ Name = "BridgeGAD-04"; Path = "C:\Users\Rajkumar\BridgeGAD-04"; Apps = @("app.py", "bridge_drawer.py") },
    @{ Name = "BridgeGAD-06"; Path = "C:\Users\Rajkumar\BridgeGAD-06"; Apps = @("main.py", "streamlit_app.py") },
    @{ Name = "BridgeGAD-07"; Path = "C:\Users\Rajkumar\BridgeGAD-07"; Apps = @("main.py", "app.py") },
    @{ Name = "BridgeGAD-10"; Path = "C:\Users\Rajkumar\BridgeGAD-10"; Apps = @("main.py", "app.py") },
    @{ Name = "BridgeGAD-12"; Path = "C:\Users\Rajkumar\BridgeGAD-12"; Apps = @("app.py") },
    @{ Name = "Bridge_Slab_Design"; Path = "C:\Users\Rajkumar\Bridge_Slab_Design"; Apps = @("bridge_design_app.py") }
)

$results = @()

foreach ($app in $bridgeApps) {
    Write-Host "`nAnalyzing: $($app.Name)" -ForegroundColor Cyan
    
    $appDir = "$analysisDir\$($app.Name)"
    New-Item -ItemType Directory -Path $appDir -Force | Out-Null
    
    if (Test-Path $app.Path) {
        Push-Location $app.Path
        
        try {
            # Find input files
            $inputFiles = @{
                Excel = (Get-ChildItem "*.xlsx" -ErrorAction SilentlyContinue).Name
                CSV = (Get-ChildItem "*.csv" -ErrorAction SilentlyContinue).Name
                JSON = (Get-ChildItem "*.json" -ErrorAction SilentlyContinue).Name
                YAML = (Get-ChildItem "*.yaml", "*.yml" -ErrorAction SilentlyContinue).Name
                Text = (Get-ChildItem "*.txt" -ErrorAction SilentlyContinue).Name
                Config = (Get-ChildItem "config*" -ErrorAction SilentlyContinue).Name
            }
            
            # Analyze each app file
            $appAnalysis = @()
            foreach ($appFile in $app.Apps) {
                if (Test-Path $appFile) {
                    Write-Host "  Found: $appFile" -ForegroundColor Green
                    
                    # Try to understand input requirements
                    $content = Get-Content $appFile -Head 20 -ErrorAction SilentlyContinue
                    $inputHints = @()
                    
                    if ($content) {
                        $inputHints = $content | Where-Object { 
                            $_ -match "sys\.argv|input|Input|\.xlsx|\.csv|\.json|\.yaml|file|File" 
                        } | Select-Object -First 3
                    }
                    
                    $appAnalysis += @{
                        File = $appFile
                        InputHints = $inputHints
                        Exists = $true
                    }
                } else {
                    $appAnalysis += @{
                        File = $appFile
                        InputHints = @()
                        Exists = $false
                    }
                }
            }
            
            # Display findings
            foreach ($type in $inputFiles.Keys) {
                if ($inputFiles[$type].Count -gt 0) {
                    Write-Host "  $type files: $($inputFiles[$type] -join ', ')" -ForegroundColor Blue
                }
            }
            
            $result = @{
                App = $app.Name
                Path = $app.Path
                InputFiles = $inputFiles
                AppAnalysis = $appAnalysis
                Status = "SUCCESS"
                Time = Get-Date
            }
            
        } catch {
            Write-Host "  Error: $_" -ForegroundColor Red
            $result = @{
                App = $app.Name
                Path = $app.Path
                InputFiles = @{}
                AppAnalysis = @()
                Status = "ERROR"
                Error = $_.ToString()
                Time = Get-Date
            }
        } finally {
            Pop-Location
        }
        
    } else {
        Write-Host "  Directory not found" -ForegroundColor Red
        $result = @{
            App = $app.Name
            Path = $app.Path
            InputFiles = @{}
            AppAnalysis = @()
            Status = "NOT_FOUND"
            Time = Get-Date
        }
    }
    
    $results += $result
}

# Save results
$reportPath = "$analysisDir\analysis_results.json"
$results | ConvertTo-Json -Depth 10 | Out-File $reportPath -Encoding UTF8

Write-Host "`nAnalysis completed!" -ForegroundColor Green
Write-Host "Results saved to: $analysisDir" -ForegroundColor Cyan

# Display summary
Write-Host "`nSummary:" -ForegroundColor Yellow
foreach ($result in $results) {
    $totalInputs = ($result.InputFiles.Values | Where-Object { $_ } | Measure-Object).Count
    Write-Host "  $($result.App): $($result.Status) - $totalInputs input file types found" -ForegroundColor White
}

Set-Location "C:\Users\Rajkumar\BridgeGAD-00"