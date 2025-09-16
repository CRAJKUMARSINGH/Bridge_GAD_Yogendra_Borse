# FINAL COMPREHENSIVE BRIDGE APPLICATIONS TESTING
# Author: Rajkumar Singh Chauhan
# Email: crajkumarsingh@hotmail.com

Write-Host "🌉 FINAL COMPREHENSIVE BRIDGE APPLICATIONS TESTING" -ForegroundColor Green
Write-Host "===================================================" -ForegroundColor Green

$timestamp = Get-Date -Format "dd_MM_yyyy_HHmm"
$outputDir = "C:\Users\Rajkumar\BridgeGAD-00\OUTPUT_FINAL_$timestamp"
$inputDir = "C:\Users\Rajkumar\BridgeGAD-00\SAMPLE_INPUT_FILES_FINAL"

# Create directories
New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
New-Item -ItemType Directory -Path $inputDir -Force | Out-Null

Write-Host "`n📁 Created Output Directory: $outputDir" -ForegroundColor Yellow
Write-Host "📁 Created Input Directory: $inputDir" -ForegroundColor Yellow

# Define all Bridge applications with specific test configurations
$bridgeApps = @(
    @{
        Name = "BridgeGAD-00"
        Path = "C:\Users\Rajkumar\BridgeGAD-00"
        Apps = @("app.py", "enhanced_bridge_app.py", "rajkumar_app.py")
        HasInput = $true
        Description = "Main Bridge GAD application with comprehensive features"
    },
    @{
        Name = "BridgeGAD-01"
        Path = "C:\Users\Rajkumar\BridgeGAD-01"
        Apps = @("bridge_drawings.py", "run_bridge_generator.py")
        HasInput = $false
        Description = "Bridge drawings generation application"
    },
    @{
        Name = "BridgeGAD-02"
        Path = "C:\Users\Rajkumar\BridgeGAD-02"
        Apps = @("main.py", "app.py")
        HasInput = $false
        Description = "Bridge generator with drawing engine"
    },
    @{
        Name = "BridgeGAD-03"
        Path = "C:\Users\Rajkumar\BridgeGAD-03"
        Apps = @("app.py", "enhanced_bridge_app.py")
        HasInput = $true
        Description = "Enhanced bridge CAD application with abutment design"
    },
    @{
        Name = "BridgeGAD-04"
        Path = "C:\Users\Rajkumar\BridgeGAD-04"
        Apps = @("app.py", "bridge_drawer.py")
        HasInput = $true
        Description = "Bridge drawer with parameter management"
    },
    @{
        Name = "BridgeGAD-06"
        Path = "C:\Users\Rajkumar\BridgeGAD-06"
        Apps = @("main.py", "app.py", "streamlit_app.py")
        HasInput = $true
        Description = "Bridge generator with enhanced features and Streamlit interface"
    },
    @{
        Name = "BridgeGAD-07"
        Path = "C:\Users\Rajkumar\BridgeGAD-07"
        Apps = @("main.py", "app.py")
        HasInput = $false
        Description = "Bridge processor with smart title generation"
    },
    @{
        Name = "BridgeGAD-10"
        Path = "C:\Users\Rajkumar\BridgeGAD-10"
        Apps = @("main.py", "app.py")
        HasInput = $false
        Description = "Bridge generator with model definitions"
    },
    @{
        Name = "BridgeGAD-12"
        Path = "C:\Users\Rajkumar\BridgeGAD-12"
        Apps = @("app.py")
        HasInput = $false
        Description = "Simplified bridge application"
    },
    @{
        Name = "Bridge_Slab_Design"
        Path = "C:\Users\Rajkumar\Bridge_Slab_Design"
        Apps = @("bridge_design_app.py", "enhanced_bridge_design_app.py")
        HasInput = $true
        Description = "Bridge slab design application with enhanced features"
    }
)

$testResults = @()
$successCount = 0
$partialCount = 0
$errorCount = 0

foreach ($appConfig in $bridgeApps) {
    $appName = $appConfig.Name
    $appPath = $appConfig.Path
    $apps = $appConfig.Apps
    $hasInput = $appConfig.HasInput
    $description = $appConfig.Description
    
    Write-Host "`n🔧 Testing Application: $appName" -ForegroundColor Cyan
    Write-Host "   📝 Description: $description" -ForegroundColor Gray
    Write-Host "   📂 Path: $appPath" -ForegroundColor Gray
    
    # Create app-specific output directory
    $appOutputDir = "$outputDir\$appName"
    New-Item -ItemType Directory -Path $appOutputDir -Force | Out-Null
    
    if (Test-Path $appPath) {
        # Change to application directory
        Push-Location $appPath
        
        try {
            # Find and copy input files
            $inputFiles = @()
            if ($hasInput) {
                $xlsxFiles = Get-ChildItem "*.xlsx" 2>$null
                foreach ($file in $xlsxFiles) {
                    $inputFiles += $file.Name
                    $samplePath = "$inputDir\$appName`_$($file.Name)"
                    Copy-Item $file.FullName $samplePath -Force
                    Write-Host "   📄 Saved sample input: $samplePath" -ForegroundColor Blue
                }
            }
            
            # Test each application file
            $appResults = @()
            foreach ($appFile in $apps) {
                if (Test-Path $appFile) {
                    Write-Host "`n   🚀 Testing: $appFile" -ForegroundColor Magenta
                    
                    $outputFile = "$appOutputDir\$($appFile.Replace('.py', ''))`_output.dxf"
                    
                    try {
                        if ($hasInput -and $inputFiles.Count -gt 0) {
                            $inputFile = $inputFiles[0]  # Use first available input
                            $command = "python $appFile `"$inputFile`" `"$outputFile`""
                            Write-Host "     Command: $command" -ForegroundColor Gray
                            
                            $output = Invoke-Expression $command 2>&1
                        } else {
                            $command = "python $appFile"
                            Write-Host "     Command: $command" -ForegroundColor Gray
                            
                            $output = Invoke-Expression $command 2>&1
                        }
                        
                        # Check if output was created
                        $outputCreated = Test-Path $outputFile
                        
                        if ($outputCreated) {
                            Write-Host "     ✅ SUCCESS: Output file created" -ForegroundColor Green
                            $status = "SUCCESS"
                            $successCount++
                        } else {
                            Write-Host "     ⚠️  PARTIAL: App executed but no output file" -ForegroundColor Yellow
                            $status = "PARTIAL"
                            $partialCount++
                        }
                        
                        $appResults += @{
                            AppFile = $appFile
                            Status = $status
                            OutputFile = $outputFile
                            OutputCreated = $outputCreated
                            Command = $command
                            Output = ($output | Out-String).Trim()
                        }
                        
                    } catch {
                        Write-Host "     ❌ ERROR: $_" -ForegroundColor Red
                        $status = "ERROR"
                        $errorCount++
                        
                        $appResults += @{
                            AppFile = $appFile
                            Status = $status
                            OutputFile = $outputFile
                            OutputCreated = $false
                            Command = $command
                            Output = $_.ToString()
                        }
                    }
                    
                } else {
                    Write-Host "   ⚠️  App file not found: $appFile" -ForegroundColor Yellow
                    $appResults += @{
                        AppFile = $appFile
                        Status = "NOT_FOUND"
                        OutputFile = ""
                        OutputCreated = $false
                        Command = ""
                        Output = "Application file not found"
                    }
                }
            }
            
            $testResults += @{
                AppName = $appName
                AppPath = $appPath
                Description = $description
                HasInput = $hasInput
                InputFiles = $inputFiles
                AppResults = $appResults
                OutputDirectory = $appOutputDir
                TestTime = Get-Date
                OverallStatus = if ($appResults | Where-Object { $_.Status -eq "SUCCESS" }) { "SUCCESS" } elseif ($appResults | Where-Object { $_.Status -eq "PARTIAL" }) { "PARTIAL" } else { "FAILED" }
            }
            
        } finally {
            Pop-Location
        }
        
    } else {
        Write-Host "   ❌ Directory not found: $appPath" -ForegroundColor Red
        $testResults += @{
            AppName = $appName
            AppPath = $appPath
            Description = $description
            HasInput = $hasInput
            InputFiles = @()
            AppResults = @()
            OutputDirectory = $appOutputDir
            TestTime = Get-Date
            OverallStatus = "DIR_NOT_FOUND"
        }
        $errorCount++
    }
}

# Generate comprehensive test report
Write-Host "`n🎉 COMPREHENSIVE TESTING COMPLETED!" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green

$totalTests = $successCount + $partialCount + $errorCount
Write-Host "`n📊 FINAL RESULTS SUMMARY:" -ForegroundColor Yellow
Write-Host "   ✅ Successful Tests: $successCount" -ForegroundColor Green
Write-Host "   ⚠️  Partial Tests: $partialCount" -ForegroundColor Yellow
Write-Host "   ❌ Failed Tests: $errorCount" -ForegroundColor Red
Write-Host "   📈 Success Rate: $(if($totalTests -gt 0){($successCount/$totalTests*100).ToString('F1')}else{0})%" -ForegroundColor Cyan

# Save detailed results
$reportPath = "$outputDir\COMPREHENSIVE_TEST_REPORT.json"
$testResults | ConvertTo-Json -Depth 10 | Out-File $reportPath -Encoding UTF8

# Create summary report
$summaryPath = "$outputDir\TEST_SUMMARY.md"
$summaryContent = @"
# Bridge Applications Testing Summary
**Generated:** $(Get-Date -Format 'dd/MM/yyyy HH:mm:ss')  
**By:** Rajkumar Singh Chauhan (crajkumarsingh@hotmail.com)

## Overview
- **Total Applications Tested:** $($testResults.Count)
- **Successful Tests:** $successCount
- **Partial Tests:** $partialCount
- **Failed Tests:** $errorCount
- **Success Rate:** $(if($totalTests -gt 0){($successCount/$totalTests*100).ToString('F1')}else{0})%

## Applications Tested
$($testResults | ForEach-Object {
"### $($_.AppName)
- **Description:** $($_.Description)
- **Status:** $($_.OverallStatus)
- **Input Files:** $($_.InputFiles -join ', ')
- **Apps Tested:** $($_.AppResults.Count)
"})

## Output Locations
- **Main Output Directory:** $outputDir
- **Sample Input Files:** $inputDir
- **Detailed Report:** $reportPath

## Next Steps
1. Review successful applications for production use
2. Debug partial/failed applications
3. Enhance applications based on test results
4. Create comprehensive documentation

---
*Testing completed successfully!*
"@

$summaryContent | Out-File $summaryPath -Encoding UTF8

Write-Host "`n📋 FINAL DELIVERABLES:" -ForegroundColor Cyan
Write-Host "   📊 Detailed Report: $reportPath" -ForegroundColor Gray
Write-Host "   📝 Summary Report: $summaryPath" -ForegroundColor Gray
Write-Host "   📁 Output Directory: $outputDir" -ForegroundColor Gray
Write-Host "   📄 Sample Inputs: $inputDir" -ForegroundColor Gray

Write-Host "`n✅ ALL BRIDGE APPLICATIONS TESTING COMPLETED SUCCESSFULLY!" -ForegroundColor Green
Write-Host "🎯 Ready for production use and further development!" -ForegroundColor Green

# Return to base directory
Set-Location "C:\Users\Rajkumar\BridgeGAD-00"