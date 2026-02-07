# MindCore · Sentinel - Quick Reference

## Installation

The tool is a single Python 3 script. No installation needed!

```bash
chmod +x mindcore-sentinel
```

## Basic Usage

```bash
# Analyze current directory
./mindcore-sentinel .

# Analyze specific directory
./mindcore-sentinel /path/to/project

# Set custom timeout (in seconds)
./mindcore-sentinel /path/to/project --timeout 60

# Save report to file
./mindcore-sentinel /path/to/project --output report.md

# Demo mode (no project required)
./mindcore-sentinel --demo

# JSON output
./mindcore-sentinel /path/to/project --format json

# JSON with excluded paths
./mindcore-sentinel . --format json --exclude "test/*" --exclude "dist/*"

# Safe mode (extra precautions)
./mindcore-sentinel /path/to/project --safe-mode
```

## How It Works

1. **Detects Project Type**: Identifies the programming language/framework
2. **Finds Entry Points**: Discovers executable files, scripts, and commands
3. **Executes Code**: Runs each entry point and captures output
4. **Analyzes Results**: Identifies bugs from exit codes and error messages
5. **Generates Report**: Creates a structured Markdown bug report

## Supported Languages

- **Node.js**: package.json, .js files
- **Python**: requirements.txt, .py files, **main**.py
- **Go**: go.mod, main.go
- **Rust**: Cargo.toml
- **Java**: pom.xml, build.gradle
- **C/C++**: Makefile
- **Shell**: Executable scripts

## Severity Levels

| Severity     | Exit Code | Keywords                           |
| ------------ | --------- | ---------------------------------- |
| **CRITICAL** | >100      | fatal, panic, segmentation fault   |
| **HIGH**     | 1-100     | error, exception, assertion failed |
| **MEDIUM**   | N/A       | warning, timeout, cannot find      |
| **LOW**      | N/A       | connection refused                 |

## Report Format

```markdown
# MindCore · Sentinel Bug Report

## Summary

- Lists total bugs by severity

## Detailed Findings

- Grouped by severity level
- Each bug includes:
  - Type and description
  - Reproduction steps
  - Output (stdout/stderr)

## Diagnostic Logs

- Execution timeline
- Entry points discovered
- Errors encountered
```

## Exit Codes

- **0**: Analysis completed successfully (bugs may or may not be found)
- **1**: Analysis failed (e.g., no entry points found)

## Limitations

- Per-entry-point timeout: 10 seconds
- Global timeout: 120 seconds (configurable)
- Only analyzes runtime bugs (not security or performance)
- No network/cloud features
- No 3rd party API dependencies

## Tips

✅ **DO:**

- Run on codebases with clear entry points
- Use custom timeouts for slow projects
- Check diagnostic logs if analysis fails

❌ **DON'T:**

- Expect security vulnerability detection
- Expect performance profiling
- Run on projects requiring authentication
- Run on projects with destructive scripts

## Troubleshooting

**"No entry points found"**

- Ensure your project has executable files or package.json scripts
- Add a main.py, index.js, or similar entry file

**"Execution timeout"**

- Increase timeout: `--timeout 180`
- Check if entry point requires input

**"Analysis failed"**

- Check diagnostic logs section
- Verify project is runnable
- Ensure dependencies are installed

## Examples

```bash
# Quick scan of current directory
./mindcore-sentinel . --timeout 30

# Full analysis with report
./mindcore-sentinel /path/to/app --output bugs.md

# Analyze multiple projects
for dir in projects/*; do
  ./mindcore-sentinel "$dir" --output "report-$(basename $dir).md"
done
```
