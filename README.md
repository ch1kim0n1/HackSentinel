# HackSentinel

MindCore's open source hackathon oriented software.

## MindCore · Sentinel

A deterministic, time-boxed bug discovery tool that explores a codebase like a rushed demo judge and outputs engineer-grade bug reports.

### Features

- **CLI-first**: Simple command-line interface for easy integration
- **Local-only**: No cloud dependencies, no authentication required
- **Deterministic**: Consistent results across runs
- **Fast**: Executes under 2 minutes with configurable timeout
- **Multi-language**: Supports Node.js, Python, Go, Rust, Java, and more
- **Structured Reports**: Markdown bug reports with severity rankings
- **Zero Configuration**: Automatically infers entry points and user flows

### Installation

The tool is self-contained in a single Python script:

```bash
chmod +x mindcore-sentinel
./mindcore-sentinel /path/to/project
```

### Usage

Basic usage:
```bash
./mindcore-sentinel /path/to/project
```

With timeout (in seconds):
```bash
./mindcore-sentinel /path/to/project --timeout 60
```

Save report to file:
```bash
./mindcore-sentinel /path/to/project --output bug-report.md
```

### How It Works

1. **Project Detection**: Automatically identifies the project type (Node.js, Python, Go, etc.)
2. **Entry Point Discovery**: Finds executable entry points (main files, package.json scripts, etc.)
3. **Execution Simulation**: Runs each entry point and captures output
4. **Bug Analysis**: Analyzes exit codes, error messages, and patterns to identify bugs
5. **Report Generation**: Creates a structured Markdown report with severity rankings

### Supported Project Types

- **Node.js**: Detects package.json scripts and common entry files (index.js, app.js, etc.)
- **Python**: Finds main.py, __main__.py modules, and executable scripts
- **Go**: Discovers main.go files and go.mod modules
- **Rust**: Detects Cargo.toml projects
- **Java**: Supports Maven (pom.xml) and Gradle (build.gradle)
- **Makefile**: Executes make targets
- **Generic**: Finds any executable files

### Bug Severity Levels

- **CRITICAL**: Segmentation faults, panics, fatal errors
- **HIGH**: Unhandled exceptions, assertion failures, non-zero exits
- **MEDIUM**: Warnings, missing dependencies, timeouts
- **LOW**: Connection issues, minor errors

### Example Output

```markdown
# MindCore · Sentinel Bug Report

**Analysis Date:** 2026-02-07 00:54:27
**Target Directory:** `/tmp/test-project`
**Analysis Duration:** 0.40s

## Summary

Found **1** potential bug(s):

- **HIGH:** 1

## Detailed Findings

### HIGH Severity

#### Bug #1: Process exited with code 1

**Type:** `non_zero_exit`

**Description:**

The entry point 'npm script: error' terminated with a non-zero exit code.

**Reproduction Steps:**

```bash
npm run error
```
```

### Limitations

- Focuses on runtime bugs only (ignores security and performance issues)
- Does not require or use 3rd party APIs
- Execution timeout per entry point: 10 seconds
- Global timeout: 120 seconds (configurable)

### Contributing

This is open source hackathon software. Feel free to contribute improvements!
