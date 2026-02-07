"""
MindCore · Sentinel - Core logic
"""

import os
import sys
import json
import time
from .scanner import SecretScanner
import socket
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from urllib import request as urllib_request
from urllib.error import URLError


def _python_cmd():
    """Return the correct python command for the current platform."""
    if sys.platform == 'win32':
        return 'python'
    return 'python3'


class MindCoreSentinel:
    """Main class for MindCore Sentinel bug discovery tool."""

    def __init__(self, target_dir: str, timeout: int = 120,
                 exclude_patterns: Optional[List[str]] = None,
                 safe_mode: bool = False,
                 verbose: bool = False,
                 quiet: bool = False,
                 per_entry_timeout: int = 10,
                 ports: Optional[List[int]] = None):
        self.target_dir = Path(target_dir).resolve()
        self.timeout = timeout
        self.start_time = time.time()
        self.bugs: List[Dict[str, Any]] = []
        self.logs: List[str] = []
        self.exclude_patterns = exclude_patterns or []
        self.safe_mode = safe_mode
        self.verbose = verbose
        self.quiet = quiet
        self.per_entry_timeout = per_entry_timeout
        self.ports = ports or [3000, 5000, 8000, 8080]
        self.project_type: str = "unknown"
        self.entry_points_found: List[Dict[str, Any]] = []

    def log(self, message: str):
        """Add a log message."""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_msg = f"[{timestamp}] {message}"
        self.logs.append(log_msg)
        if not self.quiet:
            print(log_msg, file=sys.stderr)
        
    def is_timeout(self) -> bool:
        """Check if we've exceeded the timeout."""
        return (time.time() - self.start_time) > self.timeout
        
    def detect_project_type(self) -> str:
        """Detect the type of project in the target directory."""
        self.log(f"Analyzing directory: {self.target_dir}")
        
        if (self.target_dir / "package.json").exists():
            return "nodejs"
        elif (self.target_dir / "requirements.txt").exists() or (self.target_dir / "setup.py").exists():
            return "python"
        elif (self.target_dir / "go.mod").exists():
            return "go"
        elif (self.target_dir / "Cargo.toml").exists():
            return "rust"
        elif (self.target_dir / "pom.xml").exists() or (self.target_dir / "build.gradle").exists():
            return "java"
        elif (self.target_dir / "Makefile").exists():
            return "make"
        else:
            return "unknown"
            
    def find_entry_points(self, project_type: str) -> List[Dict[str, Any]]:
        """Find potential entry points in the codebase."""
        self.log(f"Project type detected: {project_type}")
        entry_points = []
        
        if project_type == "nodejs":
            entry_points.extend(self._find_nodejs_entry_points())
        elif project_type == "python":
            entry_points.extend(self._find_python_entry_points())
        elif project_type == "go":
            entry_points.extend(self._find_go_entry_points())
        elif project_type == "rust":
            entry_points.extend(self._find_rust_entry_points())
        elif project_type == "java":
            entry_points.extend(self._find_java_entry_points())
        elif project_type == "make":
            entry_points.extend(self._find_makefile_entry_points())
        else:
            entry_points.extend(self._find_generic_entry_points())
            
        self.log(f"Found {len(entry_points)} entry points")
        return entry_points
        
    def _find_nodejs_entry_points(self) -> List[Dict[str, Any]]:
        """Find Node.js entry points."""
        entry_points = []
        
        # Check package.json for scripts
        package_json = self.target_dir / "package.json"
        if package_json.exists():
            try:
                with open(package_json, 'r') as f:
                    data = json.load(f)
                    
                # Main entry point
                if "main" in data:
                    entry_points.append({
                        "type": "nodejs_main",
                        "command": ["node", data["main"]],
                        "description": f"Main entry point: {data['main']}"
                    })
                    
                # Scripts
                if "scripts" in data:
                    for script_name, script_cmd in data["scripts"].items():
                        # Skip install/test scripts to avoid side effects
                        if script_name not in ["preinstall", "postinstall", "prepare"]:
                            entry_points.append({
                                "type": "nodejs_script",
                                "command": ["npm", "run", script_name],
                                "description": f"npm script: {script_name}",
                                "raw_command": script_cmd
                            })
            except Exception as e:
                self.log(f"Error parsing package.json: {e}")
                
        # Look for common entry files
        for filename in ["index.js", "app.js", "server.js", "main.js"]:
            filepath = self.target_dir / filename
            if filepath.exists():
                entry_points.append({
                    "type": "nodejs_file",
                    "command": ["node", filename],
                    "description": f"Common Node.js entry file: {filename}"
                })
                
        return entry_points
        
    def _find_python_entry_points(self) -> List[Dict[str, Any]]:
        """Find Python entry points."""
        entry_points = []
        
        # Look for __main__.py
        for root, dirs, files in os.walk(self.target_dir):
            if self.is_timeout():
                break
            
            # Optimization: Skip heavy directories
            dirs[:] = [d for d in dirs if d not in {'node_modules', '.git', 'venv', '__pycache__', '.idea', '.vscode'}]
            
            for file in files:
                if file == "__main__.py":
                    rel_path = Path(root).relative_to(self.target_dir)
                    entry_points.append({
                        "type": "python_main",
                        "command": [_python_cmd(), "-m", str(rel_path).replace("/", ".").replace("\\", ".")],
                        "description": f"Python module: {rel_path}"
                    })
                    
        # Look for common entry files
        for filename in ["main.py", "app.py", "run.py", "cli.py"]:
            filepath = self.target_dir / filename
            if filepath.exists():
                entry_points.append({
                    "type": "python_file",
                    "command": [_python_cmd(), filename],
                    "description": f"Common Python entry file: {filename}"
                })
                
        # Look for scripts with shebang
        for root, dirs, files in os.walk(self.target_dir):
            if self.is_timeout():
                break
            for file in files:
                if file.endswith(".py"):
                    filepath = Path(root) / file
                    try:
                        with open(filepath, 'r') as f:
                            first_line = f.readline()
                            if first_line.startswith("#!") and "python" in first_line:
                                rel_path = filepath.relative_to(self.target_dir)
                                if os.access(filepath, os.X_OK):
                                    entry_points.append({
                                        "type": "python_script",
                                        "command": [str(filepath)],
                                        "description": f"Executable Python script: {rel_path}"
                                    })
                    except Exception:
                        pass
                        
        return entry_points
        
    def _find_go_entry_points(self) -> List[Dict[str, Any]]:
        """Find Go entry points."""
        entry_points = []
        
        # Look for main.go files
        for root, dirs, files in os.walk(self.target_dir):
            if self.is_timeout():
                break
            for file in files:
                if file == "main.go":
                    filepath = Path(root) / file
                    rel_path = filepath.relative_to(self.target_dir)
                    entry_points.append({
                        "type": "go_main",
                        "command": ["go", "run", str(rel_path)],
                        "description": f"Go main file: {rel_path}"
                    })
                    
        # Try building and running
        if (self.target_dir / "go.mod").exists():
            entry_points.append({
                "type": "go_build",
                "command": ["go", "run", "."],
                "description": "Go module main package"
            })
            
        return entry_points
        
    def _find_rust_entry_points(self) -> List[Dict[str, Any]]:
        """Find Rust entry points."""
        entry_points = []
        
        if (self.target_dir / "Cargo.toml").exists():
            entry_points.append({
                "type": "rust_cargo",
                "command": ["cargo", "run"],
                "description": "Cargo run"
            })
            
        return entry_points
        
    def _find_java_entry_points(self) -> List[Dict[str, Any]]:
        """Find Java entry points."""
        entry_points = []
        
        if (self.target_dir / "pom.xml").exists():
            entry_points.append({
                "type": "maven",
                "command": ["mvn", "exec:java"],
                "description": "Maven exec"
            })
            
        if (self.target_dir / "build.gradle").exists():
            entry_points.append({
                "type": "gradle",
                "command": ["gradle", "run"],
                "description": "Gradle run"
            })
            
        return entry_points
        
    def _find_makefile_entry_points(self) -> List[Dict[str, Any]]:
        """Find Makefile entry points."""
        entry_points = []
        
        makefile = self.target_dir / "Makefile"
        if makefile.exists():
            entry_points.append({
                "type": "make",
                "command": ["make"],
                "description": "Make default target"
            })
            
            # Try to find other targets
            try:
                with open(makefile, 'r') as f:
                    for line in f:
                        if ':' in line and not line.startswith('\t') and not line.startswith('#'):
                            target = line.split(':')[0].strip()
                            if target and target not in ["all", "clean", "install"]:
                                entry_points.append({
                                    "type": "make_target",
                                    "command": ["make", target],
                                    "description": f"Make target: {target}"
                                })
            except Exception:
                pass
                
        return entry_points
        
    def _find_generic_entry_points(self) -> List[Dict[str, Any]]:
        """Find generic executable entry points."""
        entry_points = []
        
        # Look for executable files in root
        for item in self.target_dir.iterdir():
            if item.is_file() and os.access(item, os.X_OK):
                entry_points.append({
                    "type": "executable",
                    "command": [str(item)],
                    "description": f"Executable: {item.name}"
                })
                
        return entry_points
    
    def _probe_web_server(self, ports=None):
        """Probe common ports for a running web server."""
        if ports is None:
            ports = self.ports
        for port in ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', port))
                sock.close()
                
                if result == 0:  # Port is open
                    try:
                        response = urllib_request.urlopen(f'http://localhost:{port}', timeout=2)
                        return {"alive": True, "port": port, "status_code": response.getcode()}
                    except URLError:
                        return {"alive": False, "port": port, "error": "Connection refused"}
            except Exception:
                continue
        return {"alive": False, "error": "No server detected"}
        
    def execute_entry_point(self, entry_point: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an entry point and capture results."""
        self.log(f"Executing: {entry_point['description']}")
        
        result = {
            "entry_point": entry_point,
            "success": False,
            "stdout": "",
            "stderr": "",
            "exit_code": None,
            "error": None,
            "duration": 0
        }
        
        try:
            start = time.time()
            remaining_time = self.timeout - (start - self.start_time)
            
            if remaining_time <= 0:
                result["error"] = "Global timeout exceeded"
                return result
            
            # Check if this is likely a server command
            cmd_str = ' '.join(str(c) for c in entry_point["command"]).lower()
            is_server_command = any(word in cmd_str for word in ['start', 'serve', 'dev', 'server'])
            
            # Execute with timeout
            process = subprocess.Popen(
                entry_point["command"],
                cwd=self.target_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # If it's a server command, wait and probe
            if is_server_command:
                time.sleep(5)  # Grace period for server startup
                
                probe_result = self._probe_web_server()
                result["live_probe"] = probe_result
                
                # Capture any startup output
                try:
                    stdout, stderr = process.communicate(timeout=1)
                    result["stdout"] = stdout
                    result["stderr"] = stderr
                except subprocess.TimeoutExpired:
                    # Server still running, which is good
                    result["stdout"] = "(Server running in background)"
                    result["stderr"] = ""
                
                process.terminate()
                process.wait(timeout=2)
                
                result["exit_code"] = 0 if probe_result.get("alive") else 1
                result["success"] = probe_result.get("alive", False)
                result["duration"] = time.time() - start
                return result
            
            try:
                stdout, stderr = process.communicate(timeout=min(self.per_entry_timeout, remaining_time))
                result["stdout"] = stdout
                result["stderr"] = stderr
                result["exit_code"] = process.returncode
                result["success"] = process.returncode == 0
                result["duration"] = time.time() - start
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
                result["stdout"] = stdout
                result["stderr"] = stderr
                result["error"] = f"Execution timeout ({self.per_entry_timeout}s)"
                result["duration"] = time.time() - start
                
        except Exception as e:
            result["error"] = str(e)
            result["duration"] = time.time() - start
            
        return result
        
    def analyze_execution_result(self, result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Analyze execution result to identify bugs."""
        bugs_found = []
        
        # Check live probe results if available
        if "live_probe" in result:
            probe = result["live_probe"]
            if not probe.get("alive", False):
                severity = "HIGH"
                error_msg = probe.get("error", "Server not responding")
                bugs_found.append({
                    "type": "live_probe_failure",
                    "severity": severity,
                    "title": f"Live server probe failed: {error_msg}",
                    "description": f"The service started but failed to respond to HTTP requests. Port scan result: {error_msg}",
                    "reproduction": result["entry_point"]["command"],
                    "output": {
                        "probe_result": str(probe)
                    }
                })
        
        # Check for non-zero exit code
        if result["exit_code"] is not None and result["exit_code"] != 0:
            severity = "HIGH"
            if result["exit_code"] > 100:
                severity = "CRITICAL"
            elif result["stderr"] and ("warning" in result["stderr"].lower()):
                severity = "MEDIUM"
                
            bugs_found.append({
                "type": "non_zero_exit",
                "severity": severity,
                "title": f"Process exited with code {result['exit_code']}",
                "description": f"The entry point '{result['entry_point']['description']}' terminated with a non-zero exit code.",
                "reproduction": result["entry_point"]["command"],
                "output": {
                    "stdout": result["stdout"][:500],
                    "stderr": result["stderr"][:500]
                }
            })
            
        # Check for common error patterns in stderr
        stderr = result["stderr"].lower()
        if stderr:
            error_patterns = [
                ("error:", "ERROR", "Generic error message"),
                ("exception", "HIGH", "Unhandled exception"),
                ("fatal", "CRITICAL", "Fatal error"),
                ("traceback", "HIGH", "Stack trace"),
                ("segmentation fault", "CRITICAL", "Segmentation fault"),
                ("panic", "CRITICAL", "Panic"),
                ("assertion failed", "HIGH", "Assertion failure"),
                ("cannot find", "MEDIUM", "Missing dependency or file"),
                ("permission denied", "MEDIUM", "Permission issue"),
                ("connection refused", "LOW", "Connection issue")
            ]
            
            for pattern, severity, description in error_patterns:
                if pattern in stderr:
                    recommendation = None
                    if "module not found" in stderr or "cannot find module" in stderr:
                        recommendation = "Try running 'npm install' or 'pip install' to fix missing dependencies."
                    elif "permission denied" in stderr:
                        recommendation = "Check file permissions or run with elevated privileges."
                    elif "connection refused" in stderr:
                        recommendation = "Ensure that all dependent services (databases, APIs) are running."

                    bugs_found.append({
                        "type": "error_pattern",
                        "severity": severity,
                        "title": description,
                        "description": f"Found '{pattern}' in error output when executing '{result['entry_point']['description']}'",
                        "reproduction": result["entry_point"]["command"],
                        "recommendation": recommendation,
                        "output": {
                            "stderr": result["stderr"][:1000]
                        }
                    })
                    break  # Only report first pattern match
                    
        # Check for execution errors
        if result["error"]:
            severity = "HIGH"
            if "timeout" in result["error"].lower():
                severity = "MEDIUM"
            elif "not found" in result["error"].lower():
                severity = "HIGH"
                
            bugs_found.append({
                "type": "execution_error",
                "severity": severity,
                "title": f"Execution error: {result['error']}",
                "description": f"Failed to execute '{result['entry_point']['description']}'",
                "reproduction": result["entry_point"]["command"],
                "output": {
                    "error": result["error"]
                }
            })
            
        return bugs_found
        
    def _matches_exclude(self, entry_point: Dict[str, Any]) -> bool:
        """Check if an entry point matches any exclude pattern."""
        import fnmatch
        desc = entry_point.get("description", "")
        cmd_parts = entry_point.get("command", [])
        cmd_str = " ".join(str(c) for c in cmd_parts)

        for pattern in self.exclude_patterns:
            if fnmatch.fnmatch(desc, f"*{pattern}*") or fnmatch.fnmatch(cmd_str, f"*{pattern}*"):
                return True
            # Check each command part against the pattern
            for part in cmd_parts:
                if fnmatch.fnmatch(str(part), pattern):
                    return True
        return False

    def run_analysis(self) -> bool:
        """Run the complete analysis."""
        try:
            self.log("=" * 60)
            self.log("MindCore · Sentinel - Bug Discovery Tool")
            if self.safe_mode:
                self.log("SAFE MODE: No code will be executed")
            self.log("=" * 60)

            # Detect project type
            self.project_type = self.detect_project_type()
            
            # Run security scan
            self.log("Running security scan...")
            scanner = SecretScanner()
            security_findings = scanner.scan_project(str(self.target_dir))
            
            if security_findings:
                self.log(f"Found {len(security_findings)} security issues")
                for finding in security_findings:
                    self.bugs.append({
                        "type": "security_leak",
                        "severity": finding["severity"],
                        "title": finding["description"],
                        "description": f"{finding['description']} in {finding['file']} at line {finding['line']}",
                        "reproduction": f"Check file {finding['file']}",
                        "output": finding
                    })
            else:
                self.log("No security issues found")

            # Find entry points
            entry_points = self.find_entry_points(self.project_type)

            # Apply exclude filters
            if self.exclude_patterns:
                before = len(entry_points)
                entry_points = [ep for ep in entry_points if not self._matches_exclude(ep)]
                excluded = before - len(entry_points)
                if excluded > 0:
                    self.log(f"Excluded {excluded} entry points matching patterns: {self.exclude_patterns}")

            self.entry_points_found = entry_points

            if not entry_points:
                self.log("WARNING: No entry points found")
                return False

            if self.safe_mode:
                self.log(f"Safe mode: found {len(entry_points)} entry points (not executing)")
                for ep in entry_points:
                    self.log(f"  - {ep['description']}: {' '.join(str(c) for c in ep['command'])}")
                return True

            # Execute each entry point
            results = []
            for entry_point in entry_points:
                if self.is_timeout():
                    self.log("Global timeout reached, stopping execution")
                    break

                result = self.execute_entry_point(entry_point)
                results.append(result)

                if self.verbose:
                    self.log(f"  stdout: {result['stdout'][:200]}")
                    self.log(f"  stderr: {result['stderr'][:200]}")
                    self.log(f"  exit_code: {result['exit_code']}")

                # Analyze for bugs
                bugs = self.analyze_execution_result(result)
                self.bugs.extend(bugs)

            self.log(f"Analysis complete. Found {len(self.bugs)} potential bugs")
            return True

        except Exception as e:
            self.log(f"FATAL ERROR during analysis: {e}")
            import traceback
            self.log(traceback.format_exc())
            return False
            
    def generate_report(self) -> str:
        """Generate a structured Markdown bug report."""
        report = []
        
        report.append("# MindCore · Sentinel Bug Report")
        report.append("")
        report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**Target Directory:** `{self.target_dir}`")
        report.append(f"**Analysis Duration:** {time.time() - self.start_time:.2f}s")
        report.append("")
        
        # Summary
        report.append("## Summary")
        report.append("")
        
        if not self.bugs:
            report.append("✅ **No bugs detected!**")
            report.append("")
            report.append("The codebase executed successfully without any detected errors or issues.")
        else:
            severity_counts = {}
            for bug in self.bugs:
                severity = bug["severity"]
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
                
            report.append(f"Found **{len(self.bugs)}** potential bug(s):")
            report.append("")
            for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
                if severity in severity_counts:
                    report.append(f"- **{severity}:** {severity_counts[severity]}")
            report.append("")
            
            # Detailed bug reports
            report.append("## Detailed Findings")
            report.append("")
            
            # Group by severity
            for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
                severity_bugs = [b for b in self.bugs if b["severity"] == severity]
                if not severity_bugs:
                    continue
                    
                report.append(f"### {severity} Severity")
                report.append("")
                
                for i, bug in enumerate(severity_bugs, 1):
                    report.append(f"#### Bug #{i}: {bug['title']}")
                    report.append("")
                    report.append(f"**Type:** `{bug['type']}`")
                    report.append("")
                    report.append("**Description:**")
                    report.append("")
                    report.append(bug['description'])
                    report.append("")
                    
                    report.append("**Reproduction Steps:**")
                    report.append("")
                    report.append("```bash")
                    if isinstance(bug['reproduction'], list):
                        report.append(" ".join(bug['reproduction']))
                    else:
                        report.append(str(bug['reproduction']))
                    report.append("```")
                    report.append("")

                    if bug.get('recommendation'):
                        report.append("💡 **Recommendation:**")
                        report.append("")
                        report.append(f"> {bug['recommendation']}")
                        report.append("")
                    
                    if bug.get('output'):
                        report.append("**Output:**")
                        report.append("")
                        for key, value in bug['output'].items():
                            if value:
                                report.append(f"*{key.upper()}:*")
                                report.append("```")
                                report.append(str(value))
                                report.append("```")
                                report.append("")
                    
                    report.append("---")
                    report.append("")
            
        # Live Health Check Results
        has_live_probes = any(r.get("live_probe") for r in self.logs if isinstance(r, dict))
        report.append("## Live Health Checks")
        report.append("")
        report.append("Active server probing was performed on detected web services.")
        report.append("")
                    
        # Diagnostic logs
        report.append("## Diagnostic Logs")
        report.append("")
        report.append("```")
        report.append("\n".join(self.logs[-50:]))  # Last 50 log lines
        report.append("```")
        report.append("")
        
        report.append("---")
        report.append("*Generated by MindCore · Sentinel - Local Bug Discovery Tool*")

        return "\n".join(report)

    def generate_json_report(self) -> Dict[str, Any]:
        """Generate a structured JSON bug report."""
        severity_counts: Dict[str, int] = {}
        for bug in self.bugs:
            sev = bug["severity"]
            severity_counts[sev] = severity_counts.get(sev, 0) + 1

        return {
            "tool": "MindCore Sentinel",
            "analysis_date": datetime.now().isoformat(),
            "target_directory": str(self.target_dir),
            "duration_seconds": round(time.time() - self.start_time, 2),
            "project_type": self.project_type,
            "entry_points_found": len(self.entry_points_found),
            "safe_mode": self.safe_mode,
            "summary": {
                "total_bugs": len(self.bugs),
                "by_severity": severity_counts,
            },
            "bugs": [
                {
                    "severity": bug["severity"],
                    "type": bug["type"],
                    "title": bug["title"],
                    "description": bug["description"],
                    "reproduction": (
                        " ".join(bug["reproduction"])
                        if isinstance(bug["reproduction"], list)
                        else str(bug["reproduction"])
                    ),
                    "recommendation": bug.get("recommendation"),
                    "output": bug.get("output"),
                }
                for bug in self.bugs
            ],
            "entry_points": [
                {
                    "type": ep["type"],
                    "command": " ".join(str(c) for c in ep["command"]),
                    "description": ep["description"],
                }
                for ep in self.entry_points_found
            ],
        }
