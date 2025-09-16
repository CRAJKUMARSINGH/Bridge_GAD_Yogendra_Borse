# PowerShell Script to Apply Comprehensive Instructions to All BridgeGAD Applications
# Author: Rajkumar Singh Chauhan
# Email: crajkumarsingh@hotmail.com

Write-Host "🚀 APPLYING COMPREHENSIVE INSTRUCTIONS TO ALL BRIDGEGAD APPLICATIONS" -ForegroundColor Green
Write-Host "=================================================================" -ForegroundColor Green

# Define the list of BridgeGAD applications
$bridgeGadApps = @(
    "BridgeGAD-00", "BridgeGAD-01", "BridgeGAD-02", "BridgeGAD-03", "BridgeGAD-04", 
    "BridgeGAD-05", "BridgeGAD-06", "BridgeGAD-07", "BridgeGAD-08", "BridgeGAD-09", 
    "BridgeGAD-10", "BridgeGAD-11", "BridgeGAD-12"
)

$baseDir = "C:\Users\Rajkumar"
$sourceApp = "BridgeGAD-00"

Write-Host "📋 Processing $($bridgeGadApps.Count) BridgeGAD applications..." -ForegroundColor Yellow

foreach ($app in $bridgeGadApps) {
    $appPath = Join-Path $baseDir $app
    
    Write-Host "`n🔧 Processing: $app" -ForegroundColor Cyan
    
    if (Test-Path $appPath) {
        Write-Host "   ✅ Directory exists: $appPath" -ForegroundColor Green
        
        # Copy comprehensive instructions
        $sourcePath = Join-Path $baseDir "$sourceApp\COMPREHENSIVE_INSTRUCTIONS_SUMMARY.md"
        $destPath = Join-Path $appPath "COMPREHENSIVE_INSTRUCTIONS_SUMMARY.md"
        
        if (Test-Path $sourcePath) {
            Copy-Item $sourcePath $destPath -Force
            Write-Host "   📄 Copied comprehensive instructions" -ForegroundColor Green
        }
        
        # Check for git repository
        $gitPath = Join-Path $appPath ".git"
        if (Test-Path $gitPath) {
            Write-Host "   📚 Git repository detected" -ForegroundColor Green
            
            # Change to app directory and configure git
            Push-Location $appPath
            try {
                git config user.name "RAJKUMAR SINGH CHAUHAN"
                git config user.email "crajkumarsingh@hotmail.com"
                
                # Check status
                $status = git status --porcelain
                if ($status) {
                    Write-Host "   📝 Changes detected, committing..." -ForegroundColor Yellow
                    git add .
                    git commit -m "🚀 COMPREHENSIVE INSTRUCTIONS APPLIED: Following unified guidance from BridgeGAD-00

✅ APPLIED INSTRUCTIONS:
- Complete asset utilization from all *.md and *.txt files
- User-friendly BAT file requirements
- Modern deployment optimization (Streamlit/Vercel)  
- Bridge engineering excellence with LISP function integration
- Professional documentation standards
- Comprehensive testing & validation protocols

📋 FROM SOURCE FILES:
- README.md, TASK_COMPLETION_GUIDE.md, TODO.md, CONTRIBUTING.md
- ENHANCED_FEATURES_README.md, BRIDGE_ISSUES_RESOLVED.md, WARP.md
- bug removal prompts, bridge_code.txt, gad_bridge.txt
- requirements.txt, input.txt, and all guidance documents

🎯 IMPLEMENTATION READY FOR:
- Complete LISP asset utilization (cs, pier, abt1, layout, st functions)
- User-friendly BAT file creation for non-technical users
- Professional bridge drawing generation with DXF output
- Modern web deployment and comprehensive testing

By: Rajkumar Singh Chauhan - crajkumarsingh@hotmail.com"
                    
                    # Try to push if remote exists
                    $remotes = git remote
                    if ($remotes -contains "origin") {
                        Write-Host "   🌐 Pushing to remote repository..." -ForegroundColor Yellow
                        git push origin main 2>$null
                        if ($LASTEXITCODE -eq 0) {
                            Write-Host "   ✅ Successfully pushed to remote" -ForegroundColor Green
                        } else {
                            Write-Host "   ⚠️  Push failed - may need manual intervention" -ForegroundColor Red
                        }
                    } else {
                        Write-Host "   ℹ️  No remote repository configured" -ForegroundColor Blue
                    }
                } else {
                    Write-Host "   ✅ Repository is clean, no changes to commit" -ForegroundColor Green
                }
            }
            catch {
                Write-Host "   ❌ Git operation failed: $_" -ForegroundColor Red
            }
            finally {
                Pop-Location
            }
        } else {
            Write-Host "   ⚠️  No git repository found" -ForegroundColor Yellow
        }
        
        # List markdown and text files
        $markdownFiles = Get-ChildItem -Path $appPath -Filter "*.md" -ErrorAction SilentlyContinue
        $textFiles = Get-ChildItem -Path $appPath -Filter "*.txt" -ErrorAction SilentlyContinue
        
        Write-Host "   📄 Found $($markdownFiles.Count) .md files and $($textFiles.Count) .txt files" -ForegroundColor Blue
        
        if ($markdownFiles.Count -gt 0) {
            Write-Host "   📋 Markdown files:" -ForegroundColor Blue
            foreach ($file in $markdownFiles) {
                Write-Host "      - $($file.Name)" -ForegroundColor Gray
            }
        }
        
        if ($textFiles.Count -gt 0) {
            Write-Host "   📄 Text files:" -ForegroundColor Blue
            foreach ($file in $textFiles) {
                Write-Host "      - $($file.Name)" -ForegroundColor Gray
            }
        }
        
    } else {
        Write-Host "   ❌ Directory does not exist: $appPath" -ForegroundColor Red
    }
}

Write-Host "`n🎉 COMPREHENSIVE INSTRUCTIONS APPLICATION COMPLETE!" -ForegroundColor Green
Write-Host "=================================================================" -ForegroundColor Green
Write-Host "📋 Summary:" -ForegroundColor Yellow
Write-Host "   - Applied unified instructions to all available BridgeGAD applications" -ForegroundColor White
Write-Host "   - Configured git repositories with proper user credentials" -ForegroundColor White
Write-Host "   - Committed comprehensive instruction changes to repositories" -ForegroundColor White
Write-Host "   - Synchronized local and remote repositories where possible" -ForegroundColor White
Write-Host "   - Ready for systematic implementation of:" -ForegroundColor White
Write-Host "     * Complete LISP asset utilization" -ForegroundColor Gray
Write-Host "     * User-friendly BAT file creation" -ForegroundColor Gray
Write-Host "     * Modern deployment optimization" -ForegroundColor Gray
Write-Host "     * Professional bridge engineering compliance" -ForegroundColor Gray

Write-Host "`n🔄 NEXT STEPS:" -ForegroundColor Cyan
Write-Host "   1. Review each application's specific *.md and *.txt files" -ForegroundColor White
Write-Host "   2. Implement missing LISP functions (cs, pier, abt1, layout, st)" -ForegroundColor White
Write-Host "   3. Create user-friendly BAT files for easy deployment" -ForegroundColor White
Write-Host "   4. Optimize for Streamlit/Vercel deployment" -ForegroundColor White
Write-Host "   5. Apply comprehensive testing and validation" -ForegroundColor White

Write-Host "`nBy: Rajkumar Singh Chauhan (crajkumarsingh@hotmail.com)" -ForegroundColor Green