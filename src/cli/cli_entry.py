#!/usr/bin/env python3
"""
CLI Entry Point for AlgoMath

This module provides a command-line interface for the AlgoMath framework,
allowing Node.js to call Python functions via subprocess.
"""

import sys
import json
import argparse
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.cli.commands import (
    extract_command,
    generate_command,
    run_command,
    verify_command,
    status_command,
    list_command,
    help_command
)


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(description='AlgoMath CLI')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Extract command
    extract_parser = subparsers.add_parser('extract', help='Extract algorithm from text or file')
    extract_parser.add_argument('text', nargs='?', help='Mathematical text (optional if --file provided)')
    extract_parser.add_argument('--file', '-f', help='Path to PDF or text file', default=None)
    extract_parser.add_argument('--name', '-n', help='Algorithm name', default=None)

    # Generate command
    generate_parser = subparsers.add_parser('generate', help='Generate code from steps')

    # Run command
    run_parser = subparsers.add_parser('run', help='Execute generated code')
    run_parser.add_argument('--skip', action='store_true', help='Skip execution')

    # Verify command
    verify_parser = subparsers.add_parser('verify', help='Verify execution results')
    verify_parser.add_argument('--step', type=int, help='Explain specific step')
    verify_parser.add_argument('--detailed', action='store_true', help='Show detailed explanation')
    verify_parser.add_argument('--diagnostic', action='store_true', help='Run diagnostic mode')

    # Status command
    status_parser = subparsers.add_parser('status', help='Show current state')

    # List command
    list_parser = subparsers.add_parser('list', help='List saved algorithms')

    # Help command
    help_parser = subparsers.add_parser('help', help='Show help')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        # Route to appropriate command
        if args.command == 'extract':
            result = extract_command(text=args.text, file=args.file, name=args.name)
        elif args.command == 'generate':
            result = generate_command()
        elif args.command == 'run':
            result = run_command(skip=args.skip)
        elif args.command == 'verify':
            result = verify_command(
                step=args.step,
                detailed=args.detailed,
                diagnostic=args.diagnostic
            )
        elif args.command == 'status':
            result = status_command()
        elif args.command == 'list':
            result = list_command()
        elif args.command == 'help':
            result = help_command()
        else:
            print(json.dumps({
                'status': 'error',
                'message': f'Unknown command: {args.command}'
            }))
            sys.exit(1)

        # Output result as JSON for Node.js to parse
        print(json.dumps(result))

    except Exception as e:
        print(json.dumps({
            'status': 'error',
            'message': str(e)
        }))
        sys.exit(1)


if __name__ == '__main__':
    main()
