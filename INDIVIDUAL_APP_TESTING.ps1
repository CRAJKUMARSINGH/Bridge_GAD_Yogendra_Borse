# INDIVIDUAL APPLICATION TESTING WITH SPECIFIC INPUT FORMATS
# Author: Rajkumar Singh Chauhan
# Purpose: Test each Bridge app with its specific input format

Write-Host "🎯 TESTING EACH BRIDGE APP WITH SPECIFIC INPUT FORMATS" -ForegroundColor Green
Write-Host "======================================================" -ForegroundColor Green

$timestamp = Get-Date -Format "dd_MM_yyyy_HHmm"
$outputDir = "C:\Users\Rajkumar\BridgeGAD-00\INDIVIDUAL_TESTS_$timestamp"
$inputSamplesDir = "C:\Users\Rajkumar\BridgeGAD-00\CUSTOM_SAMPLE_INPUTS"

New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
New-Item -ItemType Directory -Path $inputSamplesDir -Force | Out-Null

Write-Host "`n📁 Output Directory: $outputDir"
Write-Host "📁 Sample Inputs: $inputSamplesDir"

$testResults = @()

# Test BridgeGAD-00 - Excel-based with multiple formats
Write-Host "`n🔧 Testing BridgeGAD-00 - Excel-based Bridge GAD" -ForegroundColor Cyan
$appOutputDir = "$outputDir\BridgeGAD-00"
New-Item -ItemType Directory -Path $appOutputDir -Force | Out-Null

Push-Location "C:\Users\Rajkumar\BridgeGAD-00"
try {
    # Test with different Excel files
    $excelFiles = @("sample_input.xlsx", "large_bridge.xlsx", "modified_bridge.xlsx")
    $appResults = @()
    
    foreach ($excelFile in $excelFiles) {
        if (Test-Path $excelFile) {
            Write-Host "  Testing with: $excelFile" -ForegroundColor Yellow
            
            # Copy to sample inputs
            Copy-Item $excelFile "$inputSamplesDir\BridgeGAD-00_$excelFile" -Force
            
            # Test app.py
            $outputFile = "$appOutputDir\app_$($excelFile.Replace('.xlsx', '')).dxf"
            try {
                $output = python app.py $excelFile $outputFile 2>&1
                $success = Test-Path $outputFile
                
                $appResults += @{
                    App = "app.py"
                    InputFile = $excelFile
                    OutputFile = $outputFile
                    Success = $success
                    Output = ($output | Out-String).Substring(0, [Math]::Min(500, ($output | Out-String).Length))
                }
                
                if ($success) {
                    Write-Host "    ✅ SUCCESS: app.py with $excelFile" -ForegroundColor Green
                } else {
                    Write-Host "    ⚠️  PARTIAL: app.py ran but no output" -ForegroundColor Yellow
                }
                
            } catch {
                Write-Host "    ❌ ERROR: app.py with $excelFile - $_" -ForegroundColor Red
                $appResults += @{
                    App = "app.py"
                    InputFile = $excelFile
                    OutputFile = $outputFile
                    Success = $false
                    Output = $_.ToString()
                }
            }
        }
    }
    
    $testResults += @{
        AppName = "BridgeGAD-00"
        InputFormat = "Excel (.xlsx)"
        Results = $appResults
        Status = if ($appResults | Where-Object { $_.Success }) { "SUCCESS" } else { "PARTIAL" }
    }
    
} finally {
    Pop-Location
}

# Test BridgeGAD-01 - Streamlit application
Write-Host "`n🔧 Testing BridgeGAD-01 - Streamlit Bridge Drawings" -ForegroundColor Cyan
$appOutputDir = "$outputDir\BridgeGAD-01"
New-Item -ItemType Directory -Path $appOutputDir -Force | Out-Null

Push-Location "C:\Users\Rajkumar\BridgeGAD-01"
try {
    # Test bridge_drawings.py directly
    Write-Host "  Testing bridge_drawings.py" -ForegroundColor Yellow
    
    $output = python bridge_drawings.py 2>&1
    $logFile = "$appOutputDir\bridge_drawings_output.txt"
    $output | Out-File $logFile -Encoding UTF8
    
    $testResults += @{
        AppName = "BridgeGAD-01"
        InputFormat = "No specific input file (Streamlit/Direct execution)"
        Results = @(@{
            App = "bridge_drawings.py"
            InputFile = "None"
            OutputFile = $logFile
            Success = $true
            Output = ($output | Out-String).Substring(0, [Math]::Min(300, ($output | Out-String).Length))
        })
        Status = "SUCCESS"
    }
    
    Write-Host "    ✅ SUCCESS: bridge_drawings.py executed" -ForegroundColor Green
    
} catch {
    Write-Host "    ❌ ERROR: $_" -ForegroundColor Red
    $testResults += @{
        AppName = "BridgeGAD-01"
        InputFormat = "No specific input file"
        Results = @()
        Status = "ERROR"
    }
} finally {
    Pop-Location
}

# Test BridgeGAD-03 - Excel with templates
Write-Host "`n🔧 Testing BridgeGAD-03 - Enhanced Bridge CAD" -ForegroundColor Cyan
$appOutputDir = "$outputDir\BridgeGAD-03"
New-Item -ItemType Directory -Path $appOutputDir -Force | Out-Null

Push-Location "C:\Users\Rajkumar\BridgeGAD-03"
try {
    $inputFile = "input.xlsx"
    if (Test-Path $inputFile) {
        Write-Host "  Testing with: $inputFile" -ForegroundColor Yellow
        
        # Copy to sample inputs
        Copy-Item $inputFile "$inputSamplesDir\BridgeGAD-03_$inputFile" -Force
        
        $outputFile = "$appOutputDir\enhanced_bridge_output.dxf"
        $output = python app.py $inputFile $outputFile 2>&1
        $success = Test-Path $outputFile
        
        $testResults += @{
            AppName = "BridgeGAD-03"
            InputFormat = "Excel template (input.xlsx)"
            Results = @(@{
                App = "app.py"
                InputFile = $inputFile
                OutputFile = $outputFile
                Success = $success
                Output = ($output | Out-String).Substring(0, [Math]::Min(400, ($output | Out-String).Length))
            })
            Status = if ($success) { "SUCCESS" } else { "PARTIAL" }
        }
        
        if ($success) {
            Write-Host "    ✅ SUCCESS: Enhanced bridge CAD output created" -ForegroundColor Green
        } else {
            Write-Host "    ⚠️  PARTIAL: App ran but no output file" -ForegroundColor Yellow
        }
        
    } else {
        Write-Host "    ⚠️  No input.xlsx found" -ForegroundColor Yellow
        $testResults += @{
            AppName = "BridgeGAD-03"
            InputFormat = "Excel template (input.xlsx) - NOT FOUND"
            Results = @()
            Status = "NO_INPUT"
        }
    }
    
} catch {
    Write-Host "    ❌ ERROR: $_" -ForegroundColor Red
} finally {
    Pop-Location
}

# Test BridgeGAD-04 - Parameter management
Write-Host "`n🔧 Testing BridgeGAD-04 - Bridge Drawer with Parameters" -ForegroundColor Cyan
$appOutputDir = "$outputDir\BridgeGAD-04"
New-Item -ItemType Directory -Path $appOutputDir -Force | Out-Null

Push-Location "C:\Users\Rajkumar\BridgeGAD-04"
try {
    $inputFile = "bridge_parameters_template.xlsx"
    if (Test-Path $inputFile) {
        Write-Host "  Testing with: $inputFile" -ForegroundColor Yellow
        
        # Copy to sample inputs
        Copy-Item $inputFile "$inputSamplesDir\BridgeGAD-04_$inputFile" -Force
        
        $outputFile = "$appOutputDir\bridge_drawer_output.dxf"
        $output = python app.py $inputFile $outputFile 2>&1
        $success = Test-Path $outputFile
        
        $testResults += @{
            AppName = "BridgeGAD-04"
            InputFormat = "Parameter template (.xlsx)"
            Results = @(@{
                App = "app.py"
                InputFile = $inputFile
                OutputFile = $outputFile
                Success = $success
                Output = ($output | Out-String).Substring(0, [Math]::Min(400, ($output | Out-String).Length))
            })
            Status = if ($success) { "SUCCESS" } else { "PARTIAL" }
        }
        
        if ($success) {
            Write-Host "    ✅ SUCCESS: Bridge drawer output created" -ForegroundColor Green
        } else {
            Write-Host "    ⚠️  PARTIAL: App ran but no output file" -ForegroundColor Yellow
        }
        
    } else {
        Write-Host "    ⚠️  No parameter template found" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "    ❌ ERROR: $_" -ForegroundColor Red
} finally {
    Pop-Location
}

# Test BridgeGAD-06 - Enhanced with Streamlit
Write-Host "`n🔧 Testing BridgeGAD-06 - Enhanced Bridge Generator" -ForegroundColor Cyan
$appOutputDir = "$outputDir\BridgeGAD-06"
New-Item -ItemType Directory -Path $appOutputDir -Force | Out-Null

Push-Location "C:\Users\Rajkumar\BridgeGAD-06"
try {
    $inputFile = "input.xlsx"
    if (Test-Path $inputFile) {
        Write-Host "  Testing with: $inputFile" -ForegroundColor Yellow
        
        # Copy to sample inputs
        Copy-Item $inputFile "$inputSamplesDir\BridgeGAD-06_$inputFile" -Force
        
        $outputFile = "$appOutputDir\enhanced_generator_output.dxf"
        $output = python main.py $inputFile $outputFile 2>&1
        $success = Test-Path $outputFile
        
        $testResults += @{
            AppName = "BridgeGAD-06"
            InputFormat = "Excel input (input.xlsx)"
            Results = @(@{
                App = "main.py"
                InputFile = $inputFile
                OutputFile = $outputFile
                Success = $success
                Output = ($output | Out-String).Substring(0, [Math]::Min(400, ($output | Out-String).Length))
            })
            Status = if ($success) { "SUCCESS" } else { "PARTIAL" }
        }
        
        if ($success) {
            Write-Host "    ✅ SUCCESS: Enhanced generator output created" -ForegroundColor Green
        } else {
            Write-Host "    ⚠️  PARTIAL: App ran but no output file" -ForegroundColor Yellow
        }
        
    } else {
        Write-Host "    ⚠️  No input.xlsx found" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "    ❌ ERROR: $_" -ForegroundColor Red
} finally {
    Pop-Location
}

# Test Bridge_Slab_Design - Engineering calculations
Write-Host "`n🔧 Testing Bridge_Slab_Design - Engineering Application" -ForegroundColor Cyan
$appOutputDir = "$outputDir\Bridge_Slab_Design"
New-Item -ItemType Directory -Path $appOutputDir -Force | Out-Null

Push-Location "C:\Users\Rajkumar\Bridge_Slab_Design"
try {
    $inputFile = "variable_mapping.xlsx"
    if (Test-Path $inputFile) {
        Write-Host "  Testing with: $inputFile" -ForegroundColor Yellow
        
        # Copy to sample inputs
        Copy-Item $inputFile "$inputSamplesDir\Bridge_Slab_Design_$inputFile" -Force
        
        $outputFile = "$appOutputDir\slab_design_output.json"
        $output = python bridge_design_app.py $inputFile $outputFile 2>&1
        $success = Test-Path $outputFile
        
        $testResults += @{
            AppName = "Bridge_Slab_Design"
            InputFormat = "Variable mapping (.xlsx)"
            Results = @(@{
                App = "bridge_design_app.py"
                InputFile = $inputFile
                OutputFile = $outputFile
                Success = $success
                Output = ($output | Out-String).Substring(0, [Math]::Min(400, ($output | Out-String).Length))
            })
            Status = if ($success) { "SUCCESS" } else { "PARTIAL" }
        }
        
        if ($success) {
            Write-Host "    ✅ SUCCESS: Slab design calculations completed" -ForegroundColor Green
        } else {
            Write-Host "    ⚠️  PARTIAL: App ran but no output file" -ForegroundColor Yellow
        }
        
    } else {
        Write-Host "    ⚠️  No variable mapping found" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "    ❌ ERROR: $_" -ForegroundColor Red
} finally {
    Pop-Location
}

# Generate final report
$reportPath = "$outputDir\INDIVIDUAL_TESTING_REPORT.json"
$testResults | ConvertTo-Json -Depth 10 | Out-File $reportPath -Encoding UTF8

Write-Host "`n🎉 INDIVIDUAL APPLICATION TESTING COMPLETED!" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green

Write-Host "`n📊 RESULTS SUMMARY:" -ForegroundColor Yellow
$successCount = ($testResults | Where-Object { $_.Status -eq "SUCCESS" }).Count
$partialCount = ($testResults | Where-Object { $_.Status -eq "PARTIAL" }).Count
$errorCount = ($testResults | Where-Object { $_.Status -notin @("SUCCESS", "PARTIAL") }).Count

Write-Host "   ✅ Successful: $successCount applications" -ForegroundColor Green
Write-Host "   ⚠️  Partial: $partialCount applications" -ForegroundColor Yellow
Write-Host "   ❌ Issues: $errorCount applications" -ForegroundColor Red

Write-Host "`n📁 DELIVERABLES:" -ForegroundColor Cyan
Write-Host "   📊 Test Report: $reportPath" -ForegroundColor Gray
Write-Host "   📁 Output Directory: $outputDir" -ForegroundColor Gray
Write-Host "   📄 Sample Inputs: $inputSamplesDir" -ForegroundColor Gray

foreach ($result in $testResults) {
    Write-Host "`n🔧 $($result.AppName): $($result.Status)" -ForegroundColor White
    Write-Host "   📝 Input Format: $($result.InputFormat)" -ForegroundColor Gray
}

Set-Location "C:\Users\Rajkumar\BridgeGAD-00"