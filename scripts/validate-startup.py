#!/usr/bin/env python3

import sys
import os
from pathlib import Path

def print_pass(msg: str) -> None:
    print(f"[PASS] {msg}")

def print_fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    sys.exit(1)

def main() -> None:
    # 1. Python version >= 3.10
    if sys.version_info >= (3, 10):
        print_pass("Python version >= 3.10")
    else:
        print_fail(f"Python version too old: {sys.version}")

    # 2. Required stdlib modules
    required_modules = ["curses", "json", "math", "time", "dataclasses", "heapq", "collections", "random", "importlib"]
    for mod in required_modules:
        try:
            __import__(mod)
        except ImportError:
            print_fail(f"Required stdlib module '{mod}' not found.")
    print_pass("Required stdlib modules are importable")

    # 3. sortui importable
    try:
        import sortui
        print_pass("Module 'sortui' is importable")
    except ImportError as e:
        print_fail(f"Failed to import 'sortui': {e}")

    # 4. Algorithm count >= 100
    try:
        from sortui.algorithms import ALGORITHMS
        if len(ALGORITHMS) >= 100:
            print_pass(f"Algorithm catalog size is {len(ALGORITHMS)} (>= 100)")
        else:
            print_fail(f"Algorithm catalog size is {len(ALGORITHMS)} (expected >= 100)")
    except Exception as e:
        print_fail(f"Failed to check algorithm catalog size: {e}")

    # 5. Config dir writable
    try:
        config_dir = Path.home() / ".config" / "sortui"
        config_dir.mkdir(parents=True, exist_ok=True)
        test_file = config_dir / ".write_test"
        test_file.touch()
        test_file.unlink()
        print_pass(f"Config directory {config_dir} is writable")
    except Exception as e:
        print_fail(f"Config directory is not writable: {e}")

    print("\nAll startup validation checks passed.")

if __name__ == "__main__":
    main()
