"""
HTML report generator for HackSentinel
"""

from datetime import datetime
from typing import List, Dict, Any


class HTMLReporter:
    """Generates beautiful HTML reports for bug findings and security issues."""
    
    def __init__(self, project_name: str):
        self.project_name = project_name
        self.generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def generate_report(self, bugs: List[Dict[str, Any]], 
                       logs: List[str], 
                       project_type: str,
                       execution_time: float) -> str:
        """Generate a complete HTML report."""
        
        # Categorize bugs by severity
        critical_bugs = [b for b in bugs if b.get('severity') == 'CRITICAL']
        high_bugs = [b for b in bugs if b.get('severity') == 'HIGH']
        medium_bugs = [b for b in bugs if b.get('severity') == 'MEDIUM']
        low_bugs = [b for b in bugs if b.get('severity') == 'LOW']
        
        # Categorize by type
        security_issues = [b for b in bugs if 'security' in b.get('type', '').lower()]
        runtime_errors = [b for b in bugs if 'error' in b.get('type', '').lower() or 'runtime' in b.get('type', '').lower()]
        syntax_issues = [b for b in bugs if 'syntax' in b.get('type', '').lower()]
        
        stats = {
            'total_bugs': len(bugs),
            'critical': len(critical_bugs),
            'high': len(high_bugs),
            'medium': len(medium_bugs),
            'low': len(low_bugs),
            'security': len(security_issues),
            'runtime': len(runtime_errors),
            'syntax': len(syntax_issues)
        }
        
        return self._render_html(bugs, logs, project_type, execution_time, stats)
    
    def _render_html(self, bugs, logs, project_type, execution_time, stats):
        """Render the HTML report."""
        
        bugs_html = self._render_bugs_section(bugs)
        vulnerabilities_html = self._render_vulnerabilities_section(bugs)
        logs_html = self._render_logs_section(logs)
        stats_html = self._render_stats_section(stats)
        
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sentinel Report - {self.project_name}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e1e2e 0%, #2a2a3e 100%);
            color: #e0e0e0;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }}
        
        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 3rem 2rem;
            border-radius: 16px;
            margin-bottom: 2rem;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }}
        
        header h1 {{
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        }}
        
        header p {{
            opacity: 0.9;
            font-size: 1.1rem;
        }}
        
        .meta-info {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }}
        
        .meta-card {{
            background: rgba(255, 255, 255, 0.05);
            padding: 1.5rem;
            border-radius: 12px;
            border-left: 4px solid #667eea;
        }}
        
        .meta-card .label {{
            color: #888;
            font-size: 0.9rem;
            margin-bottom: 0.5rem;
        }}
        
        .meta-card .value {{
            font-size: 1.3rem;
            font-weight: bold;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-bottom: 3rem;
        }}
        
        .stat-card {{
            background: rgba(255, 255, 255, 0.05);
            padding: 2rem;
            border-radius: 12px;
            text-align: center;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 12px 24px rgba(0, 0, 0, 0.4);
        }}
        
        .stat-card .number {{
            font-size: 3rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }}
        
        .stat-card .label {{
            color: #888;
            font-size: 1rem;
        }}
        
        .stat-card.critical .number {{ color: #ff4757; }}
        .stat-card.high .number {{ color: #ffa502; }}
        .stat-card.medium .number {{ color: #ffdd57; }}
        .stat-card.low .number {{ color: #48c774; }}
        .stat-card.security .number {{ color: #e74c3c; }}
        
        .section {{
            background: rgba(255, 255, 255, 0.03);
            padding: 2rem;
            border-radius: 12px;
            margin-bottom: 2rem;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
        
        .section h2 {{
            font-size: 1.8rem;
            margin-bottom: 1.5rem;
            border-bottom: 2px solid #667eea;
            padding-bottom: 0.5rem;
        }}
        
        .bug-item {{
            background: rgba(0, 0, 0, 0.3);
            padding: 1.5rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            border-left: 4px solid;
        }}
        
        .bug-item.critical {{ border-left-color: #ff4757; }}
        .bug-item.high {{ border-left-color: #ffa502; }}
        .bug-item.medium {{ border-left-color: #ffdd57; }}
        .bug-item.low {{ border-left-color: #48c774; }}
        
        .bug-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }}
        
        .bug-title {{
            font-size: 1.2rem;
            font-weight: bold;
        }}
        
        .severity-badge {{
            padding: 0.3rem 0.8rem;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: bold;
            text-transform: uppercase;
        }}
        
        .severity-badge.critical {{ background: #ff4757; color: white; }}
        .severity-badge.high {{ background: #ffa502; color: white; }}
        .severity-badge.medium {{ background: #ffdd57; color: #1e1e2e; }}
        .severity-badge.low {{ background: #48c774; color: white; }}
        
        .bug-description {{
            color: #ccc;
            margin-bottom: 0.8rem;
        }}
        
        .bug-location {{
            font-family: 'Courier New', monospace;
            background: rgba(0, 0, 0, 0.4);
            padding: 0.5rem;
            border-radius: 4px;
            font-size: 0.9rem;
            color: #61dafb;
        }}
        
        .no-bugs {{
            text-align: center;
            padding: 3rem;
            color: #48c774;
            font-size: 1.3rem;
        }}
        
        .no-bugs::before {{
            content: "✓";
            display: block;
            font-size: 4rem;
            margin-bottom: 1rem;
        }}
        
        .log-entry {{
            font-family: 'Courier New', monospace;
            font-size: 0.85rem;
            padding: 0.5rem;
            background: rgba(0, 0, 0, 0.3);
            border-left: 2px solid #667eea;
            margin-bottom: 0.5rem;
        }}
        
        .log-entry.error {{
            border-left-color: #ff4757;
            background: rgba(255, 71, 87, 0.1);
        }}
        
        .chart-container {{
            max-width: 600px;
            margin: 2rem auto;
            background: rgba(255, 255, 255, 0.05);
            padding: 2rem;
            border-radius: 12px;
        }}
        
        footer {{
            text-align: center;
            padding: 2rem;
            color: #666;
            font-size: 0.9rem;
        }}
        
        @media (max-width: 768px) {{
            .stats-grid {{
                grid-template-columns: 1fr;
            }}
        }}
        
        .ai-insight {{
            background: rgba(100, 100, 255, 0.1);
            border-left: 4px solid #667eea;
            padding: 1rem;
            margin-top: 1rem;
            border-radius: 6px;
            position: relative;
        }}
        
        .ai-header {{
            font-weight: bold;
            color: #a3b8ff;
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        
        .ai-content {{
            font-size: 0.95rem;
            line-height: 1.5;
            color: #e0e0e0;
            white-space: pre-wrap;
        }}
        
        .ai-fix {{
            margin-top: 0.8rem;
            padding-top: 0.8rem;
            border-top: 1px solid rgba(255,255,255,0.1);
            font-weight: bold;
            color: #48c774;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🛡️ MindCore · Sentinel Report</h1>
            <p>Security & Bug Analysis for {self.project_name}</p>
        </header>
        
        <div class="meta-info">
            <div class="meta-card">
                <div class="label">Generated At</div>
                <div class="value">{self.generated_at}</div>
            </div>
            <div class="meta-card">
                <div class="label">Project Type</div>
                <div class="value">{project_type.upper()}</div>
            </div>
            <div class="meta-card">
                <div class="label">Execution Time</div>
                <div class="value">{execution_time:.2f}s</div>
            </div>
        </div>
        
        {stats_html}
        
        {bugs_html}
        
        {vulnerabilities_html}
        
        {logs_html}
        
        <footer>
            Generated by MindCore · Sentinel | Deterministic Bug Discovery Tool
        </footer>
    </div>
    
    <script>
        // Render severity distribution chart
        const ctx = document.getElementById('severityChart');
        if (ctx) {{
            new Chart(ctx, {{
                type: 'doughnut',
                data: {{
                    labels: ['Critical', 'High', 'Medium', 'Low'],
                    datasets: [{{
                        data: [{stats['critical']}, {stats['high']}, {stats['medium']}, {stats['low']}],
                        backgroundColor: ['#ff4757', '#ffa502', '#ffdd57', '#48c774'],
                        borderWidth: 3,
                        borderColor: '#1e1e2e'
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {{
                        legend: {{
                            position: 'bottom',
                            labels: {{
                                color: '#e0e0e0',
                                font: {{
                                    size: 14
                                }},
                                padding: 15
                            }}
                        }},
                        title: {{
                            display: true,
                            text: 'Bug Severity Distribution',
                            color: '#e0e0e0',
                            font: {{
                                size: 18
                            }}
                        }}
                    }}
                }}
            }});
        }}
    </script>
</body>
</html>
"""
    
    def _render_stats_section(self, stats):
        """Render statistics section with cards."""
        return f"""
        <div class="stats-grid">
            <div class="stat-card critical">
                <div class="number">{stats['critical']}</div>
                <div class="label">Critical Issues</div>
            </div>
            <div class="stat-card high">
                <div class="number">{stats['high']}</div>
                <div class="label">High Priority</div>
            </div>
            <div class="stat-card medium">
                <div class="number">{stats['medium']}</div>
                <div class="label">Medium Priority</div>
            </div>
            <div class="stat-card low">
                <div class="number">{stats['low']}</div>
                <div class="label">Low Priority</div>
            </div>
            <div class="stat-card security">
                <div class="number">{stats['security']}</div>
                <div class="label">Security Issues</div>
            </div>
        </div>
        
        <div class="chart-container">
            <canvas id="severityChart"></canvas>
        </div>
"""
    
    def _render_bugs_section(self, bugs):
        """Render bugs section."""
        if not bugs:
            return """
        <section class="section">
            <h2>Bug Report</h2>
            <div class="no-bugs">
                No bugs detected! Your code looks clean.
            </div>
        </section>
"""
        
        bugs_html = ""
        for bug in bugs:
            severity = bug.get('severity', 'MEDIUM').lower()
            description = bug.get('description', 'No description provided')
            file_path = bug.get('file', 'Unknown file')
            line = bug.get('line', '?')
            bug_type = bug.get('type', 'bug')
            
            ai_section = ""
            if bug.get('ai_explanation'):
                ai_section = f"""
                <div class="ai-insight">
                    <div class="ai-header">🤖 AI Analysis</div>
                    <div class="ai-content">{self._escape_html(bug['ai_explanation'])}</div>
                    {f'<div class="ai-fix"><strong>Suggested Fix:</strong> {self._escape_html(bug.get("ai_fix", ""))}</div>' if bug.get('ai_fix') else ''}
                </div>
                """
            
            bugs_html += f"""
            <div class="bug-item {severity}">
                <div class="bug-header">
                    <div class="bug-title">{bug_type.replace('_', ' ').title()}</div>
                    <span class="severity-badge {severity}">{severity}</span>
                </div>
                <div class="bug-description">{description}</div>
                <div class="bug-location">📍 {file_path}:{line}</div>
                {ai_section}
            </div>
"""
        
        return f"""
        <section class="section">
            <h2>Detected Issues ({len(bugs)})</h2>
            {bugs_html}
        </section>
"""
    
    def _render_vulnerabilities_section(self, bugs):
        """Render security vulnerabilities section."""
        vulnerabilities = [b for b in bugs if 'security' in b.get('type', '').lower()]
        
        if not vulnerabilities:
            return """
        <section class="section">
            <h2>Security Vulnerabilities</h2>
            <div class="no-bugs">
                No security vulnerabilities detected.
            </div>
        </section>
"""
        
        vuln_html = ""
        for vuln in vulnerabilities:
            severity = vuln.get('severity', 'MEDIUM').lower()
            description = vuln.get('description', 'Security issue found')
            file_path = vuln.get('file', 'Unknown file')
            line = vuln.get('line', '?')
            
            vuln_html += f"""
            <div class="bug-item {severity}">
                <div class="bug-header">
                    <div class="bug-title">🔒 Security Vulnerability</div>
                    <span class="severity-badge {severity}">{severity}</span>
                </div>
                <div class="bug-description">{description}</div>
                <div class="bug-location">📍 {file_path}:{line}</div>
            </div>
"""
        
        return f"""
        <section class="section">
            <h2>Security Vulnerabilities ({len(vulnerabilities)})</h2>
            {vuln_html}
        </section>
"""
    
    def _render_logs_section(self, logs):
        """Render execution logs section."""
        if not logs:
            return ""
        
        logs_html = ""
        for log in logs[-50:]:  # Show last 50 logs
            css_class = "log-entry"
            if any(keyword in log.lower() for keyword in ['error', 'failed', 'exception']):
                css_class += " error"
            
            logs_html += f'<div class="{css_class}">{self._escape_html(log)}</div>\n'
        
        return f"""
        <section class="section">
            <h2>Execution Log</h2>
            <details>
                <summary style="cursor: pointer; padding: 1rem; background: rgba(0,0,0,0.3); border-radius: 8px;">
                    View detailed execution log ({len(logs)} entries)
                </summary>
                <div style="margin-top: 1rem; max-height: 400px; overflow-y: auto;">
                    {logs_html}
                </div>
            </details>
        </section>
"""
    
    def _escape_html(self, text):
        """Escape HTML special characters."""
        return (str(text)
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#39;'))
