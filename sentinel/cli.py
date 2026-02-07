import argparse
import sys
import json
from pathlib import Path
from .runner import MindCoreSentinel
from .html_reporter import HTMLReporter

# Patterns to redact from output (prevent accidental secret leaking)
SECRET_PATTERNS = [
    'api_key', 'apikey', 'api-key', 'secret', 'token', 'password',
    'passwd', 'credential', 'private_key', 'access_key'
]


def redact_secrets(text: str) -> str:
    """Redact potential secrets from output text."""
    import re
    for pattern in SECRET_PATTERNS:
        # Match pattern=value, pattern: value, pattern "value" etc.
        text = re.sub(
            rf'({pattern}\s*[=:"\']\s*)([^\s"\']+)',
            r'\1[REDACTED]',
            text,
            flags=re.IGNORECASE
        )
    return text


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="MindCore · Sentinel - Fast bug discovery for hackathons",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Quick Start Examples:
  sentinel .                          # Scan current directory
  sentinel /path/to/project           # Scan specific project
  sentinel . --html                   # Generate HTML report
  sentinel . --format both            # Generate both MD and HTML

Advanced Examples:
  sentinel . --timeout 60 --no-execute
  sentinel ../my-app --output bugs.html --format html
  sentinel . --demo                   # Run on sample project

Tip: Use --no-execute for safe static analysis without running code
        """
    )

    parser.add_argument(
        "target",
        nargs="?",
        default=".",
        help="Target directory to analyze (default: current directory)"
    )

    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run analysis on a bundled sample project (for demos, no real project needed)"
    )

    parser.add_argument(
        "-t", "--timeout",
        type=int,
        default=120,
        help="Maximum execution time in seconds (default: 120)"
    )

    parser.add_argument(
        "-o", "--output",
        help="Output file for bug report (default: stdout)"
    )

    parser.add_argument(
        "-f", "--format",
        choices=["markdown", "json", "html", "both"],
        default="markdown",
        help="Output format: markdown, json, html, or both (md + html) (default: markdown)"
    )

    parser.add_argument(
        "-e", "--exclude",
        action="append",
        default=[],
        help="Glob patterns to exclude from analysis (can be repeated)"
    )

    parser.add_argument(
        "-y", "--yes",
        action="store_true",
        help="Skip the safety warning prompt"
    )

    parser.add_argument(
        "--no-execute",
        "--safe-mode",
        dest="safe_mode",
        action="store_true",
        help="Analyze without executing code (safe mode for untrusted repos)"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed execution output"
    )

    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Suppress all stderr logging, only output the report"
    )

    parser.add_argument(
        "--per-entry-timeout",
        type=int,
        default=10,
        help="Timeout per entry point in seconds (default: 10)"
    )

    parser.add_argument(
        "--ports",
        default="3000,5000,8000,8080",
        help="Comma-separated ports to probe for web servers (default: 3000,5000,8000,8080)"
    )

    parser.add_argument(
        "--smart", 
        action="store_true",
        help="Enable AI-powered bug analysis and fix suggestions"
    )

    args = parser.parse_args()

    # Demo mode: use bundled sample project
    if args.demo:
        demo_dir = Path(__file__).resolve().parent.parent / "examples" / "sample-project"
        if not demo_dir.exists():
            print(f"ERROR: Demo sample project not found at: {demo_dir}", file=sys.stderr)
            return 1
        args.target = str(demo_dir)
        args.yes = True  # Skip safety warning for demo
        if not args.quiet:
            print("DEMO MODE: Analyzing bundled sample project with intentional bugs.\n",
                  file=sys.stderr)

    # Validate target directory
    target = Path(args.target).resolve()
    if not target.exists():
        print(f"ERROR: Target directory does not exist: {target}", file=sys.stderr)
        return 1

    if not target.is_dir():
        print(f"ERROR: Target is not a directory: {target}", file=sys.stderr)
        return 1
    
    if not args.quiet:
        print(f"\n🛡️  MindCore · Sentinel - Analyzing {target}\n", file=sys.stderr)

    # Safety warning (unless --yes or --safe-mode)
    if not args.yes and not args.safe_mode and not args.quiet:
        print(
            "WARNING: This tool executes code in your project directory.\n"
            "Only run on trusted codebases. Use --safe-mode to analyze without executing.\n"
            "Use --yes to skip this warning.\n",
            file=sys.stderr
        )
        try:
            response = input("Continue? [y/N] ")
            if response.lower() not in ('y', 'yes'):
                print("Aborted.", file=sys.stderr)
                return 0
        except (EOFError, KeyboardInterrupt):
            # Non-interactive environment (CI), proceed
            pass

    # Parse ports
    try:
        ports = [int(p.strip()) for p in args.ports.split(",")]
    except ValueError:
        print(f"ERROR: Invalid ports format: {args.ports}", file=sys.stderr)
        return 1

    # Run analysis
    sentinel = MindCoreSentinel(
        str(target),
        timeout=args.timeout,
        exclude_patterns=args.exclude,
        safe_mode=args.safe_mode,
        verbose=args.verbose,
        quiet=args.quiet,
        per_entry_timeout=args.per_entry_timeout,
        ports=ports,
    )
    success = sentinel.run_analysis()

    # AI Analysis
    if args.smart and sentinel.bugs:
        from .ai_analyst import AIAnalyst
        analyst = AIAnalyst()
        analyst.analyze_bugs(sentinel.bugs)

    # Generate reports based on format
    if args.format == "json":
        report = sentinel.generate_json_report()
        report_text = json.dumps(report, indent=2)
        report_extension = ".json"
    elif args.format == "html":
        report_text = sentinel.generate_html_report()
        report_extension = ".html"
    elif args.format == "both":
        # Generate both markdown and HTML
        md_report = sentinel.generate_report()
        html_report = sentinel.generate_html_report()
        
        # Save markdown
        report_text = md_report
        report_extension = ".md"
        
        # Also save HTML version
        if args.output:
            html_output_path = Path(args.output).with_suffix('.html')
            html_output_path.write_text(html_report, encoding='utf-8')
            if not args.quiet:
                print(f"HTML report written to: {html_output_path}", file=sys.stderr)
        
        # Save to global output
        try:
            global_output_dir = Path("..").resolve() / "output"
            global_output_dir.mkdir(exist_ok=True)
            html_global_path = global_output_dir / "sentinel_report.html"
            html_global_path.write_text(html_report, encoding='utf-8')
            if not args.quiet:
                print(f"HTML report saved to: {html_global_path}", file=sys.stderr)
        except Exception as e:
            if not args.quiet:
                print(f"Warning: Could not save HTML to global output: {e}", file=sys.stderr)
    else:
        # Default markdown format
        report_text = sentinel.generate_report()
        report_extension = ".md"

    # Redact secrets from output
    report_text = redact_secrets(report_text)

    # Output report to ../output/sentinel_report (as requested)
    try:
        global_output_dir = Path("..").resolve() / "output"
        global_output_dir.mkdir(exist_ok=True)
        global_report_path = global_output_dir / f"sentinel_report{report_extension}"
        global_report_path.write_text(report_text, encoding='utf-8')
        if not args.quiet:
            print(f"Report saved to global output: {global_report_path}", file=sys.stderr)
    except Exception as e:
        if not args.quiet:
            print(f"Warning: Could not save to global output: {e}", file=sys.stderr)

    # Output report
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(report_text, encoding='utf-8')
        if not args.quiet:
            print(f"Report written to: {output_path}", file=sys.stderr)
    else:
        print(report_text)

    # Exit code based on success
    if not success:
        if not args.quiet:
            print("\nANALYSIS FAILED - See diagnostic logs above", file=sys.stderr)
        return 1

    return 0
