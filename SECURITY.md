# Security Policy

## Supported Versions

Currently, `sort-tui` is in early alpha. We only provide security updates for the latest released version. 

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

## Reporting a Vulnerability

As an educational CLI tool, `sort-tui` operates entirely within the user's local terminal sandbox and processes locally generated arrays. It does not accept network connections, parse remote unsanitized data, or run elevated privileges. 

However, if you discover a vulnerability (e.g., arbitrary code execution via crafted algorithmic plugins or file-path traversal in exports), please report it responsibly.

**Do not open a public issue.**

Instead, please email the core maintainers at `sortui@example.com` with the subject `[SECURITY VULNERABILITY]`. Include detailed steps to reproduce the issue. We aim to acknowledge all reports within 48 hours and will coordinate a patch and CVE release if applicable.
