# Verify Synchronization Status of All BridgeGAD Repositories
Write-Host "🔍 VERIFYING BRIDGEGAD REPOSITORY SYNCHRONIZATION STATUS" -ForegroundColor Green
Write-Host "=======================================================" -ForegroundColor Green

$repos = @("BridgeGAD-00", "BridgeGAD-01", "BridgeGAD-02", "BridgeGAD-03", "BridgeGAD-04", "BridgeGAD-05", "BridgeGAD-06", "BridgeGAD-07", "BridgeGAD-08", "BridgeGAD-09", "BridgeGAD-10", "BridgeGAD-11", "BridgeGAD-12")
$base = "C:\Users\Rajkumar"
$synchronized = 0
$issues = 0

foreach ($repo in $repos) {
    $path = "$base\$repo"
    Write-Host "`n🔧 Checking: $repo" -ForegroundColor Cyan
    
    if (Test-Path $path) {
        if (Test-Path "$path\.git") {
            Set-Location $path
            
            # Check Git configuration
            $userName = git config user.name
            $userEmail = git config user.email
            
            if ($userName -eq "RAJKUMAR SINGH CHAUHAN" -and $userEmail -eq "crajkumarsingh@hotmail.com") {
                Write-Host "  ✅ Git configuration: Correct" -ForegroundColor Green
            } else {
                Write-Host "  ⚠️  Git configuration: Needs update" -ForegroundColor Yellow
                $issues++
            }
            
            # Check repository status
            $status = git status --porcelain
            if (-not $status) {
                Write-Host "  ✅ Working directory: Clean" -ForegroundColor Green
            } else {
                Write-Host "  ⚠️  Working directory: Has uncommitted changes" -ForegroundColor Yellow
                $issues++
            }
            
            # Check remote synchronization
            git fetch origin 2>$null
            $behind = git rev-list HEAD..origin/main --count 2>$null
            $ahead = git rev-list origin/main..HEAD --count 2>$null
            
            if ($behind -eq "0" -and $ahead -eq "0") {
                Write-Host "  ✅ Remote sync: Up to date" -ForegroundColor Green
                $synchronized++
            } elseif ($ahead -gt 0) {
                Write-Host "  📤 Remote sync: $ahead commits ahead (need to push)" -ForegroundColor Yellow
                $issues++
            } elseif ($behind -gt 0) {
                Write-Host "  📥 Remote sync: $behind commits behind (need to pull)" -ForegroundColor Yellow
                $issues++
            }
            
            # Check remote URL
            $remoteUrl = git remote get-url origin 2>$null
            if ($remoteUrl) {
                Write-Host "  🌐 Remote: $remoteUrl" -ForegroundColor Blue
            } else {
                Write-Host "  ⚠️  Remote: Not configured" -ForegroundColor Yellow
                $issues++
            }
            
        } else {
            Write-Host "  ❌ Not a Git repository" -ForegroundColor Red
            $issues++
        }
    } else {
        Write-Host "  ❌ Directory not found" -ForegroundColor Red
        $issues++
    }
}

Set-Location "C:\Users\Rajkumar\BridgeGAD-00"

Write-Host "`n🎉 VERIFICATION COMPLETED!" -ForegroundColor Green
Write-Host "=========================" -ForegroundColor Green
Write-Host "✅ Fully Synchronized: $synchronized repositories" -ForegroundColor Green
Write-Host "⚠️  Issues Found: $issues" -ForegroundColor Yellow
Write-Host "📊 Success Rate: $(($synchronized / $repos.Count * 100).ToString('F1'))%" -ForegroundColor Cyan

if ($issues -eq 0) {
    Write-Host "`n🎊 ALL BRIDGEGAD REPOSITORIES ARE PERFECTLY SYNCHRONIZED!" -ForegroundColor Green
} else {
    Write-Host "`n📋 Some repositories need attention. Review the issues above." -ForegroundColor Yellow
}

Write-Host "`nBy: Rajkumar Singh Chauhan (crajkumarsingh@hotmail.com)" -ForegroundColor Green