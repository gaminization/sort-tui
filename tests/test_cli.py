import subprocess
import sys


def run_cli(*args):
    return subprocess.run(
        [sys.executable, "-m", "sortui", *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def test_list_exits_zero():
    result = run_cli("--list")
    assert result.returncode == 0
    assert "Simple Sorts" in result.stdout


def test_version_exits_zero():
    result = run_cli("--version")
    assert result.returncode == 0
    assert "sort-tui" in result.stdout


def test_unknown_algorithm_has_helpful_message():
    result = run_cli("--algorithm", "no_such_sort")
    assert result.returncode != 0
    assert "unknown algorithm" in result.stderr.lower()
    assert "--list" in result.stderr

