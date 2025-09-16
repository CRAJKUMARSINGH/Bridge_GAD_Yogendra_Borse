# INDIVIDUAL BRIDGE APPLICATION ANALYSIS & TESTING
# Author: Rajkumar Singh Chauhan
# Email: crajkumarsingh@hotmail.com
# Purpose: Analyze each Bridge app individually for specific input formats

Write-Host "🔍 INDIVIDUAL BRIDGE APPLICATION ANALYSIS" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

$timestamp = Get-Date -Format "dd_MM_yyyy_HHmm"
$baseOutputDir = "C:\Users\Rajkumar\BridgeGAD-00\INDIVIDUAL_APP_ANALYSIS_$timestamp"
$analysisDir = "$baseOutputDir\Analysis"

# Create directories
New-Item -ItemType Directory -Path $baseOutputDir -Force | Out-Null
New-Item -ItemType Directory -Path $analysisDir -Force | Out-Null

Write-Host "`n📁 Created Analysis Directory: $baseOutputDir" -ForegroundColor Yellow

# Define each application with specific analysis
$bridgeApps = @(
    @{
        Name = "BridgeGAD-00"
        Path = "C:\Users\Rajkumar\BridgeGAD-00"
        Description = "Main Bridge GAD - Excel-based input with multiple formats"
        ExpectedInputs = @("*.xlsx", "*.yaml", "*.txt")
        MainFiles = @("app.py", "enhanced_bridge_app.py", "rajkumar_app.py")
    },
    @{
        Name = "BridgeGAD-01"
        Path = "C:\Users\Rajkumar\BridgeGAD-01"
        Description = "Bridge Drawings - Streamlit interface"
        ExpectedInputs = @("*.py", "*.json", "*.csv")
        MainFiles = @("streamlit_app.py", "bridge_drawings.py", "run_bridge_generator.py")
    },
    @{
        Name = "BridgeGAD-02"
        Path = "C:\Users\Rajkumar\BridgeGAD-02"
        Description = "Bridge Generator - Parameter-based system"
        ExpectedInputs = @("*.py", "*.json", "*.txt")
        MainFiles = @("main.py", "app.py", "bridge_generator.py", "parameter_definitions.py")
    },
    @{
        Name = "BridgeGAD-03"
        Path = "C:\Users\Rajkumar\BridgeGAD-03"
        Description = "Enhanced Bridge CAD - Abutment design with Excel inputs"
        ExpectedInputs = @("*.xlsx", "*.py", "*.dxf")
        MainFiles = @("app.py", "enhanced_bridge_app.py", "abutment_design.py")
    },
    @{
        Name = "BridgeGAD-04"
        Path = "C:\Users\Rajkumar\BridgeGAD-04"
        Description = "Bridge Drawer - Parameter management system"
        ExpectedInputs = @("*.xlsx", "*.json", "*.py")
        MainFiles = @("app.py", "bridge_drawer.py", "parameter_manager.py")
    },
    @{
        Name = "BridgeGAD-06"
        Path = "C:\Users\Rajkumar\BridgeGAD-06"
        Description = "Enhanced Bridge Generator - Streamlit + Excel"
        ExpectedInputs = @("*.xlsx", "*.py", "*.json")
        MainFiles = @("main.py", "app.py", "streamlit_app.py", "bridge_generator.py")
    },
    @{
        Name = "BridgeGAD-07"
        Path = "C:\Users\Rajkumar\BridgeGAD-07"
        Description = "Bridge Processor - LISP integration"
        ExpectedInputs = @("*.py", "*.lsp", "*.txt")
        MainFiles = @("main.py", "app.py", "bridge_processor.py", "test_lisp_logic.py")
    },
    @{
        Name = "BridgeGAD-10"
        Path = "C:\Users\Rajkumar\BridgeGAD-10"
        Description = "Bridge Generator - Model-based approach"
        ExpectedInputs = @("*.xlsx", "*.py", "*.json")
        MainFiles = @("main.py", "app.py", "bridge_generator.py", "models.py")
    },
    @{
        Name = "BridgeGAD-12"
        Path = "C:\Users\Rajkumar\BridgeGAD-12"
        Description = "Simplified Bridge Application"
        ExpectedInputs = @("*.py", "*.txt", "*.json")
        MainFiles = @("app.py")
    },
    @{
        Name = "Bridge_Slab_Design"
        Path = "C:\Users\Rajkumar\Bridge_Slab_Design"
        Description = "Bridge Slab Design - Engineering calculations"
        ExpectedInputs = @("*.xlsx", "*.py", "*.json")
        MainFiles = @("bridge_design_app.py", "enhanced_bridge_design_app.py")
    }
)

$analysisResults = @()

foreach ($app in $bridgeApps) {
    Write-Host "`n🔧 Analyzing: $($app.Name)" -ForegroundColor Cyan
    Write-Host "   📝 $($app.Description)" -ForegroundColor Gray
    
    $appAnalysisDir = "$analysisDir\$($app.Name)"
    New-Item -ItemType Directory -Path $appAnalysisDir -Force | Out-Null
    
    if (Test-Path $app.Path) {
        Push-Location $app.Path
        
        try {
            # Analyze input files
            $foundInputs = @{}
            foreach ($pattern in $app.ExpectedInputs) {
                $files = Get-ChildItem $pattern -ErrorAction SilentlyContinue
                if ($files) {
                    $foundInputs[$pattern] = $files.Name
                    Write-Host "   📄 Found $pattern files: $($files.Name -join ', ')" -ForegroundColor Blue
                }
            }
            
            # Analyze main application files
            $foundApps = @()
            foreach ($mainFile in $app.MainFiles) {
                if (Test-Path $mainFile) {
                    $foundApps += $mainFile
                    Write-Host "   🚀 Found app: $mainFile" -ForegroundColor Green
                    
                    # Try to analyze the file for input requirements
                    $content = Get-Content $mainFile -Head 50 -ErrorAction SilentlyContinue
                    if ($content) {
                        $inputHints = $content | Where-Object { 
                            $_ -match "input|Input|INPUT|argv|args|file|File|xlsx|csv|json|yaml" 
                        } | Select-Object -First 5
                        
                        if ($inputHints) {
                            Write-Host "   💡 Input hints found:" -ForegroundColor Yellow
                            foreach ($hint in $inputHints) {
                                Write-Host "      $($hint.Trim())" -ForegroundColor Gray
                            }
                        }
                    }
                }
            }
            
            # Check for README or documentation
            $docFiles = Get-ChildItem "README*", "*.md", "*.txt" -ErrorAction SilentlyContinue | Where-Object { $_.Name -ne "requirements.txt" }
            $documentation = @()
            if ($docFiles) {
                foreach ($doc in $docFiles) {
                    $documentation += $doc.Name
                    Write-Host "   📚 Documentation: $($doc.Name)" -ForegroundColor Magenta
                }
            }
            
            # Check for configuration files
            $configFiles = Get-ChildItem "config*", "*.yaml", "*.yml", "*.json" -ErrorAction SilentlyContinue
            $configurations = @()
            if ($configFiles) {
                foreach ($config in $configFiles) {
                    $configurations += $config.Name
                    Write-Host "   ⚙️  Configuration: $($config.Name)" -ForegroundColor Cyan
                }
            }
            
            $result = @{
                AppName = $app.Name
                Description = $app.Description
                Path = $app.Path
                FoundInputs = $foundInputs
                FoundApps = $foundApps
                Documentation = $documentation
                Configurations = $configurations
                Status = "ANALYZED"
                AnalysisTime = Get-Date
            }
            
        } catch {
            Write-Host "   ❌ Error analyzing: $_" -ForegroundColor Red
            $result = @{
                AppName = $app.Name
                Description = $app.Description
                Path = $app.Path
                FoundInputs = @{}
                FoundApps = @()
                Documentation = @()
                Configurations = @()
                Status = "ERROR"
                Error = $_.ToString()
                AnalysisTime = Get-Date
            }
        } finally {
            Pop-Location
        }
        
    } else {
        Write-Host "   ❌ Directory not found: $($app.Path)" -ForegroundColor Red
        $result = @{
            AppName = $app.Name
            Description = $app.Description
            Path = $app.Path
            FoundInputs = @{}
            FoundApps = @()
            Documentation = @()
            Configurations = @()
            Status = "NOT_FOUND"
            AnalysisTime = Get-Date
        }
    }
    
    $analysisResults += $result
}

# Generate comprehensive analysis report
$reportPath = "$analysisDir\INDIVIDUAL_APP_ANALYSIS_REPORT.json"
$analysisResults | ConvertTo-Json -Depth 10 | Out-File $reportPath -Encoding UTF8

# Generate markdown summary
$summaryPath = "$analysisDir\APP_INPUT_FORMATS_SUMMARY.md"
$summaryContent = @"
# Individual Bridge Application Input Format Analysis
**Generated:** $(Get-Date -Format 'dd/MM/yyyy HH:mm:ss')  
**Author:** Rajkumar Singh Chauhan  
**Email:** crajkumarsingh@hotmail.com

## Analysis Overview
This document provides detailed analysis of input formats for each Bridge application.

$($analysisResults | ForEach-Object {
"## $($_.AppName)
**Description:** $($_.Description)  
**Status:** $($_.Status)  
**Path:** $($_.Path)

### Input Files Found:
$(if ($_.FoundInputs.Keys.Count -gt 0) {
    $_.FoundInputs.GetEnumerator() | ForEach-Object { "- **$($_.Key):** $($_.Value -join ', ')`n" }
} else { "- No specific input files found`n" })

### Application Files:
$(if ($_.FoundApps.Count -gt 0) {
    $_.FoundApps | ForEach-Object { "- $_`n" }
} else { "- No application files found`n" })

### Documentation:
$(if ($_.Documentation.Count -gt 0) {
    $_.Documentation | ForEach-Object { "- $_`n" }
} else { "- No documentation found`n" })

### Configuration Files:
$(if ($_.Configurations.Count -gt 0) {
    $_.Configurations | ForEach-Object { "- $_`n" }
} else { "- No configuration files found`n" })

---
"})

## Next Steps
1. Create specific input templates for each application
2. Test each application with its native input format
3. Document specific usage patterns for each app
4. Create customized testing scripts per application

## Analysis Results Summary
- **Total Applications Analyzed:** $($analysisResults.Count)
- **Successfully Analyzed:** $(($analysisResults | Where-Object {$_.Status -eq "ANALYZED"}).Count)
- **Applications with Input Files:** $(($analysisResults | Where-Object {$_.FoundInputs.Keys.Count -gt 0}).Count)
- **Applications with Documentation:** $(($analysisResults | Where-Object {$_.Documentation.Count -gt 0}).Count)
"@

$summaryContent | Out-File $summaryPath -Encoding UTF8

Write-Host "`n🎉 INDIVIDUAL ANALYSIS COMPLETED!" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green
Write-Host "📊 Analysis Report: $reportPath" -ForegroundColor Cyan
Write-Host "📝 Summary Document: $summaryPath" -ForegroundColor Cyan
Write-Host "📁 Analysis Directory: $analysisDir" -ForegroundColor Cyan

Write-Host "`n📋 SUMMARY:" -ForegroundColor Yellow
Write-Host "   Analyzed: $($analysisResults.Count) applications" -ForegroundColor White
Write-Host "   Successful: $(($analysisResults | Where-Object {$_.Status -eq "ANALYZED"}).Count)" -ForegroundColor Green
Write-Host "   With Inputs: $(($analysisResults | Where-Object {$_.FoundInputs.Keys.Count -gt 0}).Count)" -ForegroundColor Blue
Write-Host "   With Docs: $(($analysisResults | Where-Object {$_.Documentation.Count -gt 0}).Count)" -ForegroundColor Magenta

Set-Location "C:\Users\Rajkumar\BridgeGAD-00"