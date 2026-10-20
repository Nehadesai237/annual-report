# PowerShell script to create optimized ZIP file for client delivery
# This excludes large directories like node_modules, venv, __pycache__, etc.

$ErrorActionPreference = "Stop"

Write-Host "Creating optimized ZIP file for client..." -ForegroundColor Green

# Get the current directory name
$projectName = Split-Path -Leaf (Get-Location)
$zipFileName = "$projectName-client.zip"
$tempDir = "temp-zip-$([System.Guid]::NewGuid().ToString())"

try {
    # Create temporary directory
    New-Item -ItemType Directory -Path $tempDir | Out-Null
    Write-Host "Created temporary directory: $tempDir" -ForegroundColor Yellow
    
    # Directories and files to exclude
    $excludePatterns = @(
        "**\node_modules",
        "**\venv",
        "**\env",
        "**\__pycache__",
        "**\*.pyc",
        "**\*.pyo",
        "**\build",
        "**\dist",
        "**\.git",
        "**\.vscode",
        "**\.idea",
        "**\uploads",
        "**\reports",
        "**\*.log",
        "**\.DS_Store",
        "**\Thumbs.db",
        "**\*.db",
        "**\*.sqlite*",
        "**\.pytest_cache",
        "**\htmlcov",
        "**\.coverage",
        "**\*.egg-info",
        "**\ml\models\*.h5",
        "**\ml\models\*.pkl",
        "**\ml\models\*.joblib",
        "**\frontend\build"  # React build folder
    )
    
    Write-Host "`nCopying files (excluding large directories)..." -ForegroundColor Yellow
    
    # Copy files while excluding patterns
    Get-ChildItem -Path . -Recurse | Where-Object {
        $item = $_
        $relativePath = $item.FullName.Replace((Get-Location).Path + "\", "")
        
        # Check if item matches any exclude pattern
        $shouldExclude = $false
        foreach ($pattern in $excludePatterns) {
            if ($relativePath -like $pattern -or $item.Name -like $pattern) {
                $shouldExclude = $true
                break
            }
        }
        
        # Also exclude if path contains these directories
        if ($relativePath -match "\\node_modules\\" -or 
            $relativePath -match "\\venv\\" -or 
            $relativePath -match "\\__pycache__\\" -or
            $relativePath -match "\\\.git\\" -or
            $relativePath -match "\\uploads\\" -or
            $relativePath -match "\\reports\\" -or
            $relativePath.StartsWith("$tempDir\")) {
            $shouldExclude = $true
        }
        
        return -not $shouldExclude
    } | ForEach-Object {
        $relativePath = $_.FullName.Replace((Get-Location).Path + "\", "")
        $destPath = Join-Path $tempDir $relativePath
        $destDir = Split-Path $destPath -Parent
        
        if (-not (Test-Path $destDir)) {
            New-Item -ItemType Directory -Path $destDir -Force | Out-Null
        }
        
        if (-not $_.PSIsContainer) {
            Copy-Item $_.FullName -Destination $destPath -Force
        }
    }
    
    Write-Host "Files copied successfully!" -ForegroundColor Green
    Write-Host "`nCreating ZIP file (no compression for speed)..." -ForegroundColor Yellow
    
    # Create ZIP with no compression for maximum speed
    if (Test-Path $zipFileName) {
        Remove-Item $zipFileName -Force
    }
    
    # Use .NET compression with no compression for speed
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    [System.IO.Compression.ZipFile]::CreateFromDirectory($tempDir, $zipFileName, [System.IO.Compression.CompressionLevel]::NoCompression, $false)
    
    $zipSize = (Get-Item $zipFileName).Length / 1MB
    Write-Host "`n✅ ZIP file created successfully!" -ForegroundColor Green
    Write-Host "   File: $zipFileName" -ForegroundColor Cyan
    Write-Host "   Size: $([math]::Round($zipSize, 2)) MB" -ForegroundColor Cyan
    
} catch {
    Write-Host "`n❌ Error: $_" -ForegroundColor Red
    exit 1
} finally {
    # Cleanup temporary directory
    if (Test-Path $tempDir) {
        Remove-Item -Path $tempDir -Recurse -Force
        Write-Host "`nCleaned up temporary files." -ForegroundColor Yellow
    }
}

Write-Host "`n✨ Done! Your client ZIP is ready." -ForegroundColor Green

