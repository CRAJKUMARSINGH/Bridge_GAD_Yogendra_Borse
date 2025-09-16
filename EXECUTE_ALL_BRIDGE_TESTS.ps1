# EXECUTE ALL BRIDGE APPLICATIONS TESTING
# Author: Rajkumar Singh Chauhan
Write-Host "🌉 EXECUTING ALL BRIDGE APPLICATION TESTS" -ForegroundColor Green

$timestamp = Get-Date -Format "dd_MM_yyyy_HHmm"
$baseOutputDir = "C:\Users\Rajkumar\BridgeGAD-00\OUTPUT_$timestamp"
$inputFilesDir = "C:\Users\Rajkumar\BridgeGAD-00\SAMPLE_INPUT_FILES"

# Create directories
New-Item -ItemType Directory -Path $baseOutputDir -Force | Out-Null
New-Item -ItemType Directory -Path $inputFilesDir -Force | Out-Null

# Test configurations for each app
$bridgeTests = @(
    @{ Name = "BridgeGAD-00"; Path = "C:\Users\Rajkumar\BridgeGAD-00"; MainApp = "app.py"; HasInput = $true },
    @{ Name = "BridgeGAD-01"; Path = "C:\Users\Rajkumar\BridgeGAD-01"; MainApp = "run_bridge_generator.py"; HasInput = $false },
    @{ Name = "BridgeGAD-02"; Path = "C:\Users\Rajkumar\BridgeGAD-02"; MainApp = "main.py"; HasInput = $false },
    @{ Name = "BridgeGAD-03"; Path = "C:\Users\Rajkumar\BridgeGAD-03"; MainApp = "app.py"; HasInput = $true },
    @{ Name = "BridgeGAD-04"; Path = "C:\Users\Rajkumar\BridgeGAD-04"; MainApp = "app.py"; HasInput = $true },
    @{ Name = "BridgeGAD-06"; Path = "C:\Users\Rajkumar\BridgeGAD-06"; MainApp = "main.py"; HasInput = $true },
    @{ Name = "BridgeGAD-07"; Path = "C:\Users\Rajkumar\BridgeGAD-07"; MainApp = "main.py"; HasInput = $false },
    @{ Name = "BridgeGAD-10"; Path = "C:\Users\Rajkumar\BridgeGAD-10"; MainApp = "main.py"; HasInput = $false },
    @{ Name = "BridgeGAD-12"; Path = "C:\Users\Rajkumar\BridgeGAD-12"; MainApp = "app.py"; HasInput = $false },
    @{ Name = "Bridge_Slab_Design"; Path = "C:\Users\Rajkumar\Bridge_Slab_Design"; MainApp = "bridge_design_app.py"; HasInput = $true }
)

$testResults = @()

foreach ($test in $bridgeTests) {
    $appName = $test.Name
    $appPath = $test.Path
    $mainApp = $test.MainApp
    $hasInput = $test.HasInput
    
    Write-Host "`n🔧 Testing: $appName" -ForegroundColor Cyan
    
    if (Test-Path $appPath) {
        # Create app-specific output directory
        $appOutputDir = "$baseOutputDir\$appName"
        New-Item -ItemType Directory -Path $appOutputDir -Force | Out-Null
        
        # Change to app directory
        Push-Location $appPath
        
        try {
            # Check if main app exists
            if (Test-Path $mainApp) {
                Write-Host "   📁 Found main app: $mainApp" -ForegroundColor Green
                
                # Prepare input file if needed
                $inputFile = ""
                if ($hasInput) {
                    $inputFile = Get-ChildItem "*.xlsx" | Select-Object -First 1
                    if ($inputFile) {
                        $inputFile = $inputFile.Name
                        Write-Host "   📄 Using input: $inputFile" -ForegroundColor Yellow
                        
                        # Copy input to sample files directory
                        $sampleInputPath = "$inputFilesDir\sample_$appName.xlsx"
                        if (-not (Test-Path $sampleInputPath)) {
                            Copy-Item $inputFile $sampleInputPath -Force
                            Write-Host "   💾 Saved sample input: $sampleInputPath" -ForegroundColor Blue
                        }
                    }
                }
                
                # Execute the application
                $outputFile = "$appOutputDir\bridge_output_$(Get-Date -Format 'HHmm').dxf"
                
                if ($hasInput -and $inputFile) {
                    Write-Host "   🏃 Running: python $mainApp $inputFile $outputFile" -ForegroundColor Magenta
                    $output = python $mainApp $inputFile $outputFile 2>&1
                } else {
                    Write-Host "   🏃 Running: python $mainApp" -ForegroundColor Magenta
                    $output = python $mainApp 2>&1
                }
                
                # Check if output was created
                $outputCreated = Test-Path $outputFile
                
                $result = @{
                    AppName = $appName
                    Status = if ($outputCreated) { "SUCCESS" } else { "PARTIAL" }
                    MainApp = $mainApp
                    InputFile = $inputFile
                    OutputFile = $outputFile
                    OutputCreated = $outputCreated
                    ExecutionOutput = $output -join "`n"
                    TestTime = Get-Date
                }
                
                if ($outputCreated) {
                    Write-Host "   ✅ SUCCESS: Output created" -ForegroundColor Green
                } else {
                    Write-Host "   ⚠️  PARTIAL: App ran but no output file" -ForegroundColor Yellow
                }
                
            } else {
                Write-Host "   ❌ Main app not found: $mainApp" -ForegroundColor Red
                $result = @{
                    AppName = $appName
                    Status = "APP_NOT_FOUND"
                    MainApp = $mainApp
                    InputFile = ""
                    OutputFile = ""
                    OutputCreated = $false
                    ExecutionOutput = "Main app file not found"
                    TestTime = Get-Date
                }
            }
            
        } catch {
            Write-Host "   ❌ ERROR: $_" -ForegroundColor Red
            $result = @{
                AppName = $appName
                Status = "ERROR"
                MainApp = $mainApp
                InputFile = ""
                OutputFile = ""
                OutputCreated = $false
                ExecutionOutput = $_.ToString()
                TestTime = Get-Date
            }
        } finally {
            Pop-Location
        }
        
    } else {
        Write-Host "   ❌ Directory not found: $appPath" -ForegroundColor Red
        $result = @{
            AppName = $appName
            Status = "DIR_NOT_FOUND"
            MainApp = $mainApp
            InputFile = ""
            OutputFile = ""
            OutputCreated = $false
            ExecutionOutput = "Directory not found"
            TestTime = Get-Date
        }
    }
    
    $testResults += $result
}

# Generate comprehensive test report
$reportPath = "$baseOutputDir\COMPREHENSIVE_TEST_REPORT.json"
$testResults | ConvertTo-Json -Depth 10 | Out-File $reportPath -Encoding UTF8

# Generate summary
$successCount = ($testResults | Where-Object { $_.Status -eq "SUCCESS" }).Count
$partialCount = ($testResults | Where-Object { $_.Status -eq "PARTIAL" }).Count
$errorCount = ($testResults | Where-Object { $_.Status -in @("ERROR", "APP_NOT_FOUND", "DIR_NOT_FOUND") }).Count

Write-Host "`n🎉 TESTING COMPLETED!" -ForegroundColor Green
Write-Host "===================" -ForegroundColor Green
Write-Host "✅ Successful: $successCount" -ForegroundColor Green
Write-Host "⚠️  Partial: $partialCount" -ForegroundColor Yellow
Write-Host "❌ Failed: $errorCount" -ForegroundColor Red
Write-Host "`n📊 Results saved to: $reportPath" -ForegroundColor Cyan
Write-Host "📁 Output directory: $baseOutputDir" -ForegroundColor Cyan
Write-Host "📄 Sample inputs: $inputFilesDir" -ForegroundColor Cyan

Set-Location "C:\Users\Rajkumar\BridgeGAD-00"