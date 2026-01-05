# Generate Asset Sprite Sheets
# 
# This script generates sprite sheets from source video files using ffmpeg.
# Required: ffmpeg installed and in PATH
#
# Usage: .\generate_assets.ps1
# Or:    .\generate_assets.ps1 -VideoPath "path/to/mouse.mp4" -OutputPath "output/mouse_sheet.png"

param(
    [string]$VideoPath = "$PSScriptRoot/../src/pyglet_readme/assets/source/mouse.mp4",
    [string]$OutputPath = "$PSScriptRoot/../src/pyglet_readme/assets/sprites/mouse_sheet.png",
    [int]$GridWidth = 10,
    [int]$GridHeight = 10,
    [int]$FrameWidth = 100,
    [int]$FrameHeight = 100,
    [switch]$Force = $false
)

# Resolve paths
$VideoPath = Resolve-Path -Path $VideoPath -ErrorAction SilentlyContinue
$OutputDir = Split-Path -Path $OutputPath -Parent

if (-not $VideoPath) {
    Write-Error "Video source file not found: $VideoPath"
    exit 1
}

if (-not (Test-Path $OutputDir)) {
    Write-Host "Creating output directory: $OutputDir"
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}

# Check if ffmpeg is installed
$ffmpeg = Get-Command ffmpeg -ErrorAction SilentlyContinue
if (-not $ffmpeg) {
    Write-Error "ffmpeg not found. Please install ffmpeg and add it to PATH."
    Write-Host "Download from: https://ffmpeg.org/download.html"
    exit 1
}

# Check if output file already exists
if ((Test-Path $OutputPath) -and -not $Force) {
    Write-Host "Output file already exists: $OutputPath"
    Write-Host "Use -Force to regenerate."
    exit 0
}

Write-Host "Generating sprite sheet from video..."
Write-Host "  Video: $VideoPath"
Write-Host "  Output: $OutputPath"
Write-Host "  Grid: ${GridWidth}x${GridHeight} (${FrameWidth}x${FrameHeight} px per frame)"

# Get video info to determine frame count and fps
Write-Host "Analyzing video..."
$ffprobe = Get-Command ffprobe -ErrorAction SilentlyContinue
if ($ffprobe) {
    $duration = & ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 $VideoPath
    $fps = & ffprobe -v error -select_streams v:0 -show_entries stream=r_frame_rate -of default=noprint_wrappers=1:nokey=1 $VideoPath
    $total_frames = [int]([decimal]$duration * [decimal]$fps)
    Write-Host "  Duration: ${duration}s, FPS: $fps, Est. frames: $total_frames"
} else {
    Write-Host "  (ffprobe not found, skipping detailed analysis)"
}

# Calculate required number of frames
$required_frames = $GridWidth * $GridHeight
Write-Host "  Extracting $required_frames frames..."

# Extract frames from video
# Sample every Nth frame to get exactly GridWidth*GridHeight frames
# fps=-n extracts exactly n frames evenly distributed
$fps_filter = "fps=n=$required_frames"
$scale_filter = "scale=$FrameWidth`:$FrameHeight"
$tile_filter = "tile=$GridWidth`:$GridHeight"

Write-Host "Running ffmpeg..."
$ffmpeg_args = @(
    "-i", $VideoPath,
    "-vf", "$fps_filter,$scale_filter,$tile_filter",
    "-y",  # Overwrite output
    $OutputPath
)

& ffmpeg @ffmpeg_args

if ($LASTEXITCODE -eq 0) {
    $output_size_mb = ((Get-Item $OutputPath).Length / 1MB)
    Write-Host "✓ Sprite sheet generated successfully!"
    Write-Host "  File size: $([math]::Round($output_size_mb, 2)) MB"
    Write-Host "  Location: $OutputPath"
} else {
    Write-Error "ffmpeg failed with exit code $LASTEXITCODE"
    exit 1
}
