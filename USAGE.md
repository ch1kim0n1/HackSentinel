# MindCore · Sentinel - Usage Guide for New Developers

Welcome! This guide will help you understand how to use MindCore · Sentinel to automatically discover bugs in your codebase.

## What is MindCore · Sentinel?

MindCore · Sentinel is a **bug discovery tool** that acts like a rushed demo judge at a hackathon. It:
- 🔍 Explores your codebase automatically
- 🚀 Runs your application's entry points
- 🐛 Detects bugs and errors
- 📝 Generates a detailed bug report

**No configuration needed!** Just point it at your project.

---

## Getting Started

### Step 1: Make the tool executable

```bash
chmod +x mindcore-sentinel
```

### Step 2: Run it on your project

```bash
./mindcore-sentinel /path/to/your/project
```

That's it! The tool will automatically analyze your codebase.

---

## What Happens When You Run It?

Here's a step-by-step breakdown of what the tool does:

### Phase 1: Project Detection (< 1 second)
```
[00:00:00.001] Analyzing directory: /path/to/your/project
[00:00:00.001] Project type detected: nodejs
```

**What's happening:**
- The tool scans your directory for markers like `package.json`, `requirements.txt`, `go.mod`, etc.
- It identifies your programming language/framework
- Supported: Node.js, Python, Go, Rust, Java, Makefiles, and more

### Phase 2: Entry Point Discovery (< 1 second)
```
[00:00:00.002] Found 5 entry points
```

**What's happening:**
- The tool finds all runnable parts of your code:
  - **Node.js**: package.json scripts, index.js, app.js, server.js
  - **Python**: main.py, __main__.py modules, executable scripts
  - **Go**: main.go files, go.mod packages
  - And more for other languages

**No entry points found?** The tool will tell you and exit gracefully.

### Phase 3: Execution Simulation (most time spent here)
```
[00:00:00.003] Executing: Main entry point: index.js
[00:00:00.120] Executing: npm script: start
[00:00:00.450] Executing: npm script: test
```

**What's happening:**
- Each entry point is executed one at a time
- The tool captures everything: output, errors, exit codes
- Each execution has a **10-second timeout** (so runaway processes don't hang)
- The **total timeout is 2 minutes** (120 seconds) by default

**Your code won't be modified!** The tool only reads and executes.

### Phase 4: Bug Analysis (< 1 second)
```
[00:00:02.000] Analysis complete. Found 3 potential bugs
```

**What's happening:**
- The tool analyzes all captured outputs
- It looks for error patterns: crashes, exceptions, non-zero exits
- Each bug is classified by severity (CRITICAL, HIGH, MEDIUM, LOW)

### Phase 5: Report Generation (< 1 second)

The tool outputs a beautiful Markdown report to your terminal (or a file if you specified `--output`).

---

## Understanding the Report

### Report Structure

```markdown
# MindCore · Sentinel Bug Report

**Analysis Date:** 2026-02-07 01:00:00
**Target Directory:** `/path/to/your/project`
**Analysis Duration:** 2.45s

## Summary
Found **3** potential bug(s):
- **CRITICAL:** 1
- **HIGH:** 2

## Detailed Findings
[Details for each bug...]

## Diagnostic Logs
[Execution timeline and logs...]
```

### Bug Severity Levels

| Severity | What it means | Examples |
|----------|---------------|----------|
| **🔴 CRITICAL** | Your app crashes catastrophically | Segmentation faults, panics, exit code > 100 |
| **🟠 HIGH** | Your app fails to run properly | Uncaught exceptions, non-zero exits, assertion failures |
| **🟡 MEDIUM** | Your app has warnings or timeouts | Missing dependencies, execution timeouts |
| **🟢 LOW** | Minor issues that don't stop execution | Connection errors, deprecated warnings |

### Bug Report Details

Each bug includes:

1. **Title**: Brief description of the issue
2. **Type**: Category (e.g., `non_zero_exit`, `error_pattern`, `execution_error`)
3. **Description**: What went wrong
4. **Reproduction Steps**: Exact command to reproduce the bug
5. **Output**: Captured stdout/stderr showing the error

**Example:**
```markdown
#### Bug #1: Process exited with code 1

**Type:** `non_zero_exit`

**Description:**
The entry point 'npm script: test' terminated with a non-zero exit code.

**Reproduction Steps:**
```bash
npm run test
```

**Output:**
*STDERR:*
```
Error: Test failed
    at runTests (test.js:42:11)
```
```

---

## Common Usage Scenarios

### Scenario 1: Quick Check (Current Directory)

```bash
./mindcore-sentinel .
```

**When to use:** You're in your project directory and want a quick bug scan.

**What happens:**
- Analyzes the current directory
- Outputs report to terminal
- Takes 10-30 seconds typically

### Scenario 2: Check a Specific Project

```bash
./mindcore-sentinel /path/to/my-app
```

**When to use:** Analyzing a project in a different location.

**What happens:**
- Analyzes the specified directory
- Outputs report to terminal

### Scenario 3: Save Report to File

```bash
./mindcore-sentinel /path/to/my-app --output bug-report.md
```

**When to use:** You want to save the report for later review or sharing.

**What happens:**
- Analyzes the project
- Saves report to `bug-report.md`
- Prints summary to terminal

### Scenario 4: Quick Scan with Shorter Timeout

```bash
./mindcore-sentinel /path/to/my-app --timeout 30
```

**When to use:** You want a faster scan (useful for CI/CD pipelines).

**What happens:**
- Analyzes project with 30-second total timeout
- May not execute all entry points if time runs out
- Still produces a complete report for what it tested

### Scenario 5: Comprehensive Analysis

```bash
./mindcore-sentinel /path/to/my-app --timeout 300 --output full-report.md
```

**When to use:** Deep analysis before a major release or demo.

**What happens:**
- Takes up to 5 minutes to test everything
- Saves detailed report to file
- Tests all entry points thoroughly

---

## Real-World Examples

### Example 1: Node.js Web App

**Your project structure:**
```
my-app/
├── package.json
├── server.js
├── routes/
└── tests/
```

**Running the tool:**
```bash
./mindcore-sentinel my-app
```

**What gets tested:**
- `node server.js` (main entry point)
- All scripts in package.json (start, test, build, etc.)
- Any executable files

**Sample output:**
```
[00:00:00.001] Project type detected: nodejs
[00:00:00.001] Found 4 entry points
[00:00:00.001] Executing: Main entry point: server.js
[00:00:00.150] Executing: npm script: start
[00:00:00.300] Executing: npm script: test
[00:00:00.450] Executing: npm script: build
[00:00:00.600] Analysis complete. Found 1 potential bugs
```

### Example 2: Python CLI Tool

**Your project structure:**
```
my-tool/
├── requirements.txt
├── main.py
├── cli.py
└── tests/
```

**Running the tool:**
```bash
./mindcore-sentinel my-tool
```

**What gets tested:**
- `python3 main.py`
- `python3 cli.py`
- Any Python modules with `__main__.py`

**Sample output:**
```
[00:00:00.001] Project type detected: python
[00:00:00.001] Found 2 entry points
[00:00:00.001] Executing: Common Python entry file: main.py
[00:00:00.200] Executing: Common Python entry file: cli.py
[00:00:00.400] Analysis complete. Found 0 potential bugs

✅ No bugs detected!
```

### Example 3: Go Application

**Your project structure:**
```
my-service/
├── go.mod
├── main.go
└── pkg/
```

**Running the tool:**
```bash
./mindcore-sentinel my-service
```

**What gets tested:**
- `go run main.go`
- `go run .` (module execution)

---

## Interpreting Results

### ✅ No Bugs Found

```markdown
## Summary
✅ **No bugs detected!**

The codebase executed successfully without any detected errors or issues.
```

**What this means:**
- All entry points ran successfully
- No crashes or exceptions detected
- All exit codes were 0 (success)

**Note:** This doesn't mean your code is bug-free! It means no obvious runtime errors were detected during execution.

### 🐛 Bugs Found

```markdown
## Summary
Found **2** potential bug(s):
- **HIGH:** 2
```

**What to do:**
1. Read each bug's description carefully
2. Use the reproduction steps to verify the bug
3. Check the output section for stack traces and error messages
4. Fix the issues in your code
5. Run the tool again to verify fixes

### ⚠️ Analysis Failed

```
⚠️ ANALYSIS FAILED - See diagnostic logs above
```

**Common causes:**
- No entry points found (add a main.py, index.js, etc.)
- Invalid project directory
- Permissions issues

**What to do:**
1. Check the diagnostic logs at the end of the report
2. Verify your project has runnable entry points
3. Ensure the tool has permission to read/execute files

---

## Tips for Best Results

### ✅ DO:

- **Run on projects with clear entry points** (main files, package.json scripts)
- **Fix dependencies first** (run `npm install`, `pip install -r requirements.txt`, etc.)
- **Use in CI/CD pipelines** for automated bug detection
- **Save reports** to track bugs over time
- **Run before demos** to catch embarrassing bugs

### ❌ DON'T:

- Run on projects requiring **user input** (the tool can't provide interactive input)
- Run on projects requiring **authentication/API keys** (no credentials are provided)
- Expect **security vulnerability detection** (this tool focuses on runtime bugs)
- Expect **performance analysis** (this tool doesn't profile code)
- Run on projects with **destructive operations** (use test/dev environments)

---

## Advanced Options

### Custom Timeout

Control how long the analysis runs:

```bash
# 30-second timeout (fast scan)
./mindcore-sentinel /path/to/project --timeout 30

# 5-minute timeout (thorough scan)
./mindcore-sentinel /path/to/project --timeout 300
```

### Output to File

Save the report instead of printing to terminal:

```bash
./mindcore-sentinel /path/to/project --output bugs.md
```

You can then:
- Open `bugs.md` in any Markdown viewer
- Share with your team
- Track bugs over time by keeping multiple reports

### Help Command

See all available options:

```bash
./mindcore-sentinel --help
```

---

## Troubleshooting

### Problem: "Target directory does not exist"

```bash
ERROR: Target directory does not exist: /path/to/project
```

**Solution:** Check the path is correct:
```bash
ls /path/to/project  # Verify directory exists
./mindcore-sentinel $(pwd)  # Use absolute path
```

### Problem: "No entry points found"

```
[00:00:00.001] WARNING: No entry points found
```

**Solution:** Add an entry point:
- **Node.js:** Create `index.js` or add scripts to `package.json`
- **Python:** Create `main.py` or add `__main__.py` to a module
- **Go:** Ensure you have `main.go` with a main function

### Problem: "Execution timeout"

```markdown
#### Bug #1: Execution error: Execution timeout (10s)
```

**This is expected!** It means:
- An entry point ran for more than 10 seconds
- The tool killed it to prevent hanging
- This might be a long-running server or process

**Solutions:**
- If it's a server, this is normal behavior (servers don't exit)
- If it's a bug (infinite loop), investigate and fix
- Increase global timeout if needed: `--timeout 300`

### Problem: "Command not found" errors

```
Error: Cannot find module '/path/to/file'
```

**Solution:** Install dependencies first:
```bash
# Node.js
npm install

# Python
pip install -r requirements.txt

# Go
go mod download
```

---

## Integration with Development Workflow

### Before Committing

```bash
./mindcore-sentinel . --output pre-commit-bugs.md
git add .
git commit -m "Fix: Resolved bugs found by Sentinel"
```

### In CI/CD Pipeline

```yaml
# Example GitHub Actions workflow
- name: Bug Discovery
  run: |
    ./mindcore-sentinel . --timeout 60 --output bug-report.md
    cat bug-report.md
```

### Before Demos

```bash
# Quick check 1 hour before demo
./mindcore-sentinel . --timeout 30
```

### Daily Health Checks

```bash
# Add to daily cron job
0 9 * * * cd /path/to/project && ./mindcore-sentinel . --output daily-report-$(date +%Y%m%d).md
```

---

## FAQ

**Q: Will this modify my code?**  
A: No! The tool only reads files and executes them. It never modifies your source code.

**Q: Is my code safe?**  
A: Yes. Everything runs locally. No data is sent to external services.

**Q: How long does it take?**  
A: Usually 10-30 seconds. Maximum 2 minutes by default (configurable).

**Q: What if my app needs a database?**  
A: The tool will report connection errors as LOW severity bugs. Run in a test environment with dependencies.

**Q: Can I use this in production?**  
A: It's designed for dev/test environments. Don't run on production servers!

**Q: Does it find all bugs?**  
A: No tool can find all bugs. This tool finds **runtime errors** from executing entry points. Use it alongside testing, code review, and other tools.

**Q: Why did it find false positives?**  
A: Sometimes "bugs" are expected (e.g., a script that intentionally exits with code 1). Use your judgment.

**Q: Can I exclude certain files/scripts?**  
A: Currently no. The tool automatically finds and tests all entry points.

---

## Getting Help

If you encounter issues:

1. Check the **Diagnostic Logs** section in the report
2. Review this guide's **Troubleshooting** section
3. Verify your project has standard entry points
4. Try with `--timeout 30` for a quick test

---

## Quick Command Reference

```bash
# Basic usage
./mindcore-sentinel /path/to/project

# Common options
./mindcore-sentinel /path/to/project --timeout 60
./mindcore-sentinel /path/to/project --output report.md
./mindcore-sentinel /path/to/project --timeout 30 --output quick-scan.md

# Current directory
./mindcore-sentinel .

# Help
./mindcore-sentinel --help
```

---

**Happy bug hunting! 🐛🔍**
