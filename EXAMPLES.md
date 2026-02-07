# MindCore · Sentinel Examples

This directory contains example projects that demonstrate the capabilities of MindCore · Sentinel.

## Example 1: Simple Node.js Project

A basic Node.js project with various scripts that demonstrate bug detection.

### Files:
- `package.json` - Defines npm scripts
- `index.js` - Working entry point
- `error.js` - Script with an error
- `crash.js` - Script that crashes

### Run:
```bash
./mindcore-sentinel examples/nodejs-example
```

### Expected Output:
The tool will detect:
- 1 HIGH severity bug in error.js (non-zero exit)
- 1 HIGH severity bug in crash.js (exception)

## Example 2: Python Project

A Python project with various entry points.

### Files:
- `requirements.txt` - Python dependencies
- `main.py` - Working entry point
- `buggy.py` - Script with bugs

### Run:
```bash
./mindcore-sentinel examples/python-example
```

## Creating Your Own Test Cases

1. Create a directory with your code
2. Ensure there are executable entry points (package.json scripts, main files, etc.)
3. Run: `./mindcore-sentinel /path/to/your/project`
4. Review the generated bug report

## Tips

- The tool will automatically detect the project type
- Entry points are executed with a 10-second timeout each
- The total analysis timeout is 120 seconds by default
- Use `--timeout` to adjust the global timeout
- Use `--output` to save the report to a file
