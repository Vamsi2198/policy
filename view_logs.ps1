# Snowflake Query Log Viewer for Windows PowerShell
# Quick helper script for common log viewing tasks

param(
    [Parameter(Position=0)]
    [string]$Action = "help",
    
    [int]$Limit = 0,
    [switch]$Errors
)

$LogFile = "snowflake_queries.log"
$ViewerScript = "src\view_snowflake_logs.py"

function Show-Help {
    Write-Host "`n╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║         Snowflake Query Log Viewer - PowerShell             ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan
    
    Write-Host "Usage: .\view_logs.ps1 [action] [-Limit N] [-Errors]`n" -ForegroundColor Yellow
    
    Write-Host "Actions:" -ForegroundColor Green
    Write-Host "  summary      - Show summary statistics only" -ForegroundColor White
    Write-Host "  all          - Show all logs with summary" -ForegroundColor White
    Write-Host "  recent       - Show last 10 queries (use -Limit to change)" -ForegroundColor White
    Write-Host "  failed       - Show only failed queries" -ForegroundColor White
    Write-Host "  select       - Show only SELECT queries" -ForegroundColor White
    Write-Host "  create       - Show only CREATE queries" -ForegroundColor White
    Write-Host "  alter        - Show only ALTER queries" -ForegroundColor White
    Write-Host "  tail         - Watch log file in real-time" -ForegroundColor White
    Write-Host "  test         - Run test script" -ForegroundColor White
    Write-Host "  open         - Open log file in notepad" -ForegroundColor White
    Write-Host "  help         - Show this help message`n" -ForegroundColor White
    
    Write-Host "Options:" -ForegroundColor Green
    Write-Host "  -Limit N     - Limit number of entries to show" -ForegroundColor White
    Write-Host "  -Errors      - Show detailed error messages`n" -ForegroundColor White
    
    Write-Host "Examples:" -ForegroundColor Green
    Write-Host "  .\view_logs.ps1 summary" -ForegroundColor Gray
    Write-Host "  .\view_logs.ps1 failed -Errors" -ForegroundColor Gray
    Write-Host "  .\view_logs.ps1 recent -Limit 5" -ForegroundColor Gray
    Write-Host "  .\view_logs.ps1 tail`n" -ForegroundColor Gray
}

function Invoke-LogViewer {
    param([string]$Args)
    
    if (-not (Test-Path $ViewerScript)) {
        Write-Host "❌ Error: $ViewerScript not found" -ForegroundColor Red
        return
    }
    
    $cmd = "python $ViewerScript $Args"
    Write-Host "Running: $cmd`n" -ForegroundColor Cyan
    Invoke-Expression $cmd
}

# Main logic
switch ($Action.ToLower()) {
    "help" {
        Show-Help
    }
    
    "summary" {
        Invoke-LogViewer "--summary-only"
    }
    
    "all" {
        $args = ""
        if ($Limit -gt 0) { $args += " --limit $Limit" }
        Invoke-LogViewer $args
    }
    
    "recent" {
        $limitVal = if ($Limit -gt 0) { $Limit } else { 10 }
        Invoke-LogViewer "--limit $limitVal"
    }
    
    "failed" {
        $args = "--status FAILED"
        if ($Errors) { $args += " --errors" }
        if ($Limit -gt 0) { $args += " --limit $Limit" }
        Invoke-LogViewer $args
    }
    
    "select" {
        $args = "--type SELECT"
        if ($Limit -gt 0) { $args += " --limit $Limit" }
        Invoke-LogViewer $args
    }
    
    "create" {
        $args = "--type CREATE"
        if ($Limit -gt 0) { $args += " --limit $Limit" }
        Invoke-LogViewer $args
    }
    
    "alter" {
        $args = "--type ALTER"
        if ($Limit -gt 0) { $args += " --limit $Limit" }
        Invoke-LogViewer $args
    }
    
    "tail" {
        if (-not (Test-Path $LogFile)) {
            Write-Host "❌ Error: $LogFile not found" -ForegroundColor Red
            return
        }
        Write-Host "📊 Watching $LogFile (Press Ctrl+C to stop)...`n" -ForegroundColor Cyan
        Get-Content $LogFile -Wait -Tail 20
    }
    
    "test" {
        if (-not (Test-Path "src\test_query_logging.py")) {
            Write-Host "❌ Error: Test script not found" -ForegroundColor Red
            return
        }
        Write-Host "🧪 Running query logging test...`n" -ForegroundColor Cyan
        python src\test_query_logging.py
    }
    
    "open" {
        if (-not (Test-Path $LogFile)) {
            Write-Host "❌ Error: $LogFile not found" -ForegroundColor Red
            return
        }
        Write-Host "📂 Opening $LogFile in notepad..." -ForegroundColor Cyan
        notepad $LogFile
    }
    
    default {
        Write-Host "❌ Unknown action: $Action`n" -ForegroundColor Red
        Show-Help
    }
}
