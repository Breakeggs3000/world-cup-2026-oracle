#Requires -Version 5.1
<#
.SYNOPSIS
  Create a new agent workspace from the pilot101 template.

.EXAMPLE
  .\new-agent-project.ps1 my-vibe-app -Purpose "Minimal todo app" -InitGit

.EXAMPLE
  .\new-agent-project.ps1 my-vibe-app -DryRun
#>
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$Name,

    [string]$Purpose = "",
    [string]$Parent = "",
    [switch]$InitGit,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$TemplateRoot = (Resolve-Path (Join-Path $ScriptDir "..\..")).Path

if (-not (Test-Path (Join-Path $TemplateRoot "AGENTS.md"))) {
    Write-Error "AGENTS.md not found. Run from pilot101 template."
    exit 1
}

function Get-Slug([string]$Value) {
    $slug = ($Value.ToLower() -replace '[^a-z0-9]+', '-').Trim('-')
    if ([string]::IsNullOrWhiteSpace($slug)) { return "project" }
    return $slug
}

$Slug = Get-Slug $Name
$ParentDir = if ($Parent) { (Resolve-Path $Parent).Path } else { Split-Path $TemplateRoot -Parent }
$Dest = Join-Path $ParentDir $Slug

$SkipNames = @('.git', '__pycache__', '.ruff_cache', 'node_modules', '.venv', 'venv')
$TemplateOnly = @('TEMPLATE.md')

$OverviewTemplate = @'
# Project overview

> Agents read this at session start.

## Name

'@ + "`n" + $Name + "`n" + @'

## Purpose

'@ + "`n" + $(if ($Purpose) { $Purpose } else { '_Describe what you are building._' }) + "`n" + @'

## Current status

Greenfield - workspace scaffold ready; application code not yet started.

## Tech stack

_To be decided._ Document choices here before agents implement in `src/`.

## Repository map

| Path | Contents |
|------|----------|
| `src/` | Application source |
| `agents/` | Role and crew definitions |
| `tasks/` | Work backlog |
| `workspace/` | Scratch and artifacts |

## Success criteria

_Define what "done" looks like for this product._

## Contacts / ownership

_Optional._
'@

$ReadmeTemplate = @(
    "# $Name"
    ""
    "Generated from the agent workspace template (pilot101)."
    ""
    "## Getting started"
    ""
    "1. Read [AGENTS.md](./AGENTS.md)."
    "2. Fill in [context/project/overview.md](./context/project/overview.md)."
    "3. Build in ``src/``."
    "4. Track work in ``tasks/backlog/``."
    ""
    "## Agent workspace"
    ""
    "Universal Cursor rules live in ``~/.cursor/rules/``; project-specific rules go in ``.cursor/rules/``."
) -join "`n"

function Should-Skip([string]$RelativePath) {
    $parts = $RelativePath -split '[\\/]'
    foreach ($part in $parts) {
        if ($SkipNames -contains $part) { return $true }
    }
    $leaf = Split-Path $RelativePath -Leaf
    if ($TemplateOnly -contains $leaf) { return $true }
    return $false
}

function Write-Utf8File([string]$Path, [string]$Content) {
    $dir = Split-Path $Path -Parent
    if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
    $utf8 = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::WriteAllText($Path, $Content, $utf8)
}

function Clear-WorkspaceState([string]$Root) {
    $patterns = @(
        "workspace\scratch\*",
        "memory\facts\*",
        "tasks\backlog\*",
        "workspace\artifacts\research\*",
        "workspace\artifacts\reviews\*"
    )
    foreach ($pattern in $patterns) {
        Get-ChildItem -Path (Join-Path $Root $pattern) -Force -ErrorAction SilentlyContinue |
            Where-Object { $_.Name -ne '.gitkeep' } |
            ForEach-Object {
                if ($DryRun) {
                    Write-Host "[dry-run] Would remove: $($_.FullName)"
                } else {
                    Remove-Item $_.FullName -Recurse -Force
                }
            }
    }
}

if (Test-Path $Dest) {
    Write-Error "Destination already exists: $Dest"
    exit 1
}

if ($DryRun) {
    Write-Host "[dry-run] Would create: $Dest"
} else {
    New-Item -ItemType Directory -Path $Dest | Out-Null
}

Get-ChildItem -Path $TemplateRoot -Recurse -Force | ForEach-Object {
    $rel = $_.FullName.Substring($TemplateRoot.Length).TrimStart('\', '/')
    if ([string]::IsNullOrWhiteSpace($rel)) { return }
    if (Should-Skip $rel) { return }

    $target = Join-Path $Dest $rel
    if ($_.PSIsContainer) {
        if (-not $DryRun) {
            New-Item -ItemType Directory -Path $target -Force | Out-Null
        }
    } else {
        if ($DryRun) {
            Write-Host "[dry-run] Would copy: $rel"
        } else {
            $dir = Split-Path $target -Parent
            if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
            Copy-Item $_.FullName $target -Force
        }
    }
}

Clear-WorkspaceState $Dest

$files = @{
    "context\project\overview.md" = $OverviewTemplate
    "README.md"                   = $ReadmeTemplate
}

$config = @{
    kind     = "agent-workspace-project"
    version  = "1"
    name     = $Name
    slug     = $Slug
    created  = (Get-Date -Format "yyyy-MM-dd")
    template = "pilot101"
} | ConvertTo-Json -Depth 3

$files["template.config.json"] = $config + "`n"

foreach ($entry in $files.GetEnumerator()) {
    $path = Join-Path $Dest $entry.Key
    if ($DryRun) {
        Write-Host "[dry-run] Would write: $($entry.Key)"
    } else {
        Write-Utf8File -Path $path -Content $entry.Value
    }
}

if ($InitGit) {
    if ($DryRun) {
        Write-Host "[dry-run] Would run: git init in $Dest"
    } else {
        Push-Location $Dest
        git init | Out-Null
        Pop-Location
    }
}

if ($DryRun) {
    Write-Host "[dry-run] Ready: $Dest"
} else {
    Write-Host "Created agent workspace: $Dest"
    Write-Host "Next steps:"
    Write-Host "  cd $Dest"
    Write-Host "  Edit context/project/overview.md"
    Write-Host "  Start building in src/"
}
