"""
MindCore · Sentinel - Security Scanner
"""
import os
import re
from typing import List, Dict, Any

class SecretScanner:
    PATTERNS = {
        "AWS Access Key": r"AKIA[0-9A-Z]{16}",
        "AWS Secret Key": r"(?i)aws_secret_access_key.{0,20}=.{0,20}[a-zA-Z0-9\/+]{40}",
        "Google API Key": r"AIza[0-9A-Za-z\\-_]{35}",
        "Slack Token": r"xox[baprs]-([0-9a-zA-Z]{10,48})?",
        "Private Key": r"-----BEGIN RSA PRIVATE KEY-----",
        "Generic API Key": r"(?i)(api_key|apikey|secret|token).{0,20}['\"][a-zA-Z0-9_\-]{16,64}['\"]"
    }

    def scan_file(self, filepath: str) -> List[Dict[str, Any]]:
        findings = []
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                for name, pattern in self.PATTERNS.items():
                    matches = re.finditer(pattern, content)
                    for match in matches:
                        findings.append({
                            "type": "security_leak",
                            "severity": "CRITICAL",
                            "description": f"Found {name}",
                            "file": filepath,
                            "line": content[:match.start()].count('\n') + 1
                        })
        except Exception:
            pass
        return findings

    def scan_project(self, target_dir: str, exclude_dirs=None) -> List[Dict[str, Any]]:
        exclude_dirs = exclude_dirs or {'.git', 'node_modules', 'venv', '__pycache__'}
        all_findings = []
        
        for root, dirs, files in os.walk(target_dir):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                if file.endswith(('.py', '.js', '.ts', '.env', '.json', '.yml', '.yaml', '.xml')):
                    path = os.path.join(root, file)
                    all_findings.extend(self.scan_file(path))
                    
        return all_findings
