"""Allow running as: python -m sentinel"""
from .cli import main
import sys

sys.exit(main() or 0)
