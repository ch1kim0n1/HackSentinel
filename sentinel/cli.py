import argparse
import sys
import json
from pathlib import Path
from .runner import MindCoreSentinel

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
        description="MindCore · Sentinel - Deterministic bug discovery tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /path/to/project
  %(prog)s . --timeout 60
  %(prog)s ../my-app --output bug-report.md
  %(prog)s . --format json --exclude "test/*" --exclude "scripts/*"
  %(prog)s . --safe-mode
  %(prog)s --demo                 # Run on bundled sample project
  %(prog)s --demo --format json   # Demo with JSON output

Tip: On Windows, you can also run: python -m sentinel <target>
        """
    )

    parser.add_argument(
        "target",
        nargs="?",
        default=None,
        help="Target directory to analyze"
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
        choices=["markdown", "json"],
        default="markdown",
        help="Output format (default: markdown)"
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
        "--safe-mode",
        action="store_true",
        help="Analyze without executing code (check file existence and syntax only)"
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

    # Validate target
    if args.target is None:
        parser.print_help()
        return 0

    # Validate target directory
    target = Path(args.target).resolve()
    if not target.exists():
        print(f"ERROR: Target directory does not exist: {target}", file=sys.stderr)
        return 1

    if not target.is_dir():
        print(f"ERROR: Target is not a directory: {target}", file=sys.stderr)
        return 1

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

    # Generate report
    if args.format == "json":
        report = sentinel.generate_json_report()
        report_text = json.dumps(report, indent=2)
    else:
        report_text = sentinel.generate_report()

    # Redact secrets from output
    report_text = redact_secrets(report_text)

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
